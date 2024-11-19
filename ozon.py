from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup, NavigableString
import re
import asyncio

import os

def init_webdriver():
    options = Options()

    # run browser without opening a new window
    options.add_argument("--headless")
        
    # fixes a gpu error without fully disabling gpu
    options.add_argument("--disable-gpu-compositing")
    # suppresses SSL errors 
    options.add_argument("--ignore-certificate-errors")
    # disable console output
    options.add_argument("--log-level=OFF")
    
    # prevents browser from playing audio
    options.add_argument("--mute-audio")
    prefs = {
        # shares location with every website
        "profile.default_content_setting_values.geolocation": 1
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    stealth(driver,
            platform="Win32",
            vendor="Google Inc.",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine")
    return driver

driver = init_webdriver()

def set_location(loc: tuple[int, int]):
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": loc[0],
        "longitude": loc[1],
        "accuracy": 0  # Higher accuracy (in meters)
    })

def enable_cdp_blocking():
    # Enable Chrome DevTools Protocol (CDP) for blocking resources
    driver.execute_cdp_cmd("Network.enable", {})
    
    # Set request interception patterns for types you want to block
    driver.execute_cdp_cmd(
        "Network.setBlockedURLs", {
            "urls": [
                "*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg", "*.webp",  # Images
                "*.css",  # Stylesheets
                "*.mp4", "*.webm", "*.avi", "*.mov",  # Media
                "*.ttf", "*.woff", "*.woff2", "*.otf"  # Fonts
            ]
        }
    )

async def load_html(link: str):
    driver.get(link)
    
    await wait_antibot()

    raw_html = get_source()
    return raw_html

async def wait_antibot():
    while "Antibot" in driver.title:
        await asyncio.sleep(0.1)

def get_source():
    return BeautifulSoup(driver.page_source, "html.parser")

def clean_name(name: str):
    return re.sub(r"\s+", " ", name).strip()

def parse_price(price_span):
    return int("".join([c if c.isdigit() else "" for c in price_span.text]))

def price_from_spans(priceSpans):
    count = len(priceSpans)
    
    price_span = None
    if count == 3:
        price_span = priceSpans[1]
    elif count == 2:
        price_span = priceSpans[0]
    return parse_price(price_span) if price_span else None

def get_name(html: BeautifulSoup):
    name_header = html.find("h1")
    if not name_header:
        return None

    return clean_name(name_header.text)

def get_price(html: BeautifulSoup):
    price_div = html.find('div', {"data-widget": "webPrice"})
    price_spans = price_div.find_all('span', string=lambda text: text and '₽' in text)

    return price_from_spans(price_spans)

async def wait_location():
    '''
    Finds a button, responsible for user's location
    returns btn if found, returns None, if user
    '''
    while True:
        try:
            return driver.find_element(By.XPATH, "//button[contains(., 'Сменить')]")
        except: pass
        try:
            driver.find_element(By.XPATH, "//button[contains(., 'Не сейчас')]")
            return None
        except: pass
        await asyncio.sleep(0.1)

async def wait_location_change():
    while True:
        try:
            return driver.find_element(By.XPATH, "//h1[contains(., 'доставк')]")
        except: pass
        await asyncio.sleep(0.1)

async def load_info(id: int, location: tuple[float, float] | None = None):
    if location:
        set_location(location)
    
    # driver.delete_all_cookies()
    enable_cdp_blocking()

    html = await load_html(f"https://ozon.ru/product/{id}")

    name = get_name(html)
    if not name:
        return None

    if location:
        change_btn = await wait_location()
        if change_btn:
            change_btn.click()

            await wait_location_change()

    price = get_price(html)
    if not price:
        return None

    return {"name": name, "price": price * 100}

# async def main():
    

#     article = 27524240

#     enable_cdp_blocking()
#     # preload for the future uses
#     await load_html("https://www.ozon.ru/")

#     # print(await load_info(article, (56.85423623447262, 53.242487506387455)))
#     print(await load_info(article))
#     await asyncio.sleep(120)

# asyncio.run(main())
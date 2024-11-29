from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup, NavigableString
import re
import asyncio

from time import time

from config import SLEEP_DUR, MAX_LOAD_TIME

def init_webdriver():
    """
    Creates a new driver for scraping
    """
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

def set_location(loc: tuple[float, float]):
    """
    Sets `driver`'s location to `loc`
    """
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": loc[0],
        "longitude": loc[1],
        "accuracy": 0  # Higher accuracy (in meters)
    })

def enable_cdp_blocking():
    """
    Starts blocking all the resources to speed up loading
    """
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
    """
    Returns source code of the page after it bypassed bot detection
    """
    driver.get(link)
    
    await wait_antibot()

    raw_html = get_source()
    return raw_html

async def wait_antibot():
    """
    Sleeps until it has successfully bypassed bot detection
    """
    while "Antibot" in driver.title:
        await asyncio.sleep(0.1)

def get_source():
    """
    returns the source code of the current page
    """
    return BeautifulSoup(driver.page_source, "html.parser")

def clean_name(name: str):
    """
    Removes all the spaces and new line characters to clean up the name
    """
    return re.sub(r"\s+", " ", name).strip()

def parse_price(price_span: NavigableString):
    """
    Parses given span into a number
    """
    return int("".join([c if c.isdigit() else "" for c in price_span.text]))

def price_from_spans(priceSpans):
    """
    Finds the right span from `priceSpans` and returns it's parsed form
    """
    count = len(priceSpans)
    
    price_span = None
    if count == 3:
        price_span = priceSpans[1]
    elif count == 2:
        price_span = priceSpans[0]
    return parse_price(price_span) if price_span else None

def get_name(html: BeautifulSoup):
    """
    Finds the name of the product on a page
    """
    name_header = html.find("h1")
    if not name_header:
        return None

    return clean_name(name_header.text)

def get_price(html: BeautifulSoup):
    """
    Returns the price of a product from html page
    """
    price_div = html.find('div', {"data-widget": "webPrice"})
    if not price_div:
        return None
    price_spans = price_div.find_all('span', string=lambda text: text and '₽' in text)

    if not len(price_spans):
        return None

    return price_from_spans(price_spans)

async def wait_location():
    """
    Waits for the button, responsible for user's location, to appear
    \nreturns btn if found, returns `None`, if user's location doesn't need to be changed
    """
    while True:
        try:
            return driver.find_element(By.XPATH, "//button[contains(., 'Сменить')]")
        except NoSuchElementException: pass
        try:
            driver.find_element(By.XPATH, "//button[contains(., 'Не сейчас')]")
            return None
        except NoSuchElementException: pass
        await asyncio.sleep(SLEEP_DUR)

async def wait_location_change():
    """
    Waits for the price to change according to the new location
    """
    while True:
        try:
            return driver.find_element(By.XPATH, "//h1[contains(., 'доставк')]")
        except NoSuchElementException: pass
        await asyncio.sleep(SLEEP_DUR)

async def load_info_unsafe(id: int, location: tuple[float, float] | None):
    if location:
        set_location(location)
    
    driver.delete_all_cookies()
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

    return {"name": name, "price": price}

async def load_info(id: int, location: tuple[float, float] | None = None):
    """
    returns price and name of the product from its article
    `id` - article of the product to be searched
    `location` - this location will be set on the website if provided
    `max_dur` - the limit of time for this function's execution
    """
    start_time = time()
    
    task = asyncio.create_task(load_info_unsafe(id, location))

    while not task.done():
        if time() - start_time > MAX_LOAD_TIME:
            task.cancel()
            return None
        await asyncio.sleep(SLEEP_DUR)
    return task.result()

driver = init_webdriver()
# Preload browser for more accurate results
asyncio.run(load_html("https://ozon.ru/"))

async def main():
    article = 1583876229

    enable_cdp_blocking()
    print(await load_info(article))

if __name__ == "__main__":
    asyncio.run(main())
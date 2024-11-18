from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup, NavigableString
import re
import asyncio

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
        # prevents browser from loading images
        "profile.managed_default_content_settings.images": 2,
        # shares location with every website
        "profile.default_content_setting_values.geolocation": 1
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": 56.91439917863945,
        "longitude": 53.316618733502466,
        "accuracy": 0  # Higher accuracy (in meters)
    })

    stealth(driver,
            platform="Win32",
            vendor="Google Inc.",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine")
    return driver

driver = init_webdriver()

async def load_html(id: int):
    driver.get(f"https://ozon.ru/product/{id}")
    
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

async def load_info(id: int):
    html = await load_html(id)

    name = get_name(html)
    if not name:
        return None
    price = get_price(html)
    if not price:
        return None

    return {"name": name, "price": price * 100}
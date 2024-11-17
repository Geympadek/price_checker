import requests

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup, NavigableString
import re
import asyncio

def load_json_wb(id: int):
    url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-971647&spp=30&ab_testing=false&nm={id}"
    data = requests.get(url).json()
    return data["data"]["products"]

def load_price_wb(id: int):
    try:
        products = load_json_wb(id)
        
        price = products[0]["sizes"][0]["price"]["total"]
        return int(price)
    except:
        return None
    
def load_name_wb(id: int):
    products = load_json_wb(id)

    if len(products) == 0:
        return None
        
    name = products[0]["name"]
    return name

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
    # prevents browser from loading images
    prefs = {
        "profile.managed_default_content_settings.images": 2
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

async def load_html_ozon(id: int):
    driver.get(f"https://ozon.ru/product/{id}")
    
    while "Antibot" in driver.title:
        await asyncio.sleep(0.1)

    raw_html = BeautifulSoup(driver.page_source, "html.parser")
    return raw_html

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

async def load_price_ozon(id: int):
    html = await load_html_ozon(id)

    price_div = html.find('div', {"data-widget": "webPrice"})
    price_spans = price_div.find_all('span', string=lambda text: text and '₽' in text)

    price = price_from_spans(price_spans)

    return price * 100 if price else None

async def load_name_ozon(id: int):
    html = await load_html_ozon(id)

    name_header = html.find("h1")
    if not name_header:
        return None

    return clean_name(name_header.text)

async def load_price(id: int, platform: str):
    '''
    Get product's price
    '''
    if platform == "wildberries":
        return load_price_wb(id)
    if platform == "ozon":
        return await load_price_ozon(id)

async def load_name(id: int, platform: str):
    if platform == "wildberries":
        return load_name_wb(id)
    if platform == "ozon":
        return await load_name_ozon(id)
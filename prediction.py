# import tensorflow as tf
# import numpy as np

# import keras

from loader import database
from config import RNN_PRICE_PERIOD

from math import floor

import graph

def find_old_price(prices: list[dict]):
    '''
    Returns the oldest date in the list
    '''
    return min(prices, key=lambda price: int(price["date"]))

def find_new_price(prices: list[dict]):
    '''
    Returns the newest date in the list
    '''
    return max(prices, key=lambda price: int(price["date"]))

def closest_prices(prices: list[dict], point_date: int):
    '''
    Finds the closest price entries to the `point_date` and returns them
    \n`prices` - price entries from the database
    \n`point_date` - date in seconds
    \n`return` closest_older, closest_newer 
    '''
    closest_older = None
    closest_newer = None
    min_delta_older = float('inf')
    min_delta_newer = float('inf')

    for price in prices:
        date = price["date"]
        delta = abs(date - point_date)

        if date <= point_date and delta < min_delta_older:
            closest_older = price
            min_delta_older = delta
        elif date >= point_date and delta < min_delta_newer:
            closest_newer = price
            min_delta_newer = delta

    return closest_older, closest_newer

def closest_prices(prices: list[dict], point_date: int):
    for i, price in enumerate(prices):
        date = price["date"]

        if date > point_date:
            return prices[i - 1], price
            
def normalize_prices(product_id: int):
    '''
    Normalizes info about prices, creating a list with an entry every `config.RNN_PRICE_PERIOD` seconds
    '''
    prices = database.read("prices", {"product_id": product_id})

    old_price = find_old_price(prices)
    new_price = find_new_price(prices)

    inputs_len = floor((new_price["date"] - old_price["date"]) / RNN_PRICE_PERIOD)

    inputs = []
    for i in range(inputs_len):
        point_time = old_price["date"] + i * RNN_PRICE_PERIOD
        closest_older, closest_newer = closest_prices(prices, point_time)

        distance = closest_newer["date"] - closest_older["date"]
        newer_distance = closest_newer["date"] - point_time
        older_distance = distance - newer_distance

        appr_price = closest_older["price"] * (newer_distance / distance) + closest_newer["price"] * (older_distance / distance)
        inputs.append(appr_price)
    return inputs

def prices_to_dict(predicted_prices: list, start_time: int):
    '''
    Takes prices, predicted in a list and converts them to `{"date": "price":}` format
    '''
    prices = []
    for pred_price in predicted_prices:
        prices.append({"date": start_time + RNN_PRICE_PERIOD, "price": pred_price})
        start_time += RNN_PRICE_PERIOD
    return prices

graph.generate(6, "test.png", predictions=prices_to_dict(normalize_prices(6), 1731763395))
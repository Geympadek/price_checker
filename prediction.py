# import tensorflow as tf
# import numpy as np

# import keras

from loader import database
from config import RNN_PRICE_PERIOD

from math import floor

import graph

def find_old_price(prices: list[dict]):
    return min(prices, key=lambda price: int(price["date"]))

def find_new_price(prices: list[dict]):
    return max(prices, key=lambda price: int(price["date"]))

def closest_prices(prices: list[dict], point_date: int):
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

def gen_inputs(product_id: int):
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

def data_to_prices(data: list, start_time: int):
    prices = []
    for el in data:
        prices.append({"date": start_time + RNN_PRICE_PERIOD, "price": el})
        start_time += RNN_PRICE_PERIOD
    return prices

graph.generate(6, "test.png", predictions=data_to_prices(gen_inputs(6), 1731763395))
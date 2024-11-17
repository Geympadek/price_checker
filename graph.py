from matplotlib import pyplot
from datetime import datetime

from loader import database
from matplotlib import ticker

@ticker.FuncFormatter
def date_format(x, pos=None):
    date = datetime.fromtimestamp(x)
    return f"{date.day}.{date.month}"

def generate(product_id: int, path: str):
    price_entries = database.read("prices", {"product_id": product_id})
    
    if len(price_entries) < 2:
        raise ValueError("Too few prices to draw a graph.")
    
    dates = []
    prices = []
    for entry in price_entries:
        date = int(entry["date"])

        dates.append(date)
        prices.append(int(entry["price"]) / 100)

    pyplot.plot(dates, prices, marker = 'o')
    pyplot.title("Изменение цены")
    pyplot.xlabel("Дата")
    pyplot.ylabel("Цена")
    pyplot.grid(True)

    pyplot.gca().xaxis.set_major_formatter(date_format)
    pyplot.gca().xaxis.set_major_locator(ticker.MultipleLocator(3600 * 24))

    pyplot.savefig(path)
    pyplot.close()
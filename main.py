import os, time
import requests
from datetime import datetime

API_KEY = os.getenv("OKX_API_KEY")
API_SECRET = os.getenv("OKX_API_SECRET")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

ENTRY_PRICE = 2518.63
CALLBACK = 7.5
AMOUNT = 7.54
LEVERAGE = 10

def get_price():
    r = requests.get("https://www.okx.com/api/v5/market/ticker?instId=ETH-USDT-SWAP")
    return float(r.json()["data"][0]["last"])

def calcular_trailing_stop(max_price):
    return round(max_price - CALLBACK, 2)

def evaluar():
    current_price = get_price()
    max_price = max(current_price, evaluar.max_price)
    evaluar.max_price = max_price

    trailing_stop = calcular_trailing_stop(max_price)
    profit = (current_price - ENTRY_PRICE) * (AMOUNT * LEVERAGE) / ENTRY_PRICE
    profit_pct = profit / AMOUNT * 100

    print(f"[{datetime.now()}] Precio actual: {current_price} USDT")
    print(f"Trailing Stop: {trailing_stop} | Ganancia: {profit:.2f} USDT ({profit_pct:.2f}%)")
    print("-" * 40)

evaluar.max_price = ENTRY_PRICE

while True:
    evaluar()
    time.sleep(900)
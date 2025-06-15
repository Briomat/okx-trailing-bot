import os, time
import requests
from datetime import datetime
import json
import logging

API_KEY = os.getenv("OKX_API_KEY")
API_SECRET = os.getenv("OKX_API_SECRET")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

ENTRY_PRICE = 2518.63
CALLBACK = 7.5
AMOUNT = 7.54
LEVERAGE = 10
API_URL = "https://www.okx.com/api/v5/market/ticker?instId=ETH-USDT-SWAP"
LOG_PATH = "trading_bot.log"
ESTADO_PATH = "estado.json"

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

estado = {
    "max_price": ENTRY_PRICE,
    "modo": "LONG",
    "cooldown": None,
    "ultimo_trade": None,
    "drawdown_pct": 0
}

def cargar_estado():
    global estado
    if os.path.exists(ESTADO_PATH):
        with open(ESTADO_PATH, "r") as f:
            estado = json.load(f)
    else:
        guardar_estado()

def guardar_estado():
    with open(ESTADO_PATH, "w") as f:
        json.dump(estado, f, indent=4)

def get_price():
    for _ in range(3):
        try:
            r = requests.get(API_URL, timeout=10)
            r.raise_for_status()
            return float(r.json()["data"][0]["last"])
        except Exception as e:
            logging.warning(f"Error obteniendo precio: {e}")
            time.sleep(2)
    raise Exception("No se pudo obtener el precio tras 3 intentos")

def calcular_trailing_stop(max_price):
    return round(max_price - CALLBACK, 2)

def evaluar():
    try:
        precio_actual = get_price()
        max_price = max(precio_actual, estado["max_price"])
        trailing_stop = calcular_trailing_stop(max_price)
        profit = (precio_actual - ENTRY_PRICE) * (AMOUNT * LEVERAGE) / ENTRY_PRICE
        profit_pct = profit / AMOUNT * 100

        estado["max_price"] = max_price
        guardar_estado()

        resumen = {
            "precio_actual": precio_actual,
            "stop_loss_dinamico": trailing_stop,
            "ganancia_usdt": round(profit, 2),
            "ganancia_pct": round(profit_pct, 2),
            "modo": estado["modo"]
        }

        logging.info(f"[{estado['modo']}] ETH = {precio_actual} | SL = {trailing_stop} | PnL = {profit:.2f} USDT ({profit_pct:.2f}%)")
        return resumen

    except Exception as e:
        logging.error(f"Fallo en evaluación: {e}")
        return {"error": str(e)}

cargar_estado()

while True:
    resultado = evaluar()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    time.sleep(900)

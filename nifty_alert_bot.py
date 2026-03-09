import yfinance as yf
import pandas as pd
import requests
import time
from datetime import datetime
import pytz

BOT_TOKEN = "8756647675:AAGIyJSN0OZ-J_VOzJEnuclFR_u8Wu-ZYvM"
CHAT_ID = "6491715697"

# Using NIFTY ETF as proxy for Futures
SYMBOL = "NIFTYBEES.NS"

last_signal_time = None


def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)


def market_open():

    india = pytz.timezone("Asia/Kolkata")
    now = datetime.now(india)

    if now.weekday() >= 5:
        return False

    start = now.replace(hour=9, minute=15, second=0)
    end = now.replace(hour=15, minute=30, second=0)

    return start <= now <= end


def check_signal():

    global last_signal_time

    print("Checking market...")

    data = yf.download(SYMBOL, interval="5m", period="1d")

    if len(data) < 10:
        return

    data["EMA5"] = data["Close"].ewm(span=5).mean()

    prev = data.iloc[-2]
    last = data.iloc[-1]

    alert_candle = (
        prev["Open"] > prev["EMA5"]
        and prev["High"] > prev["EMA5"]
        and prev["Low"] > prev["EMA5"]
        and prev["Close"] > prev["EMA5"]
    )

    break_condition = last["Low"] < prev["Low"]

    if alert_candle and break_condition:

        signal_time = str(data.index[-1])

        if signal_time == last_signal_time:
            return

        last_signal_time = signal_time

        entry = prev["Low"]
        sl = prev["High"] + 20
        risk = sl - entry
        tp = entry - (risk * 2)

        message = f"""
🚨 NIFTY FUTURES SIGNAL

Entry : {round(entry,2)}
SL : {round(sl,2)}
TP : {round(tp,2)}

Alert Candle Low Broken
Time : {signal_time}
"""

        send_message(message)


print("🚀 NIFTY Futures Bot Started")

while True:

    if market_open():

        try:
            check_signal()
        except Exception as e:
            print("Error:", e)

        time.sleep(300)

    else:
        time.sleep(60)
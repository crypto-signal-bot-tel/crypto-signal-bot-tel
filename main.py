import time
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import pandas_ta as ta
import telegram
import os

tv = TvDatafeed(username=None, password=None, session=os.getenv("TV_SESSION"))
bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("CHAT_ID")

symbols = [
    {"symbol": "BTCUSDT", "exchange": "BINANCE"},
    {"symbol": "DOGEUSDT", "exchange": "BINANCE"}
]

def analyze(symbol, exchange):
    df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_15_minute, n_bars=150)
    if df is None or df.empty:
        return None

    df.ta.ema(length=200, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.bbands(length=20, append=True)

    signal = None
    latest = df.iloc[-1]

    conditions = [
        latest['RSI_14'] < 30,
        latest['EMA_200'] < latest['close'],
        latest['MACDh_12_26_9'] > 0,
        latest['close'] < latest['BBL_20_2.0'],
    ]

    valid_signals = sum(conditions)

    if valid_signals >= 3:
        trend = "Long"
        icon = "⭐" if valid_signals == 4 else "🚨"
        entry = round(latest['close'], 4)
        sl = round(entry * 0.98, 4)
        tp = round(entry * 1.03, 4)

        signal = f"""
💹 {trend} Signal {icon}
Symbol: {symbol}
Entry: {entry}
SL: {sl}
TP: {tp}
Timeframe: 15m
🧠 Score: {valid_signals}/4
        """.strip()
    return signal

while True:
    for sym in symbols:
        try:
            result = analyze(sym["symbol"], sym["exchange"])
            if result:
                bot.send_message(chat_id=chat_id, text=result)
        except Exception as e:
            print(f"خطا در تحلیل {sym['symbol']}: {e}")
    time.sleep(300)
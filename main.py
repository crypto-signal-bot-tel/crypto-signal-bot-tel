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

def detect_fake_breakout(df):
    if len(df) < 3:
        return False
    prev = df.iloc[-3]
    brk = df.iloc[-2]
    ret = df.iloc[-1]
    return (brk['high'] > prev['high']) and (ret['close'] < prev['close'])

def detect_compression(df):
    recent_atr = ta.atr(df['high'], df['low'], df['close'], length=14)
    return recent_atr.iloc[-1] < recent_atr.mean() * 0.7


def detect_fvg(df):
    fvg_signals = []

    for i in range(2, len(df)):
        c1 = df.iloc[i - 2]
        c2 = df.iloc[i - 1]
        c3 = df.iloc[i]

        # FVG صعودی
        if c1['high'] < c3['low']:
            if c2['low'] > c1['high'] and c2['high'] < c3['low']:
                fvg_signals.append({'index': i, 'type': 'FVG', 'level': (c1['high'] + c3['low']) / 2})

        # IFVG نزولی
        if c1['low'] > c3['high']:
            if c2['high'] < c1['low'] and c2['low'] > c3['high']:
                fvg_signals.append({'index': i, 'type': 'IFVG', 'level': (c1['low'] + c3['high']) / 2})

    return fvg_signals


def analyze(symbol, exchange):
    df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_15_minute, n_bars=200)
    if df is None or df.empty:
        return None

    df.ta.ema(length=200, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.bbands(length=20, append=True)
    df.ta.ichimoku(append=True)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'])

    
    fvg_signals = detect_fvg(df)
    recent_fvg = [f for f in fvg_signals if f["index"] >= len(df) - 5]

    if recent_fvg:
        for fvg in recent_fvg:
            if fvg["type"] == "FVG":
                conditions.append("🟢 FVG Detected")
            elif fvg["type"] == "IFVG":
                conditions.append("🔴 IFVG Detected")

    latest = df.iloc[-1]

    conditions = []

    if latest['RSI_14'] < 30:
        conditions.append("🟢 RSI Oversold")

    if latest['EMA_200'] < latest['close']:
        conditions.append("🟢 Price Above EMA200")

    if latest['MACDh_12_26_9'] > 0:
        conditions.append("🟢 MACD Bullish")

    if latest['close'] < latest['BBL_20_2.0']:
        conditions.append("🟢 Below Bollinger Band")

    if latest['ITS_9'] < latest['IKS_26']:
        conditions.append("🟢 Ichimoku Bullish Cross")

    if detect_fake_breakout(df):
        conditions.append("🟡 Fake Breakout")

    if detect_compression(df):
        conditions.append("🟡 Price Compression")

    score = len(conditions)

    if score >= 4:
        trend = "Long"
        icon = "⭐" if score >= 6 else "🚨"
        entry = round(latest['close'], 4)
        sl = round(entry * 0.985, 4)
        tp = round(entry * 1.035, 4)

        return f"""
💹 {trend} Signal {icon}
Symbol: {symbol}
Entry: {entry}
SL: {sl}
TP: {tp}
Timeframe: 15m
✅ Confirmations:
{chr(10).join(conditions)}
        """.strip()

    return None

while True:
    for sym in symbols:
        try:
            result = analyze(sym["symbol"], sym["exchange"])
            if result:
                bot.send_message(chat_id=chat_id, text=result)
        except Exception as e:
            print(f"خطا در تحلیل {sym['symbol']}: {e}")
    time.sleep(300)
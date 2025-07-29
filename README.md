# ربات تلگرام تحلیل‌گر سیگنال کریپتو

## ابزارها:
- RSI
- EMA200
- MACD
- Bollinger Bands

## جفت‌ها:
- BTCUSDT
- DOGEUSDT

## راه‌اندازی:
1. فایل `.env` بسازید و مقادیر زیر را وارد کنید:

```
TV_SESSION=کد سشن تریدینگ‌ویو شما
TELEGRAM_TOKEN=توکن ربات تلگرام
CHAT_ID=شناسه چت تلگرام
```

2. نصب کتابخانه‌ها:
```
pip install -r requirements.txt
```

3. اجرای برنامه:
```
python main.py
```

یا دیپلوی در Railway با اتصال GitHub
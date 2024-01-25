import os
import json
import pandas as pd
from alpaca_trade_api import REST, TimeFrame
from datetime import datetime, timedelta
import os
import talib

api_key = os.environ["API_KEY"]
secret_key = os.environ["SECRET_KEY"]
base_url = os.environ["API_URL"]

symbols = ["MMM"]

api = REST(key_id=api_key, secret_key=secret_key, base_url=base_url, api_version="v2")
# Setting the date range of stock prices we want to get
end_date = datetime.today() - timedelta(days=1)
start_date = end_date - timedelta(days=365 * 2)

df_barset = api.get_bars(
    symbols,
    TimeFrame.Day,
    start_date.strftime("%Y-%m-%d"),
    end_date.strftime("%Y-%m-%d"),
    adjustment="all",
).df
df_barset = df_barset.reset_index(level=0)

print(df_barset.head())

ma_10 = talib.MA(df_barset["close"], timeperiod=10, matype=0)

ma_30 = talib.MA(df_barset["close"], timeperiod=30, matype=0)

print(ma_10)

print(ma_30)

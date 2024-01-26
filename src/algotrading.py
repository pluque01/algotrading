import os
import json
import pandas as pd
from alpaca_trade_api import REST, TimeFrame
from datetime import datetime, timedelta
import os
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

# https://kernc.github.io/backtesting.py/

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

# print(df_barset)

ma_10 = talib.MA(df_barset["close"], timeperiod=10, matype=0)

ma_30 = talib.MA(df_barset["close"], timeperiod=30, matype=0)

# print(ma_10)

# print(ma_30)

matriz_estrategia = np.vstack((df_barset["close"], ma_10, ma_30))

# Eliminar las filas que contienen NaN
matriz_estrategia = matriz_estrategia[~np.isnan(matriz_estrategia).any(axis=1)]

# Nombres de las columnas
nombres_columnas = ["cierre", "ma10", "ma30"]

# Crear un dtype con nombres para las columnas
dtype = np.dtype({"names": nombres_columnas, "formats": [float, float, float]})

# Crear una nueva matriz con dtype
matriz_estrategia = np.array(matriz_estrategia, dtype=dtype)


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

df_barset = df_barset.rename(columns={'open': 'Open', 'close': 'Close', 'high': 'High', 'low': 'Low', 'volume': 'Volume'})
df_barset['timestamp'] = pd.to_datetime(df_barset['timestamp'], errors='coerce')

df_barset = df_barset.set_index('timestamp')

# print(df_barset.columns)

bt = Backtest(df_barset, SmaCross, cash=10000, commission=0.002, exclusive_orders=True)

output = bt.run()

print(output)

# print(output._strategy)

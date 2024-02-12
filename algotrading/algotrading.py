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
start_date = end_date - timedelta(days=90)

df_barset = api.get_bars(
    symbols,
    TimeFrame.Hour,
    start_date.strftime("%Y-%m-%d"),
    end_date.strftime("%Y-%m-%d"),
    adjustment="all",
).df
df_barset = df_barset.reset_index(level=0)


# Puedes crear cualquier tipo de estrategia. Documentación en: https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html#backtesting.backtesting.Strategy
class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        # Esto es para crear indicadores, podemos usar los de ta-lib tal y como viene en la documentación
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


# Para que funcione correctamente hay que renombrar las columnas y establecer el índice del
# dataFrame en la fecha.
df_barset = df_barset.rename(
    columns={
        "open": "Open",
        "close": "Close",
        "high": "High",
        "low": "Low",
        "volume": "Volume",
    }
)
df_barset["timestamp"] = pd.to_datetime(df_barset["timestamp"], errors="coerce")

df_barset = df_barset.set_index("timestamp")

# print(df_barset.columns)

bt = Backtest(df_barset, SmaCross, cash=10000, commission=0.002, exclusive_orders=True)

output = bt.optimize(
    n1=range(5, 30, 5),
    n2=range(10, 70, 5),
    maximize="Equity Final [$]",
    constraint=lambda param: param.n1 < param.n2,
)


bt.plot(filename="./frontend/output")

# print(output._strategy)


# Pruebo a iniciar sesión
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest

trading_client = TradingClient(api_key, secret_key)

# Get our account information.
account = trading_client.get_account()

print(account)

# Check if our account is restricted from trading.
if account.trading_blocked:
    print("Account is currently restricted from trading.")

# Check how much money we can use to open new positions.
print("${} is available as buying power.".format(account.buying_power))

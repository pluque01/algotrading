## TODO: Realizar tests dándole datos de uno en uno.
## TODO: Muchos imports se hacen por necesidad para los tests

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from backtesting.test import SMA
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

import os
import json
import pandas as pd
from alpaca_trade_api import REST, TimeFrame
from datetime import datetime, timedelta
import os
import talib
import numpy as np

# Devuelve true si la segunda media móvil se ha hecho más grande que la primera
def crossover(sma1, sma2):
    if len(sma1) < 2 or len(sma2) < 2:
        raise ValueError("Both arrays must have at least 2 elements.")
    next_to_last_sma1 = sma1[-2]
    last_sma1 = sma1[-1]

    next_to_last_sma2 = sma2[-2]
    last_sma2 = sma2[-1]

    return next_to_last_sma1 > next_to_last_sma2 and last_sma1 < last_sma2

class StrategyAccount():
    #account = TradingClient(api_key, secret_key)

    n1 = 10
    n2 = 20

    def __init__(self, close, symbol, trading_client):
        self.close = close
        self.sma1 = talib.SMA(close, self.n1)
        self.sma2 = talib.SMA(close, self.n2)
        self.trading_client = trading_client
    
    def init(self):
        return None

    def next(self):
        return None

    def buy_signal(self):
        if crossover(self.sma2,self.sma1):
            return True
        else:
            return False
        
    def sell_signal(self):
        if crossover(self.sma1,self.sma2):
            return True
        else:
            return False

    def order(self):
        side = None
        if self.buy_signal():
            side=OrderSide.BUY
            print("Debería comprar\n")
        elif self.sell_signal():
            side=OrderSide.SELL
            print("Debería vender\n")

        if side == None:
            print("!No hay señal ni de compra ni de venta")
        # if side != null:
        #     market_order_data = MarketOrderRequest(
        #             symbol=self.symbol,
        #             qty=0.023,
        #             side=side,
        #             time_in_force=TimeInForce.DAY,
        #             client_order_id='my_first_order',
        #             )
        #     market_order = self.trading_client.submit_order(
        #         order_data=market_order_data)
            
    def new_data(self,data):
        self.close.append(data)
        self.sma1 = talib.SMA(self.close, self.n1)
        self.sma2 = talib.SMA(self.close, self.n2)
        self.order()


##TEST DE LA CLASE

api_key = os.environ["API_KEY"]
secret_key = os.environ["SECRET_KEY"]
base_url = os.environ["API_URL"]

symbols = ["MMM"]

api = REST(key_id=api_key, secret_key=secret_key, base_url=base_url, api_version="v2")
trading_client = TradingClient(api_key, secret_key, paper=True)
# Setting the date range of stock prices we want to get
end_date = datetime.today() - timedelta(days=1)
start_date = end_date - timedelta(days=30)

df_barset = api.get_bars(
    symbols,
    TimeFrame.Day,
    start_date.strftime("%Y-%m-%d"),
    end_date.strftime("%Y-%m-%d"),
    adjustment="all",
).df
df_barset = df_barset.reset_index(level=0)

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

estrategia_sma = StrategyAccount(df_barset["Close"], "MMM", trading_client)

print(estrategia_sma.sma1)
print(estrategia_sma.sma2)

estrategia_sma.order()

        
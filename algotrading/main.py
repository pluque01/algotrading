import os
import importlib
import re
import pandas as pd
from typing import List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from backtesting import Backtest

from .models import Asset
from . import strategies

api_key = os.environ["API_KEY"]
secret_key = os.environ["SECRET_KEY"]
base_url = os.environ["API_URL"]

api = REST(key_id=api_key, secret_key=secret_key, base_url=base_url, api_version="v2")
app = FastAPI()


# This function cicles through the assets and creates a Symbol object for each one
def parse_assets(assets):
    parsed_assets_list: List[Asset] = []
    for asset in assets:
        parsed_asset = Asset(
            id=asset.id, symbol=asset.symbol, name=asset.name, exchange=asset.exchange
        )
        parsed_assets_list.append(parsed_asset)
    return parsed_assets_list


def parse_timeframe(string):
    pattern = r"(\d+)([A-Za-z]+)"
    matches = re.match(pattern, string)

    if matches:
        # Get the quantity and time unit
        quantity = int(matches.group(1))
        time_unit = TimeFrameUnit[matches.group(2)]
        return quantity, time_unit
    else:
        raise ValueError(f"Invalid timeframe {string}")


@app.get("/assets")
def get_assets() -> List[Asset]:
    active_assets = api.list_assets(status="active")
    symbols = parse_assets(active_assets)
    return symbols


@app.get("/strategies")
def get_strategies():
    strategies_module = importlib.import_module("algotrading.strategies")
    strategies_atributes = dir(strategies_module)

    strategies = [
        atribute
        for atribute in strategies_atributes
        if isinstance(getattr(strategies_module, atribute), type)
        and atribute != "Strategy"
    ]

    return {"strategies": strategies}


@app.get("/backtest/{symbol}")
def get_backtest(
    symbol: str, start: str, end: str, strategy: str, timeframe: str | None = "1Hour"
):
    try:
        datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422, detail="End date must be in the format YYYY-MM-DD"
        )

    try:
        datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422, detail="Start date must be in the format YYYY-MM-DD"
        )

    chosen_strategy_class = getattr(strategies, "SmaCross")
    try:
        # Obtener la clase del módulo strategies utilizando getattr
        chosen_strategy_class = getattr(strategies, strategy)
        # Verificar si la clase existe y es una clase
    except AttributeError:
        raise HTTPException(status_code=422, detail="Strategy not found")

    try:
        amount, timeframe_unit = parse_timeframe(timeframe)
        TimeFrame(amount, timeframe_unit)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    df_barset = api.get_bars(
        symbol,
        timeframe,
        start,
        end,
        adjustment="all",
    ).df
    df_barset = df_barset.reset_index(level=0)
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

    bt = Backtest(
        df_barset,
        chosen_strategy_class,
        cash=10000,
        commission=0.002,
        exclusive_orders=True,
    )
    bt.optimize(
        n1=range(5, 30, 5),
        n2=range(10, 70, 5),
        maximize="Equity Final [$]",
        constraint=lambda param: param.n1 < param.n2,
    )

    file = f"{symbol}_{start}_{end}_{timeframe}_{strategy}"
    bt.plot(filename=f"frontend/{file}")
    return {"success": file}

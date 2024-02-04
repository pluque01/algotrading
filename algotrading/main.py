import os
import importlib
from typing import List

from fastapi import FastAPI
from alpaca_trade_api import REST
from .models import Asset

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


# @app.get("/backtest/{symbol}")
# def get_barset(symbol: str, start: str, end: str, timeframe: str | None = "1Hour"):

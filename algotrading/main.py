import os
import importlib
import re
from typing import List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

from alpaca.data import (
    StockHistoricalDataClient,
    StockBarsRequest,
    Adjustment,
    TimeFrame,
    TimeFrameUnit,
)
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus


from backtesting import Backtest

from .models import Asset, BacktestResults
from . import strategies

api_key = os.environ["API_KEY"]
secret_key = os.environ["SECRET_KEY"]
base_url = os.environ["API_URL"]

# api = REST(key_id=api_key, secret_key=secret_key, base_url=base_url, api_version="v2")
trading_client = TradingClient(api_key, secret_key)
stock_client = StockHistoricalDataClient(api_key, secret_key)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

htmx_init(
    templates=Jinja2Templates(directory=Path("algotrading") / "templates"),
    file_extension="html",
)


# This function cicles through the assets and creates a Symbol object for each one
def parse_assets(assets):
    parsed_assets_list: List[Asset] = []
    for asset in assets:
        asset_id = str(asset.id)
        parsed_asset = Asset(
            id=asset_id, symbol=asset.symbol, name=asset.name, exchange=asset.exchange
        )
        parsed_assets_list.append(parsed_asset)
    return parsed_assets_list


def parse_backtest_results(results):
    return BacktestResults(
        start_time=results["Start"].strftime("%d-%m-%Y"),
        end_time=results["End"].strftime("%d-%m-%Y"),
        duration=str(results["Duration"]),
        exposure_time=results["Exposure Time [%]"],
        equity_final=results["Equity Final [$]"],
        equity_peak=results["Equity Peak [$]"],
        ret=results["Return [%]"],
    )


search_params = GetAssetsRequest(status=AssetStatus.ACTIVE)
assets = trading_client.get_all_assets(search_params)
every_symbol = parse_assets(assets)


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


def filter_assets_by_prefix(assets: List[Asset], prefix: str) -> List[Asset]:
    filtered_assets = [
        asset
        for asset in assets
        if asset.name.lower().startswith(prefix.lower())
        or asset.symbol.lower().startswith(prefix.lower())
    ]
    return filtered_assets


@app.get("/assets", response_class=HTMLResponse)
@htmx("assets")
def get_assets(request: Request, search: str):
    assets = filter_assets_by_prefix(every_symbol, search)
    print(assets)
    return {"assets": assets}


@app.get("/strategies", response_class=HTMLResponse)
@htmx("strategies")
def get_strategies(request: Request):
    strategies_module = importlib.import_module("algotrading.strategies")
    strategies_atributes = dir(strategies_module)

    strategies = [
        atribute
        for atribute in strategies_atributes
        if isinstance(getattr(strategies_module, atribute), type)
        and atribute != "Strategy"
    ]

    return {"strategies": strategies}


@app.get("/backtest", response_class=HTMLResponse)
@htmx("backtest_result")
def get_backtest(
    request: Request,
    symbol: str,
    start: str,
    end: str,
    strategy: str,
    timeframe: str | None = "1Hour",
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
        tf = TimeFrame(amount, timeframe_unit)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=tf,
        start=datetime.strptime(start, "%Y-%m-%d"),
        end=datetime.strptime(end, "%Y-%m-%d"),
        adjustment=Adjustment.ALL,
    )

    bars = stock_client.get_stock_bars(request_params)

    if bars.data == {}:
        raise HTTPException(status_code=404, detail="No data found for the given input")

    bars_df = bars.df

    bars_df = bars_df.reset_index(level=0)
    # Para que funcione correctamente hay que renombrar las columnas y establecer el índice del
    # dataFrame en la fecha.
    bars_df = bars_df.rename(
        columns={
            "open": "Open",
            "close": "Close",
            "high": "High",
            "low": "Low",
            "volume": "Volume",
        }
    )
    # bars_df["timestamp"] = pd.to_datetime(bars_df["timestamp"], errors="ignore")

    # bars_df = bars_df.set_index("timestamp")

    bt = Backtest(
        bars_df,
        chosen_strategy_class,
        cash=10000,
        commission=0.002,
        exclusive_orders=True,
    )
    # bt.optimize(
    #     n1=range(5, 30, 5),
    #     n2=range(10, 70, 5),
    #     maximize="Equity Final [$]",
    #     constraint=lambda param: param.n1 < param.n2,
    # )
    backtest_results = parse_backtest_results(bt.run())
    for field_name, value in backtest_results.dict().items():
        if isinstance(value, float):
            setattr(backtest_results, field_name, round(value, 2))
    # file = f"{symbol}_{start}_{end}_{timeframe}_{strategy}"
    # bt.plot(filename=f"frontend/{file}")
    return {"results": backtest_results}

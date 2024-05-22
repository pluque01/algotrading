import os
from pathlib import Path
from datetime import datetime
from typing import Union, List, Dict
from .models import BacktestResults
from backtesting import Backtest, Strategy
from alpaca.data import (
    StockHistoricalDataClient,
    StockBarsRequest,
    Adjustment,
    TimeFrame,
)


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


class BacktesterRequest:
    assets: Union[str, List[str]]
    strategy: Strategy
    start_date: datetime
    end_date: datetime
    timeframe: TimeFrame
    cash: float = 10000
    commission: float = 0.002
    exclusive_orders: bool = True

    def __init__(
        self,
        assets: Union[str, List[str]],
        strategy: Strategy,
        start_date: datetime,
        end_date: datetime,
        timeframe: TimeFrame,
        cash: float = 10000,
        commission: float = 0.002,
        exclusive_orders: bool = True,
    ):
        self.assets = assets
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.cash = cash
        self.commission = commission
        self.exclusive_orders = exclusive_orders


class Backtester:
    data: Dict[str, BacktestResults]
    figures: Dict[str, str]
    stock_client: StockHistoricalDataClient

    def __init__(self):
        self.data = {}
        self.figures = {}
        api_key = os.environ["API_KEY"]
        secret_key = os.environ["SECRET_KEY"]
        self.stock_client = StockHistoricalDataClient(api_key, secret_key)

    def __del__(self):
        self.clear_backtests()

    def clear_backtests(self):
        self.data = {}
        for figure in self.figures.values():
            os.remove(f"{Path('algotrading')}{figure}")
        self.figures = {}

    def add_backtest(self, id: str, backtest: BacktestResults, figure: str):
        self.data[id] = backtest
        self.figures[id] = figure

    def get_backtest_data_by_id(self, id: str):
        return self.data[id]

    def get_backtest_data(self):
        return self.data

    def get_backtest_figure_by_id(self, id: str):
        return self.figures.get(id)

    def perform_backtest(self, request: BacktesterRequest):
        self.clear_backtests()

        for asset in request.assets:
            request_params = StockBarsRequest(
                symbol_or_symbols=[asset],
                timeframe=request.timeframe,
                start=request.start_date,
                end=request.end_date,
                adjustment=Adjustment.ALL,
            )

            bars = self.stock_client.get_stock_bars(request_params)

            if bars.data == {}:
                raise ValueError("No data found for the given input")

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
            bt = Backtest(
                bars_df,
                request.strategy,
                cash=request.cash,
                commission=request.commission,
                exclusive_orders=request.exclusive_orders,
            )

            backtest_results = parse_backtest_results(bt.run())
            # Round the float values to 2 decimal places
            for field_name, value in backtest_results.dict().items():
                if isinstance(value, float):
                    setattr(backtest_results, field_name, round(value, 2))

            filename = f"/plot/{asset}_{request.start_date}_{request.end_date}_{request.timeframe}_{request.strategy.__name__}.html"
            bt.plot(filename=f"{Path('algotrading')}{filename}")
            self.data[asset] = backtest_results
            self.figures[asset] = filename

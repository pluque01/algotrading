from datetime import datetime
from pydantic import BaseModel


class Asset(BaseModel):
    id: str
    exchange: str
    symbol: str
    name: str


class BacktestResults(BaseModel):
    start_time: datetime
    end_time: datetime
    duration: str
    exposure_time: float
    equity_final: float
    equity_peak: float
    ret: float

from pydantic import BaseModel, Field


class Asset(BaseModel):
    id: str
    exchange: str
    symbol: str
    name: str


class BacktestResults(BaseModel):
    start_time: str = Field(title="Start Time", description="")
    end_time: str = Field(title="End Time", description="")
    duration: str = Field(title="Duration", description="")
    exposure_time: float = Field(title="Exposure Time", description="")
    equity_final: float = Field(title="Final Equity [$]", description="")
    equity_peak: float = Field(title="Peak Equity [$]", description="")
    ret: float = Field(title="Return [%]", description="")

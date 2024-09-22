from pydantic import BaseModel, Field


class Asset(BaseModel):
    id: str
    exchange: str
    symbol: str
    name: str

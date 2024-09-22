from pydantic import BaseModel


class Asset(BaseModel):
    id: str
    exchange: str
    symbol: str
    name: str

from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")

    product_id: str
    price: str
    price_percentage_change_24h: str
    volume_24h: str
    volume_percentage_change_24h: str


class Candle(BaseModel):
    start: str
    low: str
    high: str
    open: str
    close: str
    volume: str

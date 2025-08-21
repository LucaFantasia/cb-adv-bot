from pydantic import BaseModel, ConfigDict


class Balance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: str
    currency: str


class Account(BaseModel):
    model_config = ConfigDict(extra="ignore")

    uuid: str
    name: str
    currency: str
    available_balance: Balance

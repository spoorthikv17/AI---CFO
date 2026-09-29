from datetime import date
from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    date: date
    description: str
    category: str
    type: str
    amount: float


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
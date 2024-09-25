from typing import List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    user_id: int
    transaction_type: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: Decimal
    transaction_date: str

    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True)


class UserTransactionsResponse(BaseModel):
    user_id: int
    username: str
    transactions: List[TransactionResponse]

    model_config = ConfigDict(from_attributes=True)


class ReferralCreate(BaseModel):
    referrer_id: int
    referred_id: int




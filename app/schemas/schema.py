from typing import List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class ReferralCreate(BaseModel):
    referral_code: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UsernameResponse(BaseModel):
    user_id: int
    username: str

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


class ReferralResponse(BaseModel):
    referrer_id: int
    referred_id: int

    model_config = ConfigDict(from_attributes=True)


class GetAllReferralsResponse(BaseModel):
    user_id: int
    username: str
    referrals: List[UsernameResponse]


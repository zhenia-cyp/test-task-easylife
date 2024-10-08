from typing import List
from pydantic import BaseModel, ConfigDict, field_validator
from decimal import Decimal
from datetime import datetime
from pydantic_core.core_schema import ValidationInfo


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


class UserProfileResponse(BaseModel):
    id: int
    username: str
    referral_code: str
    created_at:  datetime


class RegisterUserSchema(BaseModel):
    username: str
    email: str
    password: str
    password_check: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('password_check')
    def passwords_match(cls, value: str, info: ValidationInfo):
        password = info.data.get('password')
        if password and value != password:
            raise ValueError('Passwords do not match')
        return value


class UserSignInRequest(BaseModel):
        email: str
        hashed_password: str

        model_config = ConfigDict(from_attributes=True)


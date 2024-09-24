from pydantic import BaseModel, ConfigDict



class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    user_id: int
    transaction_type: str
    amount: float


class ReferralCreate(BaseModel):
    referrer_id: int
    referred_id: int




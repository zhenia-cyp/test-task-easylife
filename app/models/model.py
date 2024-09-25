from sqlalchemy import Column, Integer, String, func,  ForeignKey, MetaData, DateTime, Float
from sqlalchemy.orm import declarative_base
import datetime
from sqlalchemy.orm import validates
from pytz import timezone


Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __str__(self):
        return(
            f"User: id: {self.id}," 
            f"username: {self.username},"
        )

    def __repr__(self):
        return (
            f"User: id: {self.id},"
            f"username: {self.username},"

        )


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())

    @validates('amount')
    def validate_amount(self, key, value):
        if value == 0.0:
            raise ValueError("Transaction amount cannot be zero.")
        if value < 0.0:
            raise ValueError("Transaction amount cannot be negative.")
        return value

    def get_transaction_date_in_local(self):
        local_timezone = timezone('Europe/Kyiv')
        self.transaction_date  = self.transaction_date.astimezone(local_timezone)
        return self.transaction_date


    def __str__(self):
        return (
            f"Transaction: id: {self.id},"
            f"user_id: {self.user_id},"
            f"transaction_type: {self.transaction_type},"
            f"amount: {self.amount},"
            f"transaction_date: {self.transaction_date}"
        )


    def __repr__(self):
        return (
            f"Transaction: id: {self.id},"
            f"user_id: {self.user_id},"
            f"transaction_type: {self.transaction_type},"
            f"amount: {self.amount},"
            f"transaction_date: {self.transaction_date}"
        )


class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __str__(self):
        return(
                f"Referral: id: {self.id}",
                f"referrer_id: {self.referrer_id}," 
                f"referred_id: {self.referred_id}"
        )

    def __repr__(self):
        return(
            f"Referral: id: {self.id},"
            f"referrer_id: {self.referrer_id},"
            f"referred_id: {self.referred_id}"
        )



from sqlalchemy import Column, Boolean, Integer, String, func,  ForeignKey, MetaData, DateTime, Float, Numeric
from sqlalchemy.orm import declarative_base
import datetime
from sqlalchemy.orm import validates
from pytz import timezone



Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)
    hashed_password = Column(String)
    referral_code = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())


    def __str__(self):
        return f"User: id: {self.id}, username: {self.username}, email: {self.email}," \
               f"referral_code: {self.referral_code}, role: {self.role}, created_at: {self.created_at}"


    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, " \
               f"referral_code={self.referral_code}, is_active={self.is_active}, " \
               f"is_superuser={self.is_superuser}, role={self.role}, " \
               f"created_at={self.created_at})"


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


    def get_transaction_date_in_local(self, local_tz='Europe/Kyiv'):
        local_timezone = timezone(local_tz)
        self.transaction_date = self.transaction_date.astimezone(local_timezone)
        return self.transaction_date


    def __str__(self):
        return f"Transaction: id: {self.id}, user_id: {self.user_id}, " \
               f"transaction_type: {self.transaction_type}, amount: {self.amount}, " \
               f"transaction_date: {self.transaction_date}"


    def __repr__(self):
        return f"Transaction(id={self.id}, user_id={self.user_id}, " \
               f"transaction_type={self.transaction_type}, amount={self.amount}, " \
               f"transaction_date={self.transaction_date})"


class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    def __str__(self):
        return f"Referral: id={self.id}, referrer_id={self.referrer_id}, " \
               f"referred_id={self.referred_id}"


    def __repr__(self):
        return f"Referral(id={self.id}, referrer_id={self.referrer_id}, " \
               f"referred_id={self.referred_id})"


class Wallet(Base):
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),  nullable=False)
    balance = Column(Numeric(precision=10, scale=2), default=0.00)
    first_line_bonus_balance = Column(Numeric(precision=10, scale=2), default=0.00)
    second_line_bonus_balance = Column(Numeric(precision=10, scale=2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=datetime.datetime.now())


    def __str__(self):
        return f"Wallet: id: {self.id}, user_id: {self.user_id}, " \
               f"balance: {self.balance}, first_line_bonus_balance: {self.first_line_bonus_balance}, " \
               f"second_line_bonus_balance: {self.second_line_bonus_balance}"


    def __repr__(self):
        return f"Wallet: id: {self.id}, user_id: {self.user_id}, " \
               f"balance: {self.balance}, first_line_bonus_balance: {self.first_line_bonus_balance}, " \
               f"second_line_bonus_balance: {self.second_line_bonus_balance}"





from app.models.model import Transaction
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def replace_date_format(transactions):
    if isinstance(transactions, list):
        for transaction in transactions:
            formatted_date = transaction.get_transaction_date_in_local().strftime('%d.%m.%Y, %H:%M')
            transaction.transaction_date = formatted_date
        return transactions

    elif isinstance(transactions, Transaction):
        formatted_date = transactions.get_transaction_date_in_local().strftime('%d.%m.%Y, %H:%M')
        transactions.transaction_date = formatted_date
        return transactions
    return None





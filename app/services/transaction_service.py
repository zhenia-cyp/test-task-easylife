from app.models.model import Transaction
from app.schemas.schema import TransactionCreate, TransactionResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.utils.crud_repository import CrudRepository
from sqlalchemy import select


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_transaction(self, transaction: TransactionCreate) -> TransactionResponse | bool:
        """this method returns a new transaction in the database, the identical transaction user can create only after 1 minute"""
        crud_repository = CrudRepository(self.session, Transaction)
        transac_dict = transaction.model_dump(exclude_unset=True)

        one_minute = datetime.now() - timedelta(minutes=1)
        # find the identical transaction within 1 minute
        stmt = select(Transaction).where(
            Transaction.user_id == transac_dict['user_id'],
            Transaction.transaction_type == transac_dict['transaction_type'],
            Transaction.amount == transac_dict['amount'],
            Transaction.transaction_date >= one_minute
        )
        result = await self.session.execute(stmt)
        existing_transaction = result.scalars().first()
        if existing_transaction:
            return False

        new_transaction = await crud_repository.create_one(transac_dict)
        formatted_date = new_transaction.get_transaction_date_in_local().strftime('%d.%m.%Y, %H:%M')
        data = {
            "id": new_transaction.id,
            "user_id": new_transaction.user_id,
            "transaction_type": new_transaction.transaction_type,
            "amount": new_transaction.amount,
            "transaction_date": formatted_date
        }
        return TransactionResponse.model_validate(data)





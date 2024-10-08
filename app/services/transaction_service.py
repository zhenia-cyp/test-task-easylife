from app.models.model import Transaction, Referral
from app.schemas.schema import TransactionCreate, TransactionResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.utils.crud_repository import CrudRepository
from sqlalchemy import select


class TransactionService:
    MINIMUM_TRANSACTION_AMOUNT = 10.00
    FIRST_LINE_BONUS_RATE = 0.10
    SECOND_LINE_BONUS_RATE = 0.05


    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_transaction(self, transaction: TransactionCreate) -> TransactionResponse | bool:
        """method returns a new transaction, user can create another, identical transaction only after a minute."""
        crud_repository = CrudRepository(self.session, Transaction)
        transac_dict = transaction.model_dump(exclude_unset=True)

        one_minute = datetime.now() - timedelta(minutes=1)
        # Find the identical transaction within 1 minute
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
        return await self.transaction_response(new_transaction)


    async def transaction_response(self, transaction: Transaction) -> TransactionResponse:
        """create a TransactionResponse object from a Transaction."""
        formatted_date = transaction.get_transaction_date_in_local().strftime('%d.%m.%Y, %H:%M')
        data = {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "transaction_type": transaction.transaction_type,
            "amount": transaction.amount,
            "transaction_date": formatted_date
        }
        await self.add_bonuses(transaction)
        return TransactionResponse.model_validate(data)


    async def add_bonuses(self, transaction: Transaction) -> None:
        # add bonus only if the transaction amount exceeds the minimum
        referral_crud_repository = CrudRepository(self.session, Referral)
        referral_first_line = await referral_crud_repository.get_one_by(referred_id=transaction.user_id)
        if referral_first_line:
            if transaction.amount >= self.MINIMUM_TRANSACTION_AMOUNT:
                referrer_id = referral_first_line.referrer_id
                bonus_amount_first_line = transaction.amount * self.FIRST_LINE_BONUS_RATE # 10%
                bonus_data_first_line = {
                    "user_id": referrer_id,
                    "transaction_type": "bonus_transaction_first_line",
                    "amount": bonus_amount_first_line
                }
                crud_repository = CrudRepository(self.session, Transaction)
                bonus_transaction_first_line = await crud_repository.create_one(bonus_data_first_line)
                print('bonus_transaction_first_line: ', bonus_transaction_first_line)

                referral_second_line = await referral_crud_repository.get_one_by(referred_id=referrer_id)
                if referral_second_line:
                    if transaction.amount >= self.MINIMUM_TRANSACTION_AMOUNT:
                        referrer_id = referral_second_line.referrer_id
                        bonus_amount_second_line = transaction.amount * self.SECOND_LINE_BONUS_RATE # 5%
                        bonus_data_second_line = {
                            "user_id": referrer_id,
                            "transaction_type": "bonus_transaction_second_line",
                            "amount": bonus_amount_second_line
                        }
                        bonus_transaction_second_line = await crud_repository.create_one(bonus_data_second_line)
                        print('bonus_transaction_second_line: ', bonus_transaction_second_line)


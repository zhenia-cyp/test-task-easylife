from app.models.model import Transaction, Referral, Wallet
from app.schemas.schema import TransactionCreate, TransactionResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.utils.crud_repository import CrudRepository
from sqlalchemy import select
import decimal


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
        if transaction.amount < self.MINIMUM_TRANSACTION_AMOUNT:
            return

        referral_crud_repository = CrudRepository(self.session, Referral)
        referral_first_line = await referral_crud_repository.get_one_by(referred_id=transaction.user_id)
        if referral_first_line:
            referrer_id_first_line = referral_first_line.referrer_id
            bonus_amount_first_line = transaction.amount * self.FIRST_LINE_BONUS_RATE  # 10%
            await self.update_wallet_balance(referrer_id_first_line, bonus_amount_first_line, line="first")
            print(f'Bonus {bonus_amount_first_line} first line (user_id: {referrer_id_first_line})')

            referral_second_line = await referral_crud_repository.get_one_by(referred_id=referrer_id_first_line)
            if referral_second_line:
                referrer_id_second_line = referral_second_line.referrer_id
                bonus_amount_second_line = transaction.amount * self.SECOND_LINE_BONUS_RATE  # 5%
                await self.update_wallet_balance(referrer_id_second_line, bonus_amount_second_line, line="second")
                print(f'Bonus {bonus_amount_second_line} second line (user_id: {referrer_id_second_line})')


    async def update_wallet_balance(self, user_id: int, bonus_amount: float, line: str) -> None:
        wallet_crud_repository = CrudRepository(self.session, Wallet)
        wallet = await wallet_crud_repository.get_one_by(user_id=user_id)
        if wallet:
            wallet.balance += decimal.Decimal(bonus_amount)  # Convert float to decimal
            if line == "first":
                wallet.first_line_bonus_balance += decimal.Decimal(bonus_amount)
            elif line == "second":
                wallet.second_line_bonus_balance += decimal.Decimal(bonus_amount)
        else:
            wallet_data = {
                'user_id': user_id,
                'balance': decimal.Decimal(bonus_amount),  # Convert float to decimal
                'first_line_bonus_balance': decimal.Decimal(bonus_amount) if line == "first" else decimal.Decimal(0),
                'second_line_bonus_balance': decimal.Decimal(bonus_amount) if line == "second" else decimal.Decimal(0),
            }
            await wallet_crud_repository.create_one(wallet_data)

        await self.session.commit()

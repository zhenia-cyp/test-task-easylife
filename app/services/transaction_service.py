from typing import List

from app.models.model import Transaction, Referral, Wallet, User
from app.schemas.schema import TransactionCreate, TransactionResponse, BalanceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.services.user_service import UserService
from app.utils.crud_repository import CrudRepository
from sqlalchemy import select
import decimal
from app.utils.utils import replace_date_format



class TransactionService:
    MINIMUM_TRANSACTION_AMOUNT = 10.00
    FIRST_LINE_BONUS_RATE = 0.10
    SECOND_LINE_BONUS_RATE = 0.05


    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_transaction(self, transaction: TransactionCreate) -> TransactionResponse | bool:
        """method returns a new transaction, user can create another,
          identical transaction only after a minute."""
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
        """create a TransactionResponse object from a Transaction"""
        formatted_date = transaction.get_transaction_date_in_local().strftime('%Y-%m-%d, %H:%M')
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
        """this method allocates bonuses from referrals: 10% of
           the purchase amount from the first level and 5% from the second level"""
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
        """updates the user's wallet balance depending on the referral line (first or second)
           and returns common amount bonus transactions"""
        wallet_crud_repository = CrudRepository(self.session, Wallet)
        wallet = await wallet_crud_repository.get_one_by(user_id=user_id)
        if wallet:
            wallet.balance += decimal.Decimal(bonus_amount)
            if line == "first":
                wallet.first_line += decimal.Decimal(bonus_amount)
                wallet.purchases += 1
                await self.session.commit()
            elif line == "second":
                wallet.second_line += decimal.Decimal(bonus_amount)
                wallet.purchases += 1
                await self.session.commit()
        else:
            wallet_data = {
                'user_id': user_id,
                'balance': decimal.Decimal(bonus_amount),
                'first_line': decimal.Decimal(bonus_amount) if line == "first" else decimal.Decimal(0),
                'second_line': decimal.Decimal(bonus_amount) if line == "second" else decimal.Decimal(0),
                'purchases': 1
            }
            await wallet_crud_repository.create_one(wallet_data)


    async def request_payout(self, user_id: int, payout: float) -> TransactionResponse | dict:
        """This method returns a transaction - a request to withdraw funds earned from referrals"""
        wallet_crud_repository = CrudRepository(self.session, Wallet)
        transaction_crud_repository = CrudRepository(self.session, Transaction)

        wallet = await wallet_crud_repository.get_one_by(user_id=user_id)
        if not wallet:
            return {"status": "error", "message": "Wallet not found"}

        if wallet.balance == decimal.Decimal(0):
            return {"status": "error", "message": "Cannot withdraw. Your balance is zero"}

        if payout <= 0:
            return {"status": "error", "message": "Withdrawal amount must be greater than zero"}

        if wallet.balance < decimal.Decimal(payout):
            return {"status": "error", "message": "Insufficient balance for withdrawal"}

        wallet.balance -= decimal.Decimal(payout)

        if wallet.balance < 0:
            return {"status": "error", "message": "The wallet balance cannot be less than zero"}

        data = {
            'user_id': user_id,
            'transaction_type': 'request_payout',
            'amount': decimal.Decimal(payout),
        }
        transaction = await transaction_crud_repository.create_one(data)

        if transaction and wallet.balance == decimal.Decimal(0):
            wallet.balance = decimal.Decimal(0)
            wallet.first_line = decimal.Decimal(0)
            wallet.second_line = decimal.Decimal(0)
            wallet.purchases = decimal.Decimal(0)
            await self.session.commit()
            return TransactionResponse.model_validate(transaction)
        return TransactionResponse.model_validate(transaction)


    async def filter_bonus_transactions_by_date(
            self, user_id: int, start_date: str | None, end_date: str | None) ->  List[TransactionResponse]:
        """this method returns first and second-line referral transactions filtered by date"""
        referral_crud_repository = CrudRepository(self.session, Referral)
        first_line_referrals = await referral_crud_repository.get_all_by(referrer_id=user_id)
        first_line_user_ids = [referral.referred_id for referral in first_line_referrals]

        second_line_stmt = select(Referral.referred_id).where(Referral.referrer_id.in_(first_line_user_ids))
        result = await self.session.execute(second_line_stmt)
        second_line_user_ids = [row[0] for row in result.all()]

        all_referred_ids = first_line_user_ids + second_line_user_ids

        if not all_referred_ids:
            return []
        stmt = select(Transaction).where(Transaction.user_id.in_(all_referred_ids))
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        if start_date:
            stmt = stmt.where(Transaction.transaction_date >= start_date)
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
        if end_date:
            stmt = stmt.where(Transaction.transaction_date <= end_date)
        result = await self.session.execute(stmt)
        transactions = result.scalars().all()
        transactions = await replace_date_format(transactions)
        return transactions


    async def get_user_balance(self, user_id: int) -> BalanceResponse | None:
        wallet_crud_repository = CrudRepository(self.session, Wallet)
        wallet = await wallet_crud_repository.get_one_by(user_id=user_id)
        if wallet is None:
            return None
        return BalanceResponse(balance=wallet.balance)


    async def filter_payout_transaction_by_date(
            self, user_id: int, start_date: str | None, end_date: str | None) -> List[dict]:
        """This method returns payout transactions filtered by date range for a specific user"""

        start_date_obj = datetime.strptime(start_date, "%d-%m-%Y") if start_date else None
        end_date_obj = datetime.strptime(end_date, "%d-%m-%Y") if end_date else None


        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'request_payout'
        )

        if start_date_obj:
            stmt = stmt.where(Transaction.transaction_date >= start_date_obj)
        if end_date_obj:
            stmt = stmt.where(Transaction.transaction_date <= end_date_obj)

        result = await self.session.execute(stmt)
        transactions = result.scalars().all()


        return [
            {
                "id": t.id,
                "user_id": t.user_id,
                "transaction_type": t.transaction_type,
                "amount": str(t.amount),
                "transaction_date": t.transaction_date.isoformat()
            }
            for t in transactions
        ] if transactions else []
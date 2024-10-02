from sqlalchemy.sql.functions import current_user

from app.models.model import User, Transaction, Referral
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import UserCreate, UserResponse, TransactionResponse, ReferralCreate, ReferralResponse, \
    GetAllReferralsResponse
from sqlalchemy import select
from app.utils.crud_repository import CrudRepository
from app.utils.pagination import Pagination
from app.utils.utils import replace_date_format


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def is_user_exists(self, user: UserCreate) -> bool:
        """ check if the user exists in the database """
        crud_repository = CrudRepository(self.session, User)
        user = await crud_repository.get_one_by(username=user.username)
        if user:
            return True
        return False


    async def add_user(self, user: UserCreate) -> UserResponse:
        """ this method returns a new user  """
        user_dict = user.model_dump(exclude_unset=True)
        crud_repository = CrudRepository(self.session, User)
        new_user = await crud_repository.create_one(user_dict)
        print('new_user', new_user)
        return UserResponse.model_validate(new_user)


    async def get_user(self, user_id: int, page_params: PageParams) -> PaginationResponse[TransactionResponse] | None:
        """the method returns all transactions for a specific user by id"""
        user_crud_repository = CrudRepository(self.session, User)
        current_user = await user_crud_repository.get_one_by(id=user_id)
        if current_user is None:
            return None
        transaction_crud_repository = CrudRepository(self.session, Transaction)
        transactions = await transaction_crud_repository.get_all_by(user_id=user_id)
        transactions = await replace_date_format(transactions)

        pagination = Pagination(page_params, items=transactions, schema=PaginationResponse)
        transactions = await pagination.get_pagination()
        transactions.user_id = current_user.id
        transactions.username = current_user.username
        return PaginationResponse.model_validate(transactions)


    async def get_all_users(self, page_params: PageParams) -> PaginationListResponse:
        """this method returns all users and their transactions"""
        data = []
        result = await self.session.execute(
            select(User, Transaction)
            .join(Transaction, Transaction.user_id == User.id)
        )
        rows = result.fetchall()
        for user, transaction in rows:
            existing_user = next((item for item in data if item["user_id"] == user.id), None)
            if not existing_user:
                existing_user = {
                    "user_id": user.id,
                    "username": user.username,
                    "transactions": []
                }
                data.append(existing_user)
            transaction = await replace_date_format(transaction)
            existing_user["transactions"].append({
                "id": transaction.id,
                "transaction_type": transaction.transaction_type,
                "amount": transaction.amount,
                "transaction_date": transaction.transaction_date
            })
        pagination = Pagination(page_params, items=data, schema=PaginationListResponse)
        users = await pagination.get_pagination()
        return PaginationListResponse.model_validate(users)


    async def create_referral_by_code(self, code: str, referral: UserCreate ) -> ReferralResponse | None| str:
        """this method returns a referral by a referral code"""
        referal_crud_repository = CrudRepository(self.session, Referral)
        user_crud_repository = CrudRepository(self.session, User)
        user_referer = await user_crud_repository.get_one_by(referral_code=code)
        print('user_referer:', user_referer)
        if not user_referer:
            return None

        existing_user = await user_crud_repository.get_one_by(username=referral.username)
        if existing_user:
            has_referer = await referal_crud_repository.get_one_by(referred_id=existing_user.id)
            if has_referer:
                return 'has_referer'
            new_referal = await referal_crud_repository.create_one({"referrer_id": user_referer.id, "referred_id": existing_user.id})
            return new_referal
        new_user = await self.add_user(referral)
        new_referal = await referal_crud_repository.create_one(
            {"referrer_id": user_referer.id, "referred_id": new_user.id})
        return new_referal


    async def get_my_referrals(self, user_id: int) -> GetAllReferralsResponse | None:
        """method returns the current user's information with a list of their referred users"""
        user_crud_repository = CrudRepository(self.session, User)
        current_user = await user_crud_repository.get_one_by(id=user_id)
        if not current_user:
            return None
        data = {"user_id": current_user.id,
                "username": current_user.username,
                "referrals": []
                }
        referrals = await self.session.execute(
            select(Referral, User)
            .join(User, Referral.referred_id == User.id)
            .filter(Referral.referrer_id == user_id)
        )
        for referral, referred_user in referrals:
            data["referrals"].append({
                "user_id": referred_user.id,
                "username": referred_user.username
            })

        return GetAllReferralsResponse.model_validate(data)







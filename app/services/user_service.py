import uuid
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pydantic import BaseModel
from app.models.model import User, Transaction, Referral
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import (
    UserCreate, UserResponse, TransactionResponse, ReferralResponse,
    GetAllReferralsResponse, UserProfileResponse, RegisterUserSchema,
    GetAllNonReferralsResponse
)
from app.utils.crud_repository import CrudRepository
from app.utils.exceptions import GenerateReferralCodeException
from app.utils.pagination import Pagination
from app.utils.utils import replace_date_format, get_hash_password


class UserService:
    """service class responsible for managing user-related operations"""
    def __init__(self, session: AsyncSession, schema: Type[BaseModel] = None):
        self.session = session
        self.schema = schema


    async def is_user_exists(self, field: str, value: str) -> bool:
        """ Check if user exists by a specific field (email, username) """
        crud_repository = CrudRepository(self.session, User)
        filters = {field: value}
        user = await crud_repository.get_one_by(**filters)
        return user is not None


    async def generate_unique_referral_code(self, max_attempts: int = 2):
        """this method returns a unique sequence of type string"""
        attempts = 0
        while attempts < max_attempts:
            crud_repository = CrudRepository(self.session, User)
            code = str(uuid.uuid4())[:10]
            existing_code = await crud_repository.get_one_by(referral_code=code)
            if not existing_code:
                return code
            attempts += 1
        raise GenerateReferralCodeException()


    async def add_user(self, user: RegisterUserSchema) -> UserResponse:
        """ this method returns a new user  """
        hashed_password = get_hash_password(user.password)
        user_dict = user.model_dump(exclude={"password_check", "password"})
        user_dict["hashed_password"] = hashed_password
        user_dict["referral_code"] = await self.generate_unique_referral_code()
        crud_repository = CrudRepository(self.session, User)
        new_user = await crud_repository.create_one(user_dict)
        return UserResponse.model_validate(new_user)


    async def get_user(self, user_id: int,
        page_params: PageParams) -> PaginationResponse[TransactionResponse] | None:
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


    async def create_referral_by_code(self,
        code: str, referral_id: int ) -> ReferralResponse | None| bool | str:
        """this method returns a new referral """
        referral_crud_repository = CrudRepository(self.session, Referral)
        user_crud_repository = CrudRepository(self.session, User)
        user_referer = await user_crud_repository.get_one_by(referral_code=code)
        if user_referer is None:
            return None
        existing_user = await user_crud_repository.get_one_by(id=referral_id)
        print(' existing_user: ', existing_user)
        if existing_user:
            has_referer = await referral_crud_repository.get_one_by(referred_id=existing_user.id)
            print('has_referer: ',has_referer )
            if has_referer:
                return "has_referer"
            new_referral = await referral_crud_repository.create_one(
                {"referrer_id": user_referer.id, "referred_id": existing_user.id})
            print('new_referral: ', new_referral)
            return new_referral


    async def get_my_referrals(self, user_id: int) -> GetAllReferralsResponse | None:
        """this method returns the current user's information with
           a list of their referred users"""
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


    async def get_non_referrals(self, user_id: int) -> GetAllNonReferralsResponse | None:
        """this method returns a list of users who are not referred by the
           current user and not referred by anyone else."""
        user_crud_repository = CrudRepository(self.session, User)
        current_user = await user_crud_repository.get_one_by(id=user_id)
        if not current_user:
            return None

        referrals = await self.session.execute(
            select(User.id, User.username)
            .filter(User.id != user_id)
            .filter(~User.id.in_(
                select(Referral.referred_id)
            ))
        )

        data = {
            "user_id": current_user.id,
            "username": current_user.username,
            "non_referrals": []
        }

        for user in referrals.fetchall():
            data["non_referrals"].append({
                "user_id": user.id,
                "username": user.username
            })

        return GetAllNonReferralsResponse.model_validate(data)


    async def get_user_profile(self, user_id:int) -> UserProfileResponse:
        """this method returns info about user by id"""
        crud_repository = CrudRepository(self.session, User)
        user = await crud_repository.get_one_by(id=user_id)
        if user:
            return user


    async def delete_referral(self, referrer_id: int, referred_id: int) -> bool:
        """this method deletes a referral linked to the current user"""
        refferal_crud_repository = CrudRepository(self.session, Referral)
        my_referral = await refferal_crud_repository.get_one_by(
            referrer_id=referrer_id,
            referred_id=referred_id
        )
        if not my_referral:
            return False
        result = await refferal_crud_repository.delete_one(my_referral)
        return result

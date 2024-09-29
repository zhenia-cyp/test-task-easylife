from app.models.model import User, Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import UserCreate, UserResponse, TransactionResponse
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







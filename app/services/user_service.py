from app.models.model import User, Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import UserCreate, UserResponse, UserTransactionsResponse, TransactionResponse
from sqlalchemy import select
from app.utils.crud_repository import CrudRepository
from app.utils.pagination import Pagination
from app.utils.utils import replace_date_format


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def is_user_exists(self, user: UserCreate) -> bool:
        """ check if the user exists in the database """
        stmt = select(User).filter(User.username == user.username)
        result = await self.session.execute(stmt)
        exists = result.scalars().first()
        if exists:
            return True
        return False


    async def add_user(self, username: str) -> UserResponse:
        """ add a new user to the database """
        new_user = User(username=username)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserResponse.model_validate(new_user)


    async def get_user(self, user_id: int, page_params: PageParams) -> PaginationResponse[TransactionResponse] | None:
        """method gets all transactions for a specific user by id"""
        user_crud_repository = CrudRepository(self.session, User)
        current_user = await user_crud_repository.get_one_by(id=user_id)
        if current_user is None:
            return None
        transaction_crud_repository = CrudRepository(self.session, Transaction)
        transactions = await transaction_crud_repository.get_all_by(user_id=user_id)
        transactions = await replace_date_format(transactions)
        transaction_response = [TransactionResponse.model_validate(transaction) for transaction in transactions]

        pagination = Pagination(page_params, items=transaction_response, schema=PaginationResponse)
        paginated_transactions = await pagination.get_pagination()
        paginated_transactions.user_id = current_user.id
        paginated_transactions.username = current_user.username
        return paginated_transactions


    async def get_all_users(self, page_params: PageParams) -> PaginationListResponse:
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
        user_transactions_response = [UserTransactionsResponse.model_validate(item) for item in data]
        pagination = Pagination(page_params, items=user_transactions_response, schema=PaginationListResponse)
        users = await pagination.get_pagination()
        return users







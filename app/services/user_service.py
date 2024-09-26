from app.models.model import User, Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schema import UserCreate, UserResponse, UserTransactionsResponse
from sqlalchemy import select
from app.utils.crud_repository import CrudRepository
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


    async def get_user(self, user_id: int) -> UserTransactionsResponse:
        """method gets all transactions for a specific user by id"""
        user_crud_repository = CrudRepository(self.session, User)
        current_user = await user_crud_repository.get_one_by(id=user_id)
        transaction_crud_repository = CrudRepository(self.session, Transaction)
        transactions = await transaction_crud_repository.get_all_by(user_id=user_id)

        transactions = await replace_date_format(transactions)
        data = {
            'user_id': current_user.id,
            'username': current_user.username,
            'transactions': transactions
         }
        return UserTransactionsResponse.model_validate(data)








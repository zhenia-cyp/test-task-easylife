from app.models.model import User
from app.schemas.schema import UserCreate, UserResponse
from sqlalchemy import select


class UserService:
    def __init__(self, session):
        self.session = session


    async def is_user_exists(self, user: UserCreate) -> bool:
        """ Check if the user exists in the database """
        stmt = select(User).filter(User.username == user.username)
        result = await self.session.execute(stmt)
        exists = result.scalars().first()
        if exists:
            return True
        return False


    async def add_user(self, username: str) -> UserResponse:
        """ Add a new user to the database """
        new_user = User(username=username)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserResponse.model_validate(new_user)









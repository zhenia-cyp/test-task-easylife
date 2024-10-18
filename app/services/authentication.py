import logging
from app.auth.token import create_access_token, verify_token
from app.models.model import User
from app.utils.crud_repository import CrudRepository
from app.utils.exceptions import TokenError, CredentialsException
from app.utils.utils import verify_password


class AuthService:
    """provides methods for authenticating
    users and verifying tokens"""
    def __init__(self, session):
        self.logger = logging.getLogger(__name__)
        self.session = session


    async def authenticate_user(self, user, current_user):
        """authenticates a user by verifying the password"""
        if not verify_password(user.password, current_user.hashed_password):
            return False
        access_token = create_access_token(data={"sub": current_user.email})
        return access_token


    async def get_user_by_token(self, token: str):
        """returns a user based on a valid JWT token"""
        try:
            email = await verify_token(token)
        except Exception as e:
            self.logger.error(" %s", str(e))
            raise TokenError("Failed to decode the token") from e
        crud_repository = CrudRepository(self.session, User)
        user = await crud_repository.get_one_by(email=email)
        if not user:
            raise CredentialsException('User not found by token')
        return user


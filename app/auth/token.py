from datetime import timedelta, datetime
import jwt
from app.core.config import settings
from app.utils.exceptions import CredentialsException, TokenExpiredException


def create_access_token(data: dict):
    """this function creates a new JWT access token with the provided data"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def verify_token(token: str):
    """this functions verifies the provided JWT token, checking for
       expiration and validity"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get('exp')
        if exp is not None and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise TokenExpiredException("Token has expired")
        email = payload.get("sub")
        if email is None:
            raise CredentialsException("Could not validate credentials")
        return email
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredException("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise CredentialsException("Invalid token") from exc

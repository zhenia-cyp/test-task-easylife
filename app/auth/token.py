from datetime import timedelta, datetime
import jwt
from app.core.config import settings
from app.utils.exceptions import CredentialsException, TokenExpiredException, TokenNotFoundException


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get('exp')
        if exp is not None and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise TokenExpiredException("Token has expired")
        email = payload.get("sub")
        if email is None:
            raise CredentialsException("Could not validate credentials")
        return email
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException("Token has expired")
    except jwt.InvalidTokenError:
        raise CredentialsException("Invalid token")

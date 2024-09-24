from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.schemas.schema import UserResponse, UserCreate
from app.services.user_service import UserService
from fastapi import HTTPException


router_user = APIRouter()


@router_user.post("/add/user/", response_model=UserResponse)
async def add_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session)
    exists = await user_service.is_user_exists(user)
    if exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_id = await user_service.add_user(user.username)
    return user_id

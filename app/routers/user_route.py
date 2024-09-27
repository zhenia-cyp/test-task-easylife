from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import UserResponse, UserCreate, TransactionResponse
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


@router_user.get("/get/user/", response_model=PaginationResponse[TransactionResponse])
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session), page_params: PageParams = Depends(PageParams)):
    user_service = UserService(session)
    transactions = await user_service.get_user(user_id, page_params)
    if transactions is None:
        raise HTTPException(status_code=404, detail="User not found")
    return transactions


@router_user.get("/get/all/users/", response_model=PaginationListResponse)
async def get_user(session: AsyncSession = Depends(get_async_session), page_params: PageParams = Depends(PageParams)):
    user_service = UserService(session)
    users = await user_service.get_all_users(page_params)
    return users




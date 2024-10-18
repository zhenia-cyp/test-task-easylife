from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_async_session
from app.models.model import User, Wallet
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import (
    UserResponse, UserCreate, TransactionResponse, ReferralResponse,
    GetAllReferralsResponse, UserProfileResponse, RegisterUserSchema,
    UserSignInRequest, DeleteResponse, GetAllNonReferralsResponse
)
from app.services.authentication import AuthService
from app.services.user_service import UserService
from app.utils.crud_repository import CrudRepository
from app.utils.exceptions import TokenNotFoundException

router_user = APIRouter()
token_auth_scheme = HTTPBearer()


@router_user.post("/register/user/", response_model=UserResponse)
async def add_user(user: RegisterUserSchema,
                  session: AsyncSession = Depends(get_async_session)):
    """Registers a new user, ensuring that the
       email and username are unique and the passwords match"""
    user_service = UserService(session)
    email = await user_service.is_user_exists('email', user.email)
    if email:
        raise HTTPException(
             status_code=400,
             detail="User with this email already exists"
         )
    username = await user_service.is_user_exists('username', user.username)
    if username:
        raise HTTPException(
            status_code=400,
            detail="User with this username already registered"
        )
    if user.password != user.password_check:
        raise HTTPException(
            status_code=400,
            detail="The passwords do not match")
    user = await user_service.add_user(user)
    return user


@router_user.post("/login/", summary="to log into the system")
async def login(response: Response, user: UserSignInRequest,
                session: AsyncSession = Depends(get_async_session)):
    """authenticates the user and generates a JWT token, sets a cookie
       with the generated token and returns a success message"""
    user_crud_repository = CrudRepository(session, User)
    current_user = await user_crud_repository.get_one_by(email=user.email)
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    auth_service = AuthService(session)
    token = await auth_service.authenticate_user(user, current_user)
    if token is None:
        raise HTTPException(
              status_code=400,
              detail="Token not found"
          )
    response.set_cookie(
        key=settings.TOKEN_KEY,
        value=f"Bearer {token}",
        httponly=True,
        max_age=60 * 60 * 25,
        secure=False,
        samesite="lax"
    )
    return {"message": "Successfully logged in"}


@router_user.post("/logout/")
async def logout_user(response: Response):
    """logs out the user by deleting the authentication cookie"""
    response.delete_cookie(key=settings.TOKEN_KEY)
    return {"message": "Successfully logged out"}


@router_user.get("/get/user/{user_id}/", response_model=PaginationResponse[TransactionResponse])
async def get_user(user_id: int,
                   session: AsyncSession = Depends(get_async_session),
                   page_params: PageParams = Depends(PageParams)):
    """returns user transactions, filtered by pagination parameters"""
    user_service = UserService(session)
    transactions = await user_service.get_user(user_id, page_params)
    if transactions is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return transactions



@router_user.get("/", summary="admin panel")
async def home(request: Request, session: AsyncSession = Depends(get_async_session)):
    """renders the admin panel after verifying the user token and account status"""
    token = request.cookies.get('you_kent_find_it')
    if not token:
        raise TokenNotFoundException()
    auth_service = AuthService(session)
    user = await auth_service.get_user_by_token(token.replace("Bearer ", ""))
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is not active"
        )
    wallet_crud_repository = CrudRepository(session, Wallet)
    wallet = await wallet_crud_repository.get_one_by(user_id=user.id)
    context = {"request": request, "name": user, "wallet": wallet}
    from app.main import templates
    return templates.TemplateResponse("index.html", context)


@router_user.get("/get/all/users/", response_model=PaginationListResponse)
async def get_all_users(session: AsyncSession = Depends(get_async_session),
                   page_params: PageParams = Depends(PageParams)):
    """returns all users with pagination"""
    user_service = UserService(session)
    users = await user_service.get_all_users(page_params)
    return users


@router_user.post("/create/referral/by/{code}/", response_model=ReferralResponse)
async def create_referral(code: str, referral: UserCreate,
                         session: AsyncSession = Depends(get_async_session)):
    """returns the referral user linked with their referrer"""
    user_service = UserService(session)
    user = await user_service.create_referral_by_code(code, referral) # code - referer
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Referer with this code not found"
        )
    if user == 'has_referer':
        raise HTTPException(
            status_code=400,
            detail="User already has referer"
        )
    return user


@router_user.get("/get/all/referrals/{user_id}/", response_model=GetAllReferralsResponse)
async def get_referrals(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """returns a list of users associated with one referrer"""
    user_service = UserService(session)
    referrals = await user_service.get_my_referrals(user_id)
    if not referrals:
        raise HTTPException(status_code=404, detail="User not found")
    return referrals


@router_user.get("/get/all/not/refferals/{user_id}/", response_model=GetAllNonReferralsResponse)
async def get_not_referral_users(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """all users who are not referrals"""
    user_service = UserService(session)
    user = await user_service.get_non_referrals(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router_user.get("/get/user/profile/{user_id}/", response_model=UserProfileResponse)
async def get_profile(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """returns the all info about the specified user"""
    user_service = UserService(session)
    user = await user_service.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router_user.delete("/referrals/{referred_id}/current_user_id/", response_model=DeleteResponse)
async def remove_referral(referred_id: int, current_user_id: int,
                          session: AsyncSession = Depends(get_async_session)):
    """remove your referral"""
    user_service = UserService(session)
    success = await user_service.delete_referral(
        referrer_id=current_user_id, referred_id=referred_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Referral not found or not authorized to delete"
        )
    return success


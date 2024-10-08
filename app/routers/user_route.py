from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.models.model import User
from app.schemas.pagination import PageParams, PaginationResponse, PaginationListResponse
from app.schemas.schema import UserResponse, UserCreate, TransactionResponse, ReferralResponse, \
    GetAllReferralsResponse, UserProfileResponse, RegisterUserSchema, UserSignInRequest
from app.services.authentication import AuthService
from app.services.user_service import UserService
from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse
from app.utils.crud_repository import CrudRepository
from fastapi.security import HTTPBearer
from fastapi import Response
from fastapi import Cookie


router_user = APIRouter()
token_auth_scheme = HTTPBearer()


@router_user.post("/register/user/", response_model=UserResponse)
async def add_user(user: RegisterUserSchema, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session)
    email = await user_service.is_user_exists('email', user.email)
    if email:
         raise HTTPException(status_code=400, detail="User with this email already exists")
    username = await user_service.is_user_exists('username', user.username)
    if username:
        raise HTTPException(status_code=400, detail="User with this username already registered")
    if user.password != user.password_check:
        raise HTTPException(status_code=400, detail="The passwords do not match")
    user = await user_service.add_user(user)
    return user


@router_user.post("/login/")
async def login(response: Response, user: UserSignInRequest, session: AsyncSession = Depends(get_async_session)):
    user_crud_repository = CrudRepository(session, User)
    current_user = await user_crud_repository.get_one_by(email=user.email)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    auth_service = AuthService(session)
    token = await auth_service.authenticate_user(user, current_user)
    if token is False:
          raise HTTPException(status_code=400,detail="Unauthorized")
    response.set_cookie(
        key="you_kent_find_it",
        value=f"Bearer {token}",
        httponly=True,
        max_age=60 * 60 * 12,
        secure=False,
        samesite="lax"
    )
    return {"message": "Successfully logged in"}


@router_user.get("/get/user/{user_id}/", response_model=PaginationResponse[TransactionResponse])
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


@router_user.get("/")
async def home(request: Request, session: AsyncSession = Depends(get_async_session)):
    token = request.cookies.get('you_kent_find_it')
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    auth_service = AuthService(session)
    user = await auth_service.get_user_by_token(token.replace("Bearer ", ""))
    context = {"request": request, "name": user}
    from app.main import templates
    return templates.TemplateResponse("index.html", context)


@router_user.post("/create/referral/by/{code}/", response_model=ReferralResponse)
async def create_referral(code: str, referral: UserCreate, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session)
    user = await user_service.create_referral_by_code(code, referral) # code - referer
    if not user:
        raise HTTPException(status_code=404, detail="Referer with this code not found")
    if user:
        raise HTTPException(status_code=404, detail="User already has referer")
    return user


@router_user.get("/get/all/referrals/{user_id}", response_model=GetAllReferralsResponse)
async def get_referrals(user_id: int, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session)
    referrals = await user_service.get_my_referrals(user_id)
    if not referrals:
        raise HTTPException(status_code=404, detail="User not found")
    return referrals


@router_user.get("/get/user/profile/{user_id}/", response_model=UserProfileResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session)
    user = await user_service.get_user_profile(user_id)
    return user


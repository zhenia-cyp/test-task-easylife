from http.client import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request
import uvicorn
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers.health_check import check_health
from app.routers.user_route import router_user
from app.routers.transaction_route import router_transaction
from app.utils.exceptions import TokenExpiredException, CredentialsException, TokenError



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="add any string...")


app.include_router(router_user)
app.include_router(router_transaction)
app.include_router(check_health)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(request: Request, exc: HTTPException):

    return RedirectResponse(url="/docs#/default/login_login__post")


@app.exception_handler(TokenError)
async def token_no_found_exception_handler(request: Request,  exc: HTTPException):
    return RedirectResponse(url="/docs#/default/login_login__post")


@app.exception_handler(CredentialsException)
async def token_no_found_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/docs#/default/login_login__post")



if __name__ == "__main__":
    uvicorn.run('app.main:app', host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
import uvicorn
from fastapi import FastAPI, Request, HTTPException
import logging
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers.health_check import check_health
from app.routers.user_route import router_user
from app.routers.transaction_route import router_transaction
from app.utils.exceptions import (
    TokenExpiredException,
    CredentialsException,
    TokenError,
    TokenNotFoundException
)


logger = logging.getLogger(__name__)


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

# Exception handlers
@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(request: Request, exc: TokenExpiredException):
    """Handles TokenExpiredException by redirecting to the login page."""
    return RedirectResponse(url="/docs#/default/login_login__post")

@app.exception_handler(TokenError)
async def token_error_exception_handler(request: Request, exc: TokenError):
    """handles TokenError by redirecting to the login page."""
    return RedirectResponse(url="/docs#/default/login_login__post")

@app.exception_handler(CredentialsException)
async def credentials_exception_handler(request: Request, exc: CredentialsException):
    """handles CredentialsException by redirecting to the login page."""
    return RedirectResponse(url="/docs#/default/login_login__post")

@app.exception_handler(TokenNotFoundException)
async def token_not_found_exception_handler(request: Request, exc: TokenNotFoundException):
    """handles TokenNotFoundException by logging a warning and redirecting to the login page."""
    logger.warning("Token not found! URL: %s", request.url)
    return RedirectResponse(url="/docs#/default/login_login__post")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """handles general HTTPException and returns a JSON response."""
    logger.error("HTTPException raised: %s, URL: %s", exc.detail, request.url)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)

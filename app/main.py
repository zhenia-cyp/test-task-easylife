from fastapi import FastAPI
import uvicorn
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers.health_check import check_health
from app.routers.user_route import router_user
from app.routers.transaction_route import router_transaction



app = FastAPI()


app.include_router(router_user)
app.include_router(router_transaction)
app.include_router(check_health)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")



if __name__ == "__main__":
    uvicorn.run('app.main:app', host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
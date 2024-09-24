from fastapi import FastAPI
import uvicorn
from app.core.config import settings
from app.routers.health_check import check_health
from app.routers.user_route import router_user

app = FastAPI()


app.include_router(router_user)
app.include_router(check_health)


if __name__ == "__main__":
    uvicorn.run('app.main:app', host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
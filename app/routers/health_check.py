from fastapi import APIRouter

check_health = APIRouter()

@check_health.get("/health")
def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working..."
    }
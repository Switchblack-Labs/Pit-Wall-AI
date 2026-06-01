from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health_check():
    return {
        "healthy": True,
        "service": "Pit Wall AI Backend"
    }
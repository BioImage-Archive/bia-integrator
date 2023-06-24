from fastapi import APIRouter

router = APIRouter(prefix="/admin")

@router.get("/health-check")
def health_check():
    pass

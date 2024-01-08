from fastapi import APIRouter, Depends
from . import constants
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_current_user)],
    tags=[constants.OPENAPI_TAG_PRIVATE],
)


@router.get("/health-check")
def health_check():
    pass

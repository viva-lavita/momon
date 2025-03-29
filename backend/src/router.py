from fastapi import APIRouter

from src.users.router import router as users_router
from src.auth.router import router as auth_router


router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found=)"}},
)

router.include_router(users_router)
router.include_router(auth_router)

from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.users.router import router as users_router

router = APIRouter(
    responses={
        403: {"description": "The user doesn't have enough privileges"},  # пример
    },
)

router.include_router(users_router)
router.include_router(auth_router)

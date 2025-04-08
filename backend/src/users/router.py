from typing import Annotated
from fastapi import APIRouter, Depends

from src.main import app
from src.auth.models import User
from src.auth.service import get_current_active_user
from src.db import SessionDep
from src.users.schemas import UserPublic
from src.users.service import UserCRUD


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(session: SessionDep) -> list[UserPublic]:
    return await UserCRUD.get_all(session)


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

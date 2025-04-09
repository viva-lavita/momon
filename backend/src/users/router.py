from typing import Annotated, Any
from fastapi import APIRouter, Depends

from src.users.dependencies import get_current_active_user
from src.db import SessionDep

# from src.users.models import User
from src.users.schemas import UserPublic, UsersPublic
from src.users.service import UserCRUD


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UsersPublic)
async def get_users(session: SessionDep) -> Any:
    users = await UserCRUD.get_all(session)
    return UsersPublic(
        data=[UserPublic(**user.model_dump()) for user in users], count=len(users)
    )


@router.get("/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> Any:
    return current_user

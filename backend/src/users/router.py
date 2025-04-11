from typing import Annotated, Any
from fastapi import APIRouter, Depends

from src.users.dependencies import get_current_active_superuser, get_current_active_user
from src.db import SessionDep

from src.users.schemas import UserPublic, UsersPublic
from src.users.service import UserCRUD


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UsersPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
async def get_users(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> UsersPublic:
    """All users, only for superusers."""
    users = await UserCRUD.get_all(session, skip=skip, limit=limit)
    return UsersPublic(
        data=[UserPublic(**user.model_dump()) for user in users], count=len(users)
    )


@router.get("/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> Any:
    return current_user

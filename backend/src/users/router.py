import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException

from src.auth.utils import generate_new_account_email
from src.constants import EMAILS_DISABLED
from src.exceptions import EmailsDisabledException
from src.users.dependencies import (
    CurrentUser,
    get_current_active_superuser,
    get_current_active_user,
)
from src.config import settings
from src.db import SessionDep
from src.users.exceptions import UserAlreadyExists, UserAlreadyExistsException
from src.users.schemas import UserCreate, UserPublic, UserUpdateMe, UsersPublic
from src.users.service import UserCRUD
from src.utils import send_email


logger = logging.getLogger(__name__)
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
async def read_user_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
) -> Any:
    return current_user


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
async def create_user(user: UserCreate, session: SessionDep) -> Any:
    """
    Create new user only for superusers.

    role_id is not required, set to user by default.
    """
    try:
        db_user = await UserCRUD.create(session, user)
    except UserAlreadyExists:
        raise HTTPException(**UserAlreadyExistsException().dict())
    if settings.emails_enabled and user.email != settings.EMAIL_TEST_USER:
        email_data = generate_new_account_email(
            user.email, user.username, user.password
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    else:
        logger.warning(
            f"User {user.username} created without email. "
            f"Emails are disabled in settings or user has no email."
        )
        raise HTTPException(**EmailsDisabledException(detail=EMAILS_DISABLED).dict())

    return db_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    current_user: CurrentUser,
    user_update: UserUpdateMe,
    session: SessionDep,
) -> Any:
    if user_update.email:
        if await UserCRUD.get_by_email(session, user_update.email):
            raise HTTPException(**UserAlreadyExistsException().dict())
    if user_update.username:
        if await UserCRUD.get_by_username(session, user_update.username):
            raise HTTPException(**UserAlreadyExistsException().dict())
    return await UserCRUD.update(session, current_user, user_update)

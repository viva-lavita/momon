import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.auth.exceptions import UserNotFoundException
from src.auth.service import generate_new_account_email, get_password_hash, verify_password
from src.config import settings
from src.constants import EMAILS_DISABLED
from src.db import SessionDep
from src.exceptions import EmailsDisabledException
from src.models import Message
from src.users import constants, exceptions
from src.users.dependencies import CurrentSuperuser, CurrentUser, get_current_active_superuser, get_current_active_user
from src.users.exceptions import (
    IncorrectPasswordException,
    InvalidPasswordException,
    RoleNotFound,
    RoleNotFoundException,
    UserAlreadyExists,
    UserAlreadyExistsException,
)
from src.users.schemas import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from src.users.service import UserCRUD
from src.utils import send_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UsersPublic,
    dependencies=[Depends(get_current_active_superuser)],  # можно так, а можно через параметры
)
async def get_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,  # current_superuser: CurrentSuperuser вот так
) -> UsersPublic:
    """All users, only for superusers."""
    users = await UserCRUD.get_all(session, skip=skip, limit=limit)
    return UsersPublic(data=[UserPublic(**user.model_dump()) for user in users], count=len(users))


@router.get("/me/", response_model=UserPublic)
async def read_user_me(current_user: Annotated[UserPublic, Depends(get_current_active_user)]) -> Any:
    return current_user


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(get_current_active_superuser)])
async def read_user_by_id(user_id: UUID, session: SessionDep) -> Any:
    """
    Get a specific user by id.
    """
    user = await UserCRUD.get(session, "id", user_id)
    if not user:
        raise HTTPException(**UserNotFoundException().dict())
    return user


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep) -> Any:
    """
    Create new user only for superusers.

    role_id is not required, set to user by default.
    """
    try:
        db_user = await UserCRUD.create(session, user)
    except UserAlreadyExists:
        raise HTTPException(**UserAlreadyExistsException().dict())
    except RoleNotFound:
        raise HTTPException(**RoleNotFoundException().dict())
    if settings.emails_enabled and user.email != settings.EMAIL_TEST_USER:
        email_data = generate_new_account_email(user.email, user.username, user.password)
        send_email(email_to=user.email, subject=email_data.subject, html_content=email_data.html_content)
    else:
        logger.warning(
            f"User {user.username} created without email. Emails are disabled in settings or user has no email."
        )
        raise HTTPException(**EmailsDisabledException(detail=EMAILS_DISABLED).dict())

    return db_user


@router.post("/signup", response_model=UserPublic)
async def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user.
    """
    try:
        user = await UserCRUD.create(session, user_in)
    except UserAlreadyExists:
        raise HTTPException(**UserAlreadyExistsException().dict())
    return user


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def update_user(session: SessionDep, user_id: UUID, user_in: UserUpdate) -> Any:
    """
    Update a user, only for superusers.
    """
    user = await UserCRUD.get(session, "id", user_id)
    if not user:
        raise HTTPException(**UserNotFoundException().dict())
    try:
        user = await UserCRUD.update(db_user=user, user_in=user_in, session=session)
    except UserAlreadyExists:
        raise HTTPException(**UserAlreadyExistsException().dict())
    except RoleNotFound:
        raise HTTPException(**RoleNotFoundException().dict())
    return user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(current_user: CurrentUser, user_update: UserUpdateMe, session: SessionDep) -> Any:
    try:
        user = await UserCRUD.update(db_user=current_user, user_in=user_update, session=session)
    except UserAlreadyExists:
        raise HTTPException(**UserAlreadyExistsException().dict())
    except RoleNotFound:
        raise HTTPException(**RoleNotFoundException().dict())
    return user


@router.patch("/me/password", response_model=Message)
async def update_password_me(session: SessionDep, body: UpdatePassword, current_user: CurrentUser) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(**InvalidPasswordException().dict())
    if body.current_password == body.new_password:
        raise HTTPException(**IncorrectPasswordException().dict())

    hashed_password = get_password_hash(password=body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    await session.commit()
    return Message(message=constants.PASSWORD_UPDATED_SUCCESSFULLY)


@router.delete("/me", response_model=Message)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    if current_user.is_superuser:
        raise HTTPException(**exceptions.SuperuserDeleteException().dict())
    await UserCRUD.delete(session, current_user.id)
    return Message(constants.USER_DELETED_SUCCESSFULLY)


@router.delete("/{user_id}", response_model=Message)
async def delete_user(session: SessionDep, user_id: UUID, current_superuser: CurrentSuperuser) -> Any:
    """Delete a user, only for superusers."""
    user = await UserCRUD.get(session, "id", user_id)
    if not user:
        raise HTTPException(**UserNotFoundException().dict())
    if current_superuser.id == user_id:
        raise HTTPException(**exceptions.SuperuserDeleteException().dict())
    await UserCRUD.delete(session, user_id)
    return Message(message=constants.USER_DELETED_SUCCESSFULLY)

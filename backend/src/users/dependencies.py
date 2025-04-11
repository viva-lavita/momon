from typing import Annotated
from fastapi import Depends, HTTPException, status
import jwt

from src.auth.dependencies import TokenDep
from src.auth.schemas import TokenData
from src.db import SessionDep
from src.config import settings
from src.auth.exceptions import NotValidCredentialsException
from src.users.models import User
from src.users.schemas import UserPublic
from src.users import constants
from src.users.service import get_user


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(**NotValidCredentialsException().dict())
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = await get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserPublic:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=constants.INACTIVE_USER
        )
    return UserPublic(**current_user.model_dump())


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

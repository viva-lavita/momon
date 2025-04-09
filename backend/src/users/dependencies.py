from typing import Annotated
from fastapi import Depends, HTTPException, status
import jwt

from src.auth.constants import NotValidCredentials, TokenDep
from src.auth.schemas import TokenData
from src.db import SessionDep
from src.config import settings
from src.users.models import User
from src.users.schemas import UserInDB, UserPublic
from src.users.service import UserCRUD


async def get_user(session: SessionDep, username: str) -> UserInDB:
    user = await UserCRUD.get_by_username(session, username)
    if user:
        return UserInDB(**user.model_dump())


async def get_current_user(session: SessionDep, token: TokenDep) -> UserPublic:
    credentials_exception = HTTPException(
        status_code=NotValidCredentials.status_code,
        detail=NotValidCredentials.detail,
        headers=NotValidCredentials.headers,
    )
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
    return UserPublic(**user.model_dump())


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserPublic:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return UserPublic(**current_user.model_dump())

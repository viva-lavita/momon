from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
import jwt
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.schemas import TokenData
from src.config import settings
from src.auth.constants import NotValidCredentials, TokenDep, pwd_context
from src.users.models import User
from src.users.schemas import UserInDB, UserPublic
from src.users.service import UserCRUD


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str) -> UserInDB:
    user = await UserCRUD.get_by_username(session, username)
    if user:
        return UserInDB(**user.model_dump())


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> UserPublic:
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserPublic(**user.model_dump())


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(session: AsyncSession, token: TokenDep) -> UserPublic:
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

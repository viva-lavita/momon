from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException

from src.auth import exceptions
from src.auth.dependencies import TokenDep
from src.db import SessionDep
from src.auth.utils import create_access_token
from src.config import settings
from src.auth.schemas import Token
from src.auth.dependencies import authenticate_user
from src.users.dependencies import CurrentUser
from src.users.schemas import UserPublic


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token", response_model=Token)
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(**exceptions.IncorrectUsernameOrPasswordException().dict())
    if not user.is_active:
        raise HTTPException(**exceptions.InactiveUserException().dict())
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser, token: TokenDep) -> Any:
    return current_user

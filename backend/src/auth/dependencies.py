from typing import Annotated

from fastapi import Depends

from src.auth.constants import JWTBearer
from src.auth.service import verify_password
from src.db import SessionDep
from src.users.models import User
from src.users.service import get_user


async def authenticate_user(session: SessionDep, username: str, password: str) -> User:
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


oauth2_scheme = JWTBearer(tokenUrl="/auth/access-token")
TokenDep = Annotated[str, Depends(oauth2_scheme)]

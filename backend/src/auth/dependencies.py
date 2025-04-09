from src.auth.service import verify_password
from src.db import SessionDep
from src.users.dependencies import get_user
from src.users.schemas import UserPublic


async def authenticate_user(
    session: SessionDep, username: str, password: str
) -> UserPublic:
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserPublic(**user.model_dump())

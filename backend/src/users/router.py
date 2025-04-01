from fastapi import APIRouter

from src.db import SessionDep
from src.users.schemas import UserPublic
from src.users.service import UserCRUD


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(session: SessionDep) -> list[UserPublic]:
    return await UserCRUD.get_all(session)

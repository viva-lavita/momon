from typing import Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.utils import get_password_hash
from src.models import get_by_name, get_list
from src.users.models import User, UserCRUDModel
from src.users.schemas import UserCreate, UserUpdate


class UserCRUD:
    crud = UserCRUDModel

    @classmethod
    async def create(cls, session: AsyncSession, user_create: UserCreate) -> User:
        db_obj = await User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @classmethod
    async def update_user(
        *, session: AsyncSession, db_user: User, user_in: UserUpdate
    ) -> Any:
        user_data = user_in.model_dump(
            exclude_unset=True
        )  # исключаем поля, которых нет в схеме
        extra_data = {}
        if "password" in user_data:  # хэшируем пароль
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        await db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @classmethod
    async def get(cls, session: AsyncSession, user_id: str) -> User:
        return await cls.crud.get(session, "id", user_id)

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str) -> User:
        return await get_by_name(session, User, name)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[User]:
        return await get_list(session, select(User))

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: str) -> None:
        await cls.crud.delete(session, "id", user_id)

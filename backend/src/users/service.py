import logging
from typing import Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.auth.utils import get_password_hash
from src.db import SessionDep
from src.models import get_list
from src.users.constants import UserRolesEnum
from src.users.exceptions import UserAlreadyExists
from src.users.models import Role, User, UserCRUDModel, RoleCRUDModel
from src.users.schemas import RoleCreate, RoleBase, UserCreate, UserUpdateMe


logger = logging.getLogger(__name__)


class UserCRUD:
    crud = UserCRUDModel

    @classmethod
    async def create(cls, session: AsyncSession, user_create: UserCreate) -> User:
        if await cls.crud.get(session, "email", user_create.email):
            raise UserAlreadyExists(
                f"User with email {user_create.email} already exists"
            )
        if await cls.crud.get(session, "username", user_create.username):
            raise UserAlreadyExists(
                f"User with username {user_create.username} already exists"
            )
        if user_create.role_id is None:
            user_create.role_id = (
                await RoleCRUD.get(session, "name", UserRolesEnum.user.name)
            ).id
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @classmethod
    async def update(
        session: AsyncSession, db_user: User, user_in: UserUpdateMe
    ) -> Any:
        user_data = user_in.model_dump(
            exclude_unset=True
        )  # исключаем поля, которых нет в схеме
        extra_data = {}
        if "password" in user_data:  # хэшируем пароль
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @classmethod
    async def get(cls, session: AsyncSession, field: str, value: Any) -> User:
        return await cls.crud.get(session, field, value)

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str) -> User:
        return await cls.crud.get(session, "username", username)  # уникальное поле

    @classmethod
    async def get_all(
        cls, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        return await get_list(
            session, select(User).where(User.is_active).offset(skip).limit(limit)
        )

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> User:
        return await cls.crud.get(session, "email", email)

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: str) -> None:
        await cls.crud.delete(session, "id", user_id)


class RoleCRUD:
    crud = RoleCRUDModel

    @classmethod
    async def get(cls, session: AsyncSession, field: str, value: Any) -> User:
        return await cls.crud.get(session, field, value)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[User]:
        return await get_list(session, select(Role))

    @classmethod
    async def delete(cls, session: AsyncSession, role_id: str) -> None:
        await cls.crud.delete(session, "id", role_id)

    @classmethod
    async def get_or_create(
        cls, session: AsyncSession, role_create: RoleCreate
    ) -> RoleBase:
        role = await cls.crud.get(session, "name", role_create.name)
        if role:
            return role
        return await cls.crud.create(session, **role_create.model_dump())


async def create_superuser(session: AsyncSession):  # наглядно get_or_create и create
    role_user = await RoleCRUD.get_or_create(
        session, RoleCreate(name=UserRolesEnum.user)
    )
    logger.info(f"User role created: {role_user}")
    role_admin = await RoleCRUD.get_or_create(
        session, RoleCreate(name=UserRolesEnum.admin)
    )
    logger.info(f"Admin role created: {role_admin}")
    try:
        user = await UserCRUD.create(
            session,
            UserCreate(
                username=settings.FIRST_SUPERUSER,
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                role_id=role_admin.id,
                is_superuser=True,
            ),
        )
        logger.info(f"Superuser created: {user}")
    except UserAlreadyExists:
        logger.info("Superuser already exists")
        pass


async def get_user(session: SessionDep, username: str) -> User:
    user = await UserCRUD.get_by_username(session, username)
    if user:
        return user

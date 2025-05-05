import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.auth.service import get_password_hash
from src.config import settings
from src.db import SessionDep
from src.models import get_list
from src.users.constants import UserRolesEnum
from src.users.exceptions import RoleNotFound, UserAlreadyExists
from src.users.models import Role, RoleCRUDModel, User, UserCRUDModel
from src.users.schemas import RoleBase, RoleCreate, UserCreate, UserRegister, UserUpdate, UserUpdateMe

logger = logging.getLogger(__name__)


class UserCRUD:
    crud = UserCRUDModel

    @classmethod
    async def get_test(cls, field: str, value: Any) -> User:
        return await cls.crud.get_test(field, value)

    @classmethod
    async def create(cls, session: AsyncSession, user_create: UserCreate | UserRegister) -> User:
        if await cls.crud.get(session, "email", user_create.email):
            raise UserAlreadyExists(
                f"User with email {user_create.email} already exists"  # TODO: залогировать все подобные?
            )
        if await cls.crud.get(session, "username", user_create.username):
            raise UserAlreadyExists(f"User with username {user_create.username} already exists")
        if getattr(user_create, "role_id", None) is None:
            user_create = UserCreate.model_validate(user_create, update={"role_id": None})
        if user_create.role_id is not None:
            if await RoleCRUD.get(session, "id", user_create.role_id) is None:
                raise RoleNotFound(f"Role with id {user_create.role_id} not found")
        if user_create.role_id is None:
            user_create.role_id = (await RoleCRUD.get(session, "name", UserRolesEnum.user.name)).id
        db_obj = User.model_validate(user_create, update={"hashed_password": get_password_hash(user_create.password)})
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @classmethod
    async def update(cls, db_user: User, user_in: UserUpdateMe | UserUpdate, session: AsyncSession) -> Any:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:  # хэшируем пароль
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        if "role_id" in user_data and user_data["role_id"] != db_user.role_id:
            role = await RoleCRUD.get(session, "id", user_data["role_id"])
            if role is None:
                raise RoleNotFound(f"Role with id {user_data['role_id']} not found")
            extra_data["role_id"] = user_data["role_id"]
        if "email" in user_data and user_data["email"] != db_user.email:
            if await cls.crud.get(session, "email", user_data["email"]):
                raise UserAlreadyExists(f"User with email {user_data['email']} already exists")
            extra_data["email"] = user_data["email"]
        if "username" in user_data and user_data["username"] != db_user.username:
            if await cls.crud.get(session, "username", user_data["username"]):
                raise UserAlreadyExists(f"User with username {user_data['username']} already exists")
            extra_data["username"] = user_data["username"]
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
    async def get_all(cls, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        return await get_list(session, select(User).where(User.is_active).offset(skip).limit(limit))

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> User:
        return await cls.crud.get(session, "email", email)

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: str) -> None:
        await cls.crud.delete(session, "id", user_id)


class RoleCRUD:
    crud = RoleCRUDModel

    @classmethod
    async def get(cls, session: AsyncSession, field: str, value: Any) -> User | None:
        return await cls.crud.get(session, field, value)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[User]:
        return await get_list(session, select(Role))

    @classmethod
    async def delete(cls, session: AsyncSession, role_id: str) -> None:
        await cls.crud.delete(session, "id", role_id)

    @classmethod
    async def get_or_create(cls, session: AsyncSession, role_create: RoleCreate) -> RoleBase | tuple[RoleBase, bool]:
        role = await cls.crud.get(session, "name", role_create.name)
        if role:
            return role, False
        return (await cls.crud.create(session, **role_create.model_dump()), True)


async def create_superuser(session: AsyncSession):  # наглядно get_or_create и create
    role_user, created = await RoleCRUD.get_or_create(session, RoleCreate(name=UserRolesEnum.user))
    if created:
        logger.info(f"User role created: {role_user}")
    role_admin, created = await RoleCRUD.get_or_create(session, RoleCreate(name=UserRolesEnum.admin))
    if created:
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

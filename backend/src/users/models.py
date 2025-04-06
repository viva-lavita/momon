import uuid

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, SQLModel, Relationship

from src.models import CRUDBase
from src.users.schemas import UserBase
from src.users.constants import UserRolesEnum


class User(UserBase, AsyncAttrs, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    role_id: uuid.UUID = Field(
        foreign_key="role.id", nullable=False, ondelete="PROTECT"
    )
    role: "Role" = Relationship(back_populates="users")
    # items: list["Item"] = Relationship(  # пример реляции
    #     back_populates="owner",
    #     cascade_delete=True
    # )


# class Item(ItemBase, table=True):
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  # пример реляции
#     owner_id: uuid.UUID = Field(
#         foreign_key="user.id", nullable=False, ondelete="CASCADE"
#     )
#     owner: User | None = Relationship(back_populates="items")


class UserCRUDModel(CRUDBase):
    table = User


class Role(SQLModel, AsyncAttrs, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: UserRolesEnum
    users: list[User] | None = Relationship(back_populates="role")


class RoleCRUDModel(CRUDBase):
    table = Role

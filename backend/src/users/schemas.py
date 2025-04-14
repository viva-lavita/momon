import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserInDB(UserBase):
    id: uuid.UUID
    hashed_password: str


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role_id: uuid.UUID | None = Field(foreign_key="role.id", default=None)


class UserRegister(SQLModel):
    username: str = Field(unique=True, index=True, max_length=255)
    email: EmailStr = Field(max_length=255, unique=True)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# При обновлении, все не обязательны
class UserUpdate(UserBase):
    username: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)
    role_id: uuid.UUID | None = Field(foreign_key="role.id", default=None)


class UserUpdateMe(SQLModel):
    username: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# Свойство, дополнение - id всегда обязателен
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class RoleBase(SQLModel):
    id: uuid.UUID
    name: str


class RoleInDB(RoleBase):
    users: list[UserPublic]


class RoleCreate(SQLModel):
    name: str

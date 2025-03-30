import uuid

from sqlmodel import Field
# from sqlmodel import Relationship

from src.models import CRUDBase
from src.users.schemas import UserBase


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    # items: list["Item"] = Relationship(  # пример реляции
    #     back_populates="owner",
    #     cascade_delete=True
    # )


class UserCRUDModel(CRUDBase):
    table = User

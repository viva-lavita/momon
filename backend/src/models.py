from typing import Any, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlmodel import SQLModel, delete, func, select, update

from src.db import connection

Table = TypeVar("Table", bound=SQLModel)


class CRUDBase:
    table: type[Table]

    # @classmethod
    # @connection
    # async def get_test(cls, field: str, value: Any, session: AsyncSession = None) -> Table | None:
    #     """Тестирование с session переданной только на уровне репозитория."""
    #     return (
    #         (await session.execute(select(cls.table).where(getattr(cls.table, field) == value)))
    #         .unique()
    #         .scalars()
    #         .one()
    #     )

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Table:
        created_fields = {k: v for k, v in kwargs.items() if getattr(cls.table, k, None) is not None}
        instance = cls.table(**created_fields)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def get(cls, session: AsyncSession, field: str, value: Any) -> Table | None:
        query = select(cls.table).where(getattr(cls.table, field) == value)
        return await exactly_one(session, query)

    @classmethod
    async def update(cls, session: AsyncSession, field: str, value: Any, **kwargs) -> None:
        updated_fields = {k: v for k, v in kwargs.items() if getattr(cls.table, k, None) is not None}
        query = update(cls.table).where(getattr(cls.table, field) == value).values(**updated_fields)
        await session.execute(query)
        await session.commit()

    @classmethod
    async def delete(cls, session: AsyncSession, field: str, value: Any) -> None:
        query = delete(cls.table).where(getattr(cls.table, field) == value)
        await session.execute(query)
        await session.commit()


async def get_list(session: AsyncSession, query: Select) -> list[Table]:
    return (await session.execute(query)).unique().scalars().all()


async def exactly_one(session: AsyncSession, query) -> Table | None:
    try:
        return (await session.execute(query)).unique().scalars().one()
    except NoResultFound:
        return None


async def get_total_rows(session: AsyncSession, query: Select) -> int:
    return (await session.execute(select(func.count()).select_from(query.subquery()))).scalars().one()


# Generic message
class Message(SQLModel):
    message: str


@connection
async def get_test_list(query: Select, session: AsyncSession = None) -> list[Table]:
    return (await session.execute(query)).unique().scalars().all()

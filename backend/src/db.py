# TODO: Допиши в функцию init_db создание суперюзера после создания моделей юзера

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings


engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=settings.POSTGRES_ECHO,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


async def init_db(session: AsyncSession):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # сюда добавить создание суперюзера


async def get_session() -> AsyncGenerator[AsyncSession, None, None]:
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

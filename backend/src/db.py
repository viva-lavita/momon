# TODO: Допиши в функцию init_db создание суперюзера после создания моделей юзера

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


# class BaseTable(SQLModel, # идея была хорошая, но споткнулась на переиспользование схем в моделях таблиц
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     created_at: datetime = Field(server_default=func.now())
#     updated_at: datetime = Field(server_default=func.now(), onupdate=func.now())

#     @declared_attr.directive
#     def __tablename__(cls) -> str:
#         """Generate table name from class name. Model User -> tablename users"""
#         return cls.__name__.lower() + 's'


def connection(method):
    """
    Декоратор для создания сессии и обработки исключений

    :param method: функция, которую нужно обернуть
    :return: обернутая функция

    Пример использования:
    @connection
    async def get_users(session):
        return await session.execute(select(User))
    """

    async def wrapper(*args, **kwargs):
        async with async_sessionmaker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper

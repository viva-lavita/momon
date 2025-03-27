# Создай движок и функцию init_db, которая создает бд и суперюзера


from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings


engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=settings.POSTGRES_ECHO,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

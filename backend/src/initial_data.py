# Создание начальных данных, запуск из скрипта
import asyncio
import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    # async for session in get_session(): # Как вариант
    async with AsyncSession(engine) as session:
        await init_db(session)


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()

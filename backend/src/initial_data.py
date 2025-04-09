# Создание начальных данных, запуск из скрипта
import asyncio
import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import engine, init_db
from src.users.service import create_superuser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        await init_db(session)
        await create_superuser(session)


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()

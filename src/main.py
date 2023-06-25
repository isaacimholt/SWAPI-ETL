import asyncio
import logging

from etl.extract import extract
from settings import Settings

logger = logging.getLogger(__name__)


async def etl(settings: Settings):
    async for person in extract(settings=settings):
        print(person)


if __name__ == "__main__":
    _settings = Settings()
    asyncio.run(
        etl(
            settings=_settings,
        )
    )

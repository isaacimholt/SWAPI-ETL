import asyncio
import logging

from etl.extract import extract
from etl.transform import transform
from settings import Settings

logger = logging.getLogger(__name__)


async def etl(settings: Settings):
    people = extract(settings=settings)
    people = await transform(people=people, settings=settings)
    print(people)


if __name__ == "__main__":
    _settings = Settings()
    asyncio.run(
        etl(
            settings=_settings,
        )
    )

import asyncio
import logging

from etl.extract import extract
from etl.transform import transform
from settings import Settings

logger = logging.getLogger(__name__)


async def etl(settings: Settings):
    people_aiter = extract(settings=settings)
    people_df = await transform(people=people_aiter, settings=settings)
    print(people_df)


if __name__ == "__main__":
    _settings = Settings()
    asyncio.run(etl(settings=_settings))

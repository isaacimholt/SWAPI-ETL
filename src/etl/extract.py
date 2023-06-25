import asyncio
import logging
from math import ceil
from os import path
from typing import AsyncIterator

import aiohttp
from tqdm import tqdm

from etl.utils import _init_get_entity
from models import Person, PersonPage
from settings import Settings

logger = logging.getLogger(__name__)


async def extract(settings: Settings) -> AsyncIterator[Person]:
    get_person_page = _init_get_entity(settings=settings, entity_model=PersonPage)
    connector = aiohttp.TCPConnector(limit=settings.max_simultaneous_requests)
    client_session = aiohttp.ClientSession(connector=connector, raise_for_status=True)
    async with client_session as client:

        person_page = await get_person_page(client, path.join(settings.api_url_base, "people"))
        for person in person_page.results:
            yield person

        num_pages = ceil(person_page.count / settings.api_max_page_results)
        if num_pages <= 1:
            return

        # todo: use url query constructor
        urls = [path.join(settings.api_url_base, f"people/?page={i}") for i in range(2, num_pages + 1)]
        tasks = [get_person_page(client, url) for url in urls]
        tasks = tqdm(asyncio.as_completed(tasks), total=num_pages - 1)
        for task in tasks:
            # we might normally catch exceptions here
            person_page = await task
            for person in person_page.results:
                yield person



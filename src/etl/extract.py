import asyncio
import logging
from math import ceil
from os import path
from typing import AsyncIterator, Callable, Awaitable

import aiohttp
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, wait_random_exponential, stop_after_attempt, before_sleep_log
from tqdm import tqdm

from _types import M
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


def _init_get_entity(settings: Settings, entity_model: M) -> Callable[[aiohttp.ClientSession, str], Awaitable[M]]:
    """Wrapper function to init getter function with retry settings for getting entities."""

    @retry(
        retry=retry_if_exception_type(aiohttp.ClientError),
        wait=wait_random_exponential(multiplier=1, max=3),
        stop=stop_after_attempt(settings.max_request_retries),
        before_sleep=before_sleep_log(logger, logging.WARNING),  # log when we retry
    )
    async def get_entity(client: aiohttp.ClientSession, url: str) -> PersonPage:
        """Gets an entity with some retry logic."""
        async with client.get(url) as resp:
            _json = await resp.json()
            try:
                return entity_model(**_json)
            except (ValidationError, TypeError):
                # we want to see the data that failed validation, but we also want to raise error
                logger.error(f"\nCannot load json:\n{_json}")
                raise

    return get_entity

import asyncio
import logging
from math import ceil
from typing import AsyncIterator, Callable, Awaitable

import aiohttp
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, wait_random_exponential, stop_after_attempt, before_sleep_log
from tqdm import tqdm

from models import Person, PersonPage
from settings import Settings

logger = logging.getLogger(__name__)


async def extract(settings: Settings) -> AsyncIterator[Person]:
    get_person_page = _init_get_person_page(settings=settings)
    connector = aiohttp.TCPConnector(limit=settings.max_simultaneous_requests)
    client_session = aiohttp.ClientSession(connector=connector, raise_for_status=True)
    async with client_session as client:
        # todo: use path join
        person_page = await get_person_page(client, settings.api_url_base + "people")
        for person in person_page.results:
            yield person

        num_pages = ceil(person_page.count / settings.api_max_page_results)
        if num_pages <= 1:
            return

        # todo: use path join
        # todo: use url query constructor
        urls = [settings.api_url_base + f"people/?page={i}" for i in range(2, num_pages + 1)]
        tasks = [get_person_page(client, url) for url in urls]
        tasks = tqdm(asyncio.as_completed(tasks), total=num_pages - 1)
        for task in tasks:
            # we might normally catch exceptions here
            person_page = await task
            for person in person_page.results:
                yield person


def _init_get_person_page(settings: Settings) -> Callable[[aiohttp.ClientSession, str], Awaitable[PersonPage]]:
    """Wrapper function to init getter function with retry settings for getting person pages."""

    @retry(
        retry=retry_if_exception_type(aiohttp.ClientError),
        wait=wait_random_exponential(multiplier=1, max=3),
        stop=stop_after_attempt(settings.max_request_retries),
        before_sleep=before_sleep_log(logger, logging.WARNING),  # log when we retry
    )
    async def get_person_page(client: aiohttp.ClientSession, url: str) -> PersonPage:
        """Gets a person page with some retry logic."""
        async with client.get(url) as resp:
            _json = await resp.json()
            try:
                return PersonPage(**_json)
            except (ValidationError, TypeError):
                logger.error(f"\nCannot load json:\n{_json}")
                raise

    return get_person_page

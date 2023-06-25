import logging
from typing import Callable, Awaitable

import aiohttp
from async_lru import alru_cache
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, wait_random_exponential, stop_after_attempt, before_sleep_log

from _types import M
from models import PersonPage
from settings import Settings

logger = logging.getLogger(__name__)


def _init_get_entity(settings: Settings, entity_model: M) -> Callable[[aiohttp.ClientSession, str], Awaitable[M]]:
    """Wrapper function to init getter function with retry settings for getting entities."""

    @alru_cache()
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

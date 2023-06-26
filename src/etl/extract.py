import asyncio
import logging
from math import ceil
from os import path
from typing import AsyncIterator

import aiohttp
from tqdm import tqdm

from etl.utils import _init_get_entity
from models import APIPersonPage, Person, APISpecies, Species
from settings import Settings

logger = logging.getLogger(__name__)


async def extract(settings: Settings) -> AsyncIterator[Person]:
    # set up getters for various page types
    get_person_page = _init_get_entity(settings=settings, entity_model=APIPersonPage)
    get_species_page = _init_get_entity(settings=settings, entity_model=APISpecies)

    # set up aiohttp client session
    connector = aiohttp.TCPConnector(limit=settings.max_simultaneous_requests)
    client_session = aiohttp.ClientSession(connector=connector, raise_for_status=True)

    async with client_session as client:

        # get 1st page which has total count of objects
        person_page = await get_person_page(client, path.join(settings.api_url_base, "people"))
        for api_person in person_page.results:
            # create Person objects from api data, enrich with species api data
            api_species_coros = [get_species_page(client, url) for url in api_person.species]
            api_species: list[APISpecies] = await asyncio.gather(*api_species_coros)
            yield Person.from_api_person(api_person=api_person, species=[Species(name=s.name) for s in api_species])

        # calculate how many pages remain
        num_pages = ceil(person_page.count / settings.api_max_page_results)
        if num_pages <= 1:
            return

        # get remaining pages
        urls = [path.join(settings.api_url_base, f"people/?page={i}") for i in range(2, num_pages + 1)]
        tasks = [get_person_page(client, url) for url in urls]
        tasks = tqdm(asyncio.as_completed(tasks), total=num_pages - 1)

        for task in tasks:
            # we might normally catch exceptions here
            person_page = await task
            for api_person in person_page.results:
                # create Person objects from api data, enrich with species api data
                api_species_coros = [get_species_page(client, url) for url in api_person.species]
                api_species: list[APISpecies] = await asyncio.gather(*api_species_coros)
                yield Person.from_api_person(api_person=api_person, species=[Species(name=s.name) for s in api_species])

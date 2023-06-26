import heapq
from operator import attrgetter
from typing import AsyncIterator

import pandas as pd
from pandas import DataFrame

from models import PersonComparator, CSVCOL, Person
from settings import Settings


async def transform(people: AsyncIterator[Person], settings: Settings) -> DataFrame:
    people = await filter_and_sort(people=people, settings=settings)
    return to_df(people)


async def filter_and_sort(people: AsyncIterator[Person], settings: Settings) -> list[Person]:
    # 1. Handle "large" datasets with heap queue
    # 2. Ignore people that do not have a numeric height
    # 3. Configurable number of max people to consider
    # this function is overkill for the current data source (max 100 results from api)
    # but wanted to demonstrate handling much larger data streams in memory-efficient way

    # had some difficulty here, wanted to use a heapq.nlargest solution to handle "large" streaming data
    # but heapq.nlargest handles only iter protocol and not async aiter, so had to do n-largest filter "by hand"
    # most_films = heapq.nlargest(settings.max_person_filter, people, lambda p: len(p.films) and p.height is not None)

    most_films_heap: list[PersonComparator] = []
    async for person in people:

        # skip non-numeric heights
        if person.height is None:
            continue

        # create a comparison wrapper with person & key
        person_with_key = PersonComparator(key=len(person.films), person=person)

        # push heap & handle max number of items
        if len(most_films_heap) < settings.max_person_filter:
            heapq.heappush(most_films_heap, person_with_key)
        else:
            heapq.heappushpop(most_films_heap, person_with_key)

    # unwrap PersonComparator
    most_films: list[Person] = [comparator.person for comparator in most_films_heap]

    return sorted(most_films, key=attrgetter("height"), reverse=True)


def to_df(people: list[Person]) -> DataFrame:
    data = [
        {
            CSVCOL.NAME:        p.name,
            CSVCOL.SPECIES:     ", ".join(s.name for s in p.species),
            CSVCOL.HEIGHT:      p.height,
            CSVCOL.APPEARANCES: len(p.films),
        }
        for p in people
    ]
    return pd.DataFrame.from_records(data, index=CSVCOL.NAME)

from unittest.mock import patch, Mock

import aiohttp
import pydantic
import pytest
import tenacity

from etl.extract import extract
from settings import Settings


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get', autospec=True)
async def test_extract_client_error_raises_retry_error(mock_get):
    mock_get.side_effect = Mock(side_effect=aiohttp.ClientError)

    with pytest.raises(tenacity.RetryError):
        results = [_ async for _ in extract(settings=Settings(max_request_retries=0))]


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get', autospec=True)
async def test_extract_validation_error(mock_get):
    mock_get.return_value.__aenter__.return_value.json.return_value = {"wrong_key": None}

    with pytest.raises(pydantic.ValidationError):
        results = [_ async for _ in extract(settings=Settings(max_request_retries=0))]


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get', autospec=True)
async def test_extract_one_result(mock_get):
    api_person_dict = {
        "name":       "C-3PO",
        "height":     "167",
        "mass":       "75",
        "hair_color": "n/a",
        "skin_color": "gold",
        "eye_color":  "yellow",
        "birth_year": "112BBY",
        "gender":     "n/a",
        "homeworld":  "https://swapi.dev/api/planets/1/",
        "films":      [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/2/",
            "https://swapi.dev/api/films/3/",
            "https://swapi.dev/api/films/4/",
            "https://swapi.dev/api/films/5/",
            "https://swapi.dev/api/films/6/"
        ],
        "species":    [
            "https://swapi.dev/api/species/2/"
        ],
        "vehicles":   [],
        "starships":  [],
        "created":    "2014-12-10T15:10:51.357000Z",
        "edited":     "2014-12-20T21:17:50.309000Z",
        "url":        "https://swapi.dev/api/people/2/"
    }

    api_people_page_1_dict = {
        "count":    20,
        "next":     "https://swapi.dev/api/people/?page=2",
        "previous": None,
        "results":  [api_person_dict for _ in range(10)],
    }

    api_people_page_2_dict = {
        "count":    20,
        "next":     None,
        "previous": "https://swapi.dev/api/people/?page=1",
        "results":  [api_person_dict for _ in range(10)],
    }

    api_species_dict = {
        "name":             "Droid",
        "classification":   "artificial",
        "designation":      "sentient",
        "average_height":   "n/a",
        "skin_colors":      "n/a",
        "hair_colors":      "n/a",
        "eye_colors":       "n/a",
        "average_lifespan": "indefinite",
        "homeworld":        None,
        "language":         "n/a",
        "people":           [
            "https://swapi.dev/api/people/2/",
            "https://swapi.dev/api/people/3/",
            "https://swapi.dev/api/people/8/",
            "https://swapi.dev/api/people/23/"
        ],
        "films":            [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/2/",
            "https://swapi.dev/api/films/3/",
            "https://swapi.dev/api/films/4/",
            "https://swapi.dev/api/films/5/",
            "https://swapi.dev/api/films/6/"
        ],
        "created":          "2014-12-10T15:16:16.259000Z",
        "edited":           "2014-12-20T21:36:42.139000Z",
        "url":              "https://swapi.dev/api/species/2/"
    }

    # set up sequence of calls, after a url is requested the first time it is cached
    mock_get.return_value.__aenter__.return_value.json.side_effect = [
        api_people_page_1_dict,
        api_species_dict,
        api_people_page_2_dict,
    ]

    results = [_ async for _ in extract(settings=Settings(max_simultaneous_requests=1))]

    assert len(results) == 20

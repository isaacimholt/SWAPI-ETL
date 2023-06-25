from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum, auto

from pydantic import BaseModel, validator, Field, HttpUrl

from _types import Color
from validators import convert_null, convert_decimal, extract_colors


class Person(BaseModel):
    """Represents a Person object from api/people/"""
    name: str
    height: Decimal | None
    mass: Decimal | None
    hair_colors: list[Color] = Field(..., alias="hair_color")
    skin_colors: list[Color] = Field(..., alias="skin_color")
    eye_colors: list[Color] = Field(..., alias="eye_color")
    birth_year: str | None
    gender: str | None
    homeworld: HttpUrl | None
    films: list[HttpUrl]
    species: list[HttpUrl]
    vehicles: list[HttpUrl]
    starships: list[HttpUrl]
    created: datetime.datetime
    edited: datetime.datetime
    url: HttpUrl

    # validators
    _convert_nulls = validator(
        "height", "mass", "birth_year", "gender", "homeworld", pre=True, allow_reuse=True
    )(convert_null)
    _convert_decimals = validator("height", "mass", pre=True, allow_reuse=True)(convert_decimal)
    _extract_colors = validator("hair_colors", "skin_colors", "eye_colors", pre=True, allow_reuse=True)(extract_colors)


class PersonPage(BaseModel):
    count: int
    next: HttpUrl | None
    previous: HttpUrl | None
    results: list[Person]


@dataclass(order=True)
class PersonComparator:
    """Used for comparison in heap https://docs.python.org/3/library/heapq.html"""
    key: int
    person: Person = field(compare=False)  # compare=False to preserve heap insertion order


class Species(BaseModel):
    name: str
    classification: str
    designation: str
    average_height: Decimal | None
    skin_colors: list[Color]
    hair_colors: list[Color]
    eye_colors: list[Color]
    average_lifespan: Decimal | None
    homeworld: HttpUrl | None
    language: str | None
    people: list[HttpUrl]
    films: list[HttpUrl]
    created: datetime.datetime
    edited: datetime.datetime
    url: HttpUrl

    # validators
    _convert_nulls = validator("language", "homeworld", pre=True, allow_reuse=True)(convert_null)
    _convert_decimals = validator("average_height", "average_lifespan", pre=True, allow_reuse=True)(convert_decimal)
    _extract_colors = validator("hair_colors", "skin_colors", "eye_colors", pre=True, allow_reuse=True)(extract_colors)


class CSVCOL(StrEnum):
    """Columns for CSV export"""
    NAME = auto()
    SPECIES = auto()
    HEIGHT = auto()
    APPEARANCES = auto()

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, NewType

from pydantic import BaseModel, validator, Field, HttpUrl

from utils import is_null

Color = NewType("Color", str)


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

    @validator("height", "mass", "birth_year", "gender", "homeworld", pre=True)
    def convert_null(cls, v) -> Any | None:
        """Convert 'nullable' fields from string to None."""
        if isinstance(v, str) and is_null(v):
            return None
        return v

    @validator("height", "mass", pre=True)
    def convert_decimal(cls, v) -> Any | Decimal | None:
        """Convert 'nullable' fields from string to None."""
        if isinstance(v, str):
            if is_null(v):
                return None
            # remove thousands separator
            return Decimal(v.replace(",", ""))
        return v

    @validator("hair_colors", "skin_colors", "eye_colors", pre=True)
    def extract_colors(cls, v) -> Any | list[Color]:
        """Extract list of colors for various fields."""
        if isinstance(v, str):
            if is_null(v):
                return []
            return [Color(c.strip().lower()) for c in v.split(",")]
        return v


class PersonPage(BaseModel):
    count: int
    next: HttpUrl | None
    previous: HttpUrl | None
    results: list[Person]

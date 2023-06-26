"""For use with Pydantic to normalize & validate data"""
from __future__ import annotations

from decimal import Decimal, DecimalException
from typing import Any

from _types import Color
from utils import is_null


def convert_null(v) -> Any | None:
    """Convert 'nullable' fields from string to None."""
    if isinstance(v, str) and is_null(v):
        return None
    return v


def convert_decimal(v) -> Any | Decimal | None:
    """Convert numeric values to Decimal."""
    if isinstance(v, str):
        if is_null(v):
            return None
        # remove thousands separator
        try:
            return Decimal(v.replace(",", ""))
        except DecimalException:
            return None
    return v


def extract_colors(v) -> Any | list[Color]:
    """Extract list of colors for various fields."""
    if isinstance(v, str):
        if is_null(v):
            return []
        return [Color(c.strip().lower()) for c in v.split(",")]
    return v

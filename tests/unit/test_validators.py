from decimal import Decimal

import pytest

from _types import Color
from validators import convert_null, convert_decimal, extract_colors


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("unknown", None),
        ("N/A", None),
        ("", None),
        (None, None),
    ],
)
def test_convert_null(test_input, expected):
    assert convert_null(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1000", Decimal("1000")),
        ("1,000", Decimal("1000")),
        ("1,000.00", Decimal("1000.00")),
        ("N/A", None),
        ("", None),
        ("foobar", None),
        (None, None),
    ],
)
def test_convert_decimal(test_input, expected):
    assert convert_decimal(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("  blue,  green  ", [Color("blue"), Color("green")]),
        ("  BLUE-Green  ", [Color("blue-green")]),
        ("N/A", []),
        ("", []),
        (None, None),
    ],
)
def test_extract_colors(test_input, expected):
    assert extract_colors(test_input) == expected

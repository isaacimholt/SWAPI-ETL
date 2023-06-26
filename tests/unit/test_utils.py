import pytest

from utils import is_null


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("unknown", True),
        ("N/A", True),
        ("", True),
    ],
)
def test_is_null(test_input, expected):
    assert is_null(test_input) == expected

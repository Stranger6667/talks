import pytest


def twice(value):
    return value * 2


@pytest.mark.parametrize('value, expected', (
    (1, 2),
    (3, 6),
    (4, 8),
))
def test_twice(value, expected):
    assert twice(value) == expected

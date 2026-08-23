import pytest

from domain.roulette_table import (
    column_of,
    dozen_of,
    numbers_in_street,
    street_of,
)


@pytest.mark.parametrize(
    "number,expected",
    [(1, 1), (2, 1), (3, 1), (4, 2), (34, 12), (36, 12)],
)
def test_street_of(number, expected):

    assert street_of(number) == expected


def test_street_of_out_of_range():

    with pytest.raises(ValueError):
        street_of(0)

    with pytest.raises(ValueError):
        street_of(37)


def test_numbers_in_street():

    assert numbers_in_street(1) == (1, 2, 3)
    assert numbers_in_street(12) == (34, 35, 36)


@pytest.mark.parametrize(
    "number,expected",
    [(1, 1), (12, 1), (13, 2), (24, 2), (25, 3), (36, 3), (0, None)],
)
def test_dozen_of(number, expected):

    assert dozen_of(number) == expected


@pytest.mark.parametrize(
    "number,expected",
    [(1, 1), (4, 1), (2, 2), (5, 2), (3, 3), (36, 3), (0, None)],
)
def test_column_of(number, expected):

    assert column_of(number) == expected

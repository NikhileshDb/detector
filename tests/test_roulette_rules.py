import pytest

from domain.roulette_result import RouletteColor
from domain.roulette_rules import expected_color


def test_zero_and_double_zero_are_green():

    assert expected_color("0") == RouletteColor.GREEN
    assert expected_color("00") == RouletteColor.GREEN


def test_known_red_number():

    assert expected_color("1") == RouletteColor.RED


def test_known_black_number():

    assert expected_color("2") == RouletteColor.BLACK


def test_invalid_number_raises():

    with pytest.raises(ValueError):
        expected_color("37")

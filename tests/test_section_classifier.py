import pytest

from analytics.sections.section_classifier import (
    ORPHELINS_NUMBERS,
    SECTION_NUMBERS,
    TIERS_NUMBERS,
    VOISINS_NUMBERS,
    ZERO_NUMBERS,
    RouletteSection,
    get_section,
)


def test_section_sizes_and_partition():
    assert len(ZERO_NUMBERS) == 7
    assert len(VOISINS_NUMBERS) == 10
    assert len(TIERS_NUMBERS) == 12
    assert len(ORPHELINS_NUMBERS) == 8
    assert set().union(*SECTION_NUMBERS.values()) == set(range(37))
    for left in SECTION_NUMBERS.values():
        for right in SECTION_NUMBERS.values():
            if left is not right:
                assert left.isdisjoint(right)


@pytest.mark.parametrize("number", range(37))
def test_every_european_number_classifies_once(number):
    matches = [section for section, numbers in SECTION_NUMBERS.items() if number in numbers]
    assert len(matches) == 1
    assert get_section(number) == matches[0]


@pytest.mark.parametrize("number", [0, 3, 12, 15, 35])
def test_zero_priority_numbers_are_zero_section(number):
    assert get_section(number) is RouletteSection.ZERO


@pytest.mark.parametrize(
    ("number", "section"),
    [(23, RouletteSection.TIERS), (7, RouletteSection.VOISINS), (17, RouletteSection.ORPHELINS)],
)
def test_examples(number, section):
    assert get_section(number) is section


@pytest.mark.parametrize("number", [-1, 37, "37", "abc", True, False, "1.0"])
def test_invalid_numbers_are_rejected(number):
    with pytest.raises(ValueError):
        get_section(number)

from enum import Enum


class RouletteSection(str, Enum):
    ZERO = "ZERO"
    VOISINS = "VOISINS"
    TIERS = "TIERS"
    ORPHELINS = "ORPHELINS"


ZERO_NUMBERS = frozenset({12, 35, 3, 26, 0, 32, 15})
VOISINS_NUMBERS = frozenset({22, 18, 29, 7, 28, 19, 4, 21, 2, 25})
TIERS_NUMBERS = frozenset({27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33})
ORPHELINS_NUMBERS = frozenset({1, 20, 14, 31, 9, 17, 34, 6})

SECTION_NUMBERS = {
    RouletteSection.ZERO: ZERO_NUMBERS,
    RouletteSection.VOISINS: VOISINS_NUMBERS,
    RouletteSection.TIERS: TIERS_NUMBERS,
    RouletteSection.ORPHELINS: ORPHELINS_NUMBERS,
}

SECTION_CODES = {
    RouletteSection.ZERO: "Z",
    RouletteSection.VOISINS: "V",
    RouletteSection.TIERS: "T",
    RouletteSection.ORPHELINS: "O",
}


def _parse_number(number: int | str) -> int:
    if isinstance(number, bool):
        raise ValueError("Roulette number must be an integer from 0 to 36.")
    try:
        parsed = int(number)
    except (TypeError, ValueError) as exc:
        raise ValueError("Roulette number must be an integer from 0 to 36.") from exc
    if parsed < 0 or parsed > 36 or (isinstance(number, str) and str(parsed) != number.strip()):
        raise ValueError("Roulette number must be an integer from 0 to 36.")
    return parsed


def get_section(number: int | str) -> RouletteSection:
    parsed = _parse_number(number)
    for section, numbers in SECTION_NUMBERS.items():
        if parsed in numbers:
            return section
    raise AssertionError(f"Unclassified European roulette number: {parsed}")

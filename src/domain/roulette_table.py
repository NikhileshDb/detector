STREET_COUNT = 12
NUMBERS_PER_STREET = 3


def street_of(number: int) -> int:

    if number < 1 or number > 36:
        raise ValueError(
            f"Number {number} has no street (only 1-36)."
        )

    return ((number - 1) // NUMBERS_PER_STREET) + 1


def numbers_in_street(street: int) -> tuple[int, int, int]:

    if street < 1 or street > STREET_COUNT:
        raise ValueError(
            f"Street {street} out of range (1-{STREET_COUNT})."
        )

    first = ((street - 1) * NUMBERS_PER_STREET) + 1

    return (first, first + 1, first + 2)


def dozen_of(number: int) -> int | None:

    if number <= 0 or number > 36:
        return None

    return ((number - 1) // 12) + 1


def column_of(number: int) -> int | None:

    if number <= 0 or number > 36:
        return None

    remainder = number % 3

    if remainder == 1:
        return 1

    if remainder == 2:
        return 2

    return 3

"""Single-zero European wheel order in the user's viewing orientation."""

WHEEL_ORDER = (
    0, 26, 3, 35, 12, 28, 7, 29, 18, 22, 9, 31, 14,
    20, 1, 33, 16, 24, 5, 10, 23, 8, 30, 11, 36, 13,
    27, 6, 34, 17, 25, 2, 21, 4, 19, 15, 32,
)

_INDEX = {number: index for index, number in enumerate(WHEEL_ORDER)}


def wheel_index(number: int | str) -> int:
    try:
        parsed = int(number)
    except (TypeError, ValueError) as exc:
        raise ValueError("European roulette number must be an integer from 0 to 36.") from exc
    if parsed not in _INDEX:
        raise ValueError("European roulette number must be an integer from 0 to 36.")
    return _INDEX[parsed]

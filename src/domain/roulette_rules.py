from domain.roulette_result import RouletteColor


RED_NUMBERS = {
    1, 3, 5, 7, 9,
    12, 14, 16, 18,
    19, 21, 23, 25, 27,
    30, 32, 34, 36,
}


BLACK_NUMBERS = {
    2, 4, 6, 8, 10,
    11, 13, 15, 17,
    20, 22, 24, 26, 28,
    29, 31, 33, 35,
}


def expected_color(
    number: str,
) -> RouletteColor:

    if number in {"0", "00"}:
        return RouletteColor.GREEN

    value = int(number)

    if value in RED_NUMBERS:
        return RouletteColor.RED

    if value in BLACK_NUMBERS:
        return RouletteColor.BLACK

    raise ValueError(
        f"Invalid roulette number: {number}"
    )

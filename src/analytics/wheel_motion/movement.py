from dataclasses import dataclass
from enum import Enum

from analytics.wheel_motion.wheel_order import WHEEL_ORDER, wheel_index


class WheelDirection(str, Enum):
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    SAME = "SAME"


@dataclass(frozen=True)
class WheelMovement:
    from_number: int
    to_number: int
    direction: WheelDirection
    wheel_distance: int
    right_distance: int
    left_distance: int
    skipped_numbers: tuple[int, ...]
    middle_candidates: tuple[int, ...]
    opposite_number: int
    continuation_number: int


def calculate_movement(from_number: int | str, to_number: int | str) -> WheelMovement:
    start = _number(from_number)
    end = _number(to_number)
    start_index = wheel_index(start)
    end_index = wheel_index(end)
    right_distance = (end_index - start_index) % len(WHEEL_ORDER)
    left_distance = (start_index - end_index) % len(WHEEL_ORDER)
    if right_distance == 0:
        direction = WheelDirection.SAME
        distance = 0
        skipped = ()
    elif right_distance < left_distance:
        direction = WheelDirection.RIGHT
        distance = right_distance
        skipped = tuple(WHEEL_ORDER[(start_index + offset) % len(WHEEL_ORDER)] for offset in range(1, distance))
    else:
        direction = WheelDirection.LEFT
        distance = left_distance
        skipped = tuple(WHEEL_ORDER[(start_index - offset) % len(WHEEL_ORDER)] for offset in range(1, distance))
    middle = _middle_candidates(skipped)
    opposite_offset = -distance if direction is WheelDirection.RIGHT else distance
    opposite = WHEEL_ORDER[(start_index + opposite_offset) % len(WHEEL_ORDER)]
    continuation_offset = distance if direction is WheelDirection.RIGHT else -distance
    continuation = WHEEL_ORDER[(end_index + continuation_offset) % len(WHEEL_ORDER)]
    return WheelMovement(start, end, direction, distance, right_distance, left_distance, skipped, middle, opposite, continuation)


def _number(value: int | str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("European roulette number must be an integer from 0 to 36.") from exc
    if parsed < 0 or parsed > 36 or (isinstance(value, str) and value.strip() != str(parsed)):
        raise ValueError("European roulette number must be an integer from 0 to 36.")
    return parsed


def _middle_candidates(skipped: tuple[int, ...]) -> tuple[int, ...]:
    if not skipped:
        return ()
    middle = len(skipped) // 2
    return (skipped[middle],) if len(skipped) % 2 else (skipped[middle - 1], skipped[middle])

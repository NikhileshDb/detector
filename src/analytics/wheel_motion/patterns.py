from dataclasses import asdict, dataclass

from analytics.wheel_motion.movement import WheelMovement, calculate_movement
from analytics.wheel_motion.wheel_order import WHEEL_ORDER, wheel_index


@dataclass(frozen=True)
class ThreeSpinObservation:
    first_number: int
    second_number: int
    third_number: int
    first_movement: WheelMovement
    second_movement: WheelMovement
    third_position: str


def classify_third_position(first_movement: WheelMovement, third_number: int) -> str:
    if third_number in first_movement.middle_candidates:
        return "MIDDLE_TARGET"
    if third_number in first_movement.skipped_numbers:
        return "OTHER_SKIPPED"
    return "OUTSIDE_SEGMENT"


def scan_three_spin_observations(numbers: list[int | str]) -> list[ThreeSpinObservation]:
    observations = []
    for index in range(len(numbers) - 2):
        first = int(numbers[index])
        second = int(numbers[index + 1])
        third = int(numbers[index + 2])
        first_movement = calculate_movement(first, second)
        second_movement = calculate_movement(second, third)
        observations.append(ThreeSpinObservation(first, second, third, first_movement, second_movement, classify_third_position(first_movement, third)))
    return observations


def summarize_three_spin_observations(observations: list[ThreeSpinObservation], min_occurrences: int = 1) -> list[dict]:
    groups: dict[tuple, list[ThreeSpinObservation]] = {}
    for observation in observations:
        movement = observation.first_movement
        key = (movement.direction.value, movement.wheel_distance, len(movement.skipped_numbers))
        groups.setdefault(key, []).append(observation)
    result = []
    for (direction, distance, skipped_count), items in groups.items():
        if len(items) < min_occurrences:
            continue
        counts = {position: sum(item.third_position == position for item in items) for position in ("MIDDLE_TARGET", "OTHER_SKIPPED", "OUTSIDE_SEGMENT")}
        result.append({"direction": direction, "wheel_distance": distance, "skipped_count": skipped_count, "occurrences": len(items), "outcomes": {key: {"count": value, "probability": value / len(items)} for key, value in counts.items()}})
    return sorted(result, key=lambda item: item["occurrences"], reverse=True)


def summarize_projected_target_hits(observations: list[ThreeSpinObservation]) -> dict:
    sample_size = len(observations)
    target_getters = {
        "middle": lambda movement: movement.middle_candidates,
        "equal_distance": lambda movement: (movement.continuation_number,),
        "opposite_distance": lambda movement: (movement.opposite_number,),
    }
    targets = {}
    for name, target_getter in target_getters.items():
        exact_count = 0
        with_one_neighbor_count = 0
        for observation in observations:
            target_numbers = tuple(target_getter(observation.first_movement))
            if observation.third_number in target_numbers:
                exact_count += 1
            if observation.third_number in _targets_with_neighbors(target_numbers):
                with_one_neighbor_count += 1
        targets[name] = {
            "exact_count": exact_count,
            "with_one_neighbor_count": with_one_neighbor_count,
            "exact_probability": exact_count / sample_size if sample_size else 0.0,
            "with_one_neighbor_probability": with_one_neighbor_count / sample_size if sample_size else 0.0,
        }
    return {"sample_size": sample_size, "targets": targets}


def _targets_with_neighbors(target_numbers: tuple[int, ...]) -> set[int]:
    result = set(target_numbers)
    for target in target_numbers:
        index = wheel_index(target)
        result.add(WHEEL_ORDER[(index - 1) % len(WHEEL_ORDER)])
        result.add(WHEEL_ORDER[(index + 1) % len(WHEEL_ORDER)])
    return result


def current_movement_analysis(numbers: list[int | str], historical_numbers: list[int | str], min_occurrences: int = 1) -> dict:
    if len(numbers) < 2:
        return {"current": None, "historical": []}
    current = calculate_movement(numbers[-2], numbers[-1])
    historical = scan_three_spin_observations(historical_numbers)
    matching = [item for item in historical if item.first_movement.direction == current.direction and item.first_movement.wheel_distance == current.wheel_distance and len(item.first_movement.skipped_numbers) == len(current.skipped_numbers)]
    summary = summarize_three_spin_observations(matching, min_occurrences)
    eligible_matching = matching if len(matching) >= min_occurrences else []
    return {"current": {"from_number": current.from_number, "to_number": current.to_number, "direction": current.direction.value, "wheel_distance": current.wheel_distance, "skipped_numbers": list(current.skipped_numbers), "middle_candidates": list(current.middle_candidates), "opposite_number": current.opposite_number, "continuation_number": current.continuation_number}, "historical": summary, "projected_target_hits": summarize_projected_target_hits(eligible_matching)}

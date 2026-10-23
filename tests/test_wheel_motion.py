import pytest

from analytics.wheel_motion.movement import WheelDirection, calculate_movement
from analytics.wheel_motion.patterns import ThreeSpinObservation, summarize_projected_target_hits
from analytics.wheel_motion.wheel_order import WHEEL_ORDER, wheel_index


def test_single_zero_wheel_is_complete():
    assert len(WHEEL_ORDER) == 37
    assert set(WHEEL_ORDER) == set(range(37))
    assert WHEEL_ORDER[:4] == (0, 26, 3, 35)


def test_direction_is_calculated_from_any_previous_number():
    assert calculate_movement(0, 26).direction is WheelDirection.RIGHT
    assert calculate_movement(0, 32).direction is WheelDirection.LEFT
    assert calculate_movement(31, 31).direction is WheelDirection.SAME


def test_23_to_30_has_only_8_between_them():
    movement = calculate_movement(23, 30)
    assert movement.direction is WheelDirection.RIGHT
    assert movement.wheel_distance == 2
    assert movement.skipped_numbers == (8,)
    assert movement.middle_candidates == (8,)


def test_even_skipped_segment_has_two_middle_candidates():
    movement = calculate_movement(0, 12)
    assert len(movement.skipped_numbers) == 3
    assert len(movement.middle_candidates) == 1
    movement = calculate_movement(0, 28)
    assert movement.middle_candidates == (3, 35)


def test_opposite_number_uses_same_distance_in_reverse_direction():
    movement = calculate_movement(10, 20)
    assert movement.direction is WheelDirection.LEFT
    assert movement.wheel_distance == 6
    assert movement.opposite_number == 13
    assert movement.continuation_number == 29


def test_projected_target_hits_include_one_wheel_neighbor():
    first_movement = calculate_movement(10, 20)
    observations = [
        ThreeSpinObservation(10, 20, third, first_movement, calculate_movement(20, third), "")
        for third in (16, 33, 13, 36, 29, 7, 0)
    ]

    summary = summarize_projected_target_hits(observations)

    assert summary["sample_size"] == 7
    assert summary["targets"]["middle"]["exact_count"] == 1
    assert summary["targets"]["middle"]["with_one_neighbor_count"] == 2
    assert summary["targets"]["opposite_distance"]["exact_count"] == 1
    assert summary["targets"]["opposite_distance"]["with_one_neighbor_count"] == 2
    assert summary["targets"]["equal_distance"]["exact_count"] == 1
    assert summary["targets"]["equal_distance"]["with_one_neighbor_count"] == 2


@pytest.mark.parametrize("value", [-1, 37, "37", "1.0", "abc"])
def test_invalid_numbers_are_rejected(value):
    with pytest.raises(ValueError):
        wheel_index(value)

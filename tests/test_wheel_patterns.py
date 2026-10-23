from analytics.wheel_motion.movement import WheelDirection, calculate_movement
from analytics.wheel_motion.patterns import classify_third_position, scan_three_spin_observations, summarize_three_spin_observations


def test_third_spin_can_land_on_middle_target():
    movement = calculate_movement(23, 30)
    assert classify_third_position(movement, 8) == "MIDDLE_TARGET"


def test_three_spin_scan_records_both_movements():
    observations = scan_three_spin_observations([23, 30, 8])
    assert len(observations) == 1
    assert observations[0].first_movement.direction is WheelDirection.RIGHT
    assert observations[0].third_position == "MIDDLE_TARGET"


def test_summary_normalizes_outcomes():
    observations = scan_three_spin_observations([23, 30, 8, 17, 25, 0])
    result = summarize_three_spin_observations(observations)
    assert sum(next(iter(item["outcomes"].values()))["probability"] for item in result) >= 0
    assert all(sum(outcome["probability"] for outcome in item["outcomes"].values()) == 1 for item in result)

from analytics.wheel_motion.patterns import current_movement_analysis, scan_three_spin_observations


class WheelMotionService:
    def __init__(self, spin_repository):
        self.spin_repository = spin_repository

    def numbers(self, window=1000):
        spins = self.spin_repository.recent(window)
        return [int(spin.number) for spin in reversed(spins)]

    def current(self, window=1000, min_occurrences=1):
        numbers = self.numbers(window)
        return current_movement_analysis(numbers, numbers, min_occurrences)

    def movements(self, window=100):
        return [
            {
                "from_number": item.first_number,
                "to_number": item.second_number,
                "third_number": item.third_number,
                "direction": item.first_movement.direction.value,
                "wheel_distance": item.first_movement.wheel_distance,
                "skipped_numbers": list(item.first_movement.skipped_numbers),
                "middle_candidates": list(item.first_movement.middle_candidates),
                "opposite_number": item.first_movement.opposite_number,
                "continuation_number": item.first_movement.continuation_number,
                "third_position": item.third_position,
            }
            for item in scan_three_spin_observations(self.numbers(window))
        ]

from domain.roulette_rules import (
    expected_color,
)

from storage.models import (
    RoundStatus,
    SpinSource,
)
from storage.round_repository import (
    RoundRepository,
)
from storage.spin_repository import (
    SpinRepository,
)


class ManualResultService:
    def __init__(
        self,
        round_repository: RoundRepository,
        spin_repository: SpinRepository,
    ):
        self.round_repository = (
            round_repository
        )

        self.spin_repository = (
            spin_repository
        )

    def add_missing_result(
        self,
        round_id: int,
        number: str,
    ):

        round_item = (
            self.round_repository
            .get_by_id(
                round_id
            )
        )

        if round_item is None:
            raise ValueError(
                f"Round {round_id} not found."
            )

        existing = (
            self.spin_repository
            .get_by_round(
                round_id
            )
        )

        if existing is not None:
            raise ValueError(
                "Round already has a result."
            )

        color = expected_color(
            number
        )

        spin = (
            self.spin_repository.create(
                round_id=round_id,
                number=number,
                color=color.value,
                source=SpinSource.MANUAL,
                confidence=None,
            )
        )

        self.round_repository.mark_completed(
            round_id
        )

        return spin

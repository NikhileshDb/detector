from domain.roulette_rules import (
    expected_color,
)

from storage.database import Database
from storage.round_repository import (
    RoundRepository,
)
from storage.spin_repository import (
    SpinRepository,
)


class CorrectionService:
    def __init__(
        self,
        database: Database,
        round_repository: RoundRepository,
        spin_repository: SpinRepository,
    ):
        self.database = database

        self.round_repository = (
            round_repository
        )

        self.spin_repository = (
            spin_repository
        )

    def correct_result(
        self,
        round_id: int,
        corrected_number: str,
    ) -> None:

        color = expected_color(
            corrected_number
        )

        with self.database.transaction() as connection:

            round_item = (
                self.round_repository
                .get_by_id(
                    round_id,
                    connection=connection,
                )
            )

            if round_item is None:
                raise ValueError(
                    f"Round {round_id} not found."
                )

            existing = (
                self.spin_repository
                .get_by_round(
                    round_id,
                    connection=connection,
                )
            )

            if existing is None:
                raise ValueError(
                    f"No spin exists for round {round_id}."
                )

            self.spin_repository.update_correction(
                round_id=round_id,
                corrected_number=corrected_number,
                corrected_color=color.value,
                connection=connection,
            )

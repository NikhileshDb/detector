from domain.roulette_rules import (
    expected_color,
)

from storage.database import Database
from storage.models import (
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

    def add_missing_result(
        self,
        round_id: int,
        number: str,
    ):

        color = expected_color(
            number
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

            if existing is not None:
                raise ValueError(
                    "Round already has a result."
                )

            spin = (
                self.spin_repository.create(
                    round_id=round_id,
                    number=number,
                    color=color.value,
                    source=SpinSource.MANUAL,
                    confidence=None,
                    connection=connection,
                )
            )

            self.round_repository.mark_completed(
                round_id,
                connection=connection,
            )

        return spin

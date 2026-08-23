from dataclasses import dataclass


from domain.detector_state import (
    DetectorState,
)


@dataclass(frozen=True)
class RoundStarted:
    round_id: int


class RoundStateMachine:
    def __init__(self):
        self.state = DetectorState.UNKNOWN
        self.round_id = 0

    # ============================================================
    # PLACE YOUR BETS
    # ============================================================

    def on_place_your_bets(
        self,
    ) -> RoundStarted | None:

        if (
            self.state
            == DetectorState.PLACE_YOUR_BETS
        ):
            return None

        self.round_id += 1

        self.state = (
            DetectorState.PLACE_YOUR_BETS
        )

        return RoundStarted(
            round_id=self.round_id
        )

    # ============================================================
    # BETS CLOSING
    # ============================================================

    def on_bets_closing(
        self,
    ) -> bool:

        if self.round_id == 0:
            return False

        if (
            self.state
            == DetectorState.BETS_CLOSING
        ):
            return False

        self.state = (
            DetectorState.BETS_CLOSING
        )

        return True

    # ============================================================
    # BETS CLOSED
    # ============================================================

    def on_bets_closed(
        self,
    ) -> bool:

        if self.round_id == 0:
            return False

        if (
            self.state
            == DetectorState.WAITING_FOR_RESULT
        ):
            return False

        self.state = (
            DetectorState.WAITING_FOR_RESULT
        )

        return True

    # ============================================================
    # NEXT GAME SOON
    #
    # IMPORTANT:
    # On this roulette site NEXT GAME SOON appears BEFORE
    # the winning result such as "23 RED".
    # ============================================================

    def on_next_game_soon(
        self,
    ) -> bool:

        if self.round_id == 0:
            return False

        if (
            self.state
            == DetectorState.NEXT_GAME_SOON
        ):
            return False

        # Don't regress a confirmed/reading result.
        if self.state in {
            DetectorState.READING_RESULT,
            DetectorState.RESULT_CONFIRMED,
        }:
            return False

        self.state = (
            DetectorState.NEXT_GAME_SOON
        )

        return True

    # ============================================================
    # RESULT APPEARS
    # ============================================================

    def on_result_visible(
        self,
    ) -> bool:

        allowed_states = {
            DetectorState.WAITING_FOR_RESULT,
            DetectorState.BETS_CLOSING,
            DetectorState.NEXT_GAME_SOON,
        }

        if (
            self.state
            not in allowed_states
        ):
            return False

        self.state = (
            DetectorState.READING_RESULT
        )

        return True

    # ============================================================
    # RESULT CONFIRMED
    # ============================================================

    def on_result_confirmed(
        self,
    ) -> bool:

        if (
            self.state
            != DetectorState.READING_RESULT
        ):
            return False

        self.state = (
            DetectorState.RESULT_CONFIRMED
        )

        return True

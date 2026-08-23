from dataclasses import dataclass

from domain.roulette_result import (
    RouletteColor,
    ValidatedResult,
)


@dataclass(frozen=True)
class ConfirmedResult:
    number: str
    color: RouletteColor
    confidence: float


class ResultStabilizer:

    def __init__(
        self,
        required_matches: int = 3,
    ):
        self.required_matches = (
            required_matches
        )

        self._candidate: str | None = None

        self._candidate_color: (
            RouletteColor | None
        ) = None

        self._match_count = 0
        self._confidence_sum = 0.0

    def push(
        self,
        result: ValidatedResult | None,
    ) -> ConfirmedResult | None:

        if result is None:
            # Important:
            # do NOT reset because one OCR miss
            # should not destroy previous evidence.
            return None

        if (
            result.number != self._candidate
            or result.color
            != self._candidate_color
        ):
            self._candidate = result.number
            self._candidate_color = (
                result.color
            )

            self._match_count = 1
            self._confidence_sum = (
                result.confidence
            )

            return None

        self._match_count += 1

        self._confidence_sum += (
            result.confidence
        )

        if (
            self._match_count
            < self.required_matches
        ):
            return None

        average_confidence = (
            self._confidence_sum
            / self._match_count
        )

        return ConfirmedResult(
            number=self._candidate,
            color=self._candidate_color,
            confidence=average_confidence,
        )

    def reset_candidate(self) -> None:
        self._candidate = None
        self._candidate_color = None
        self._match_count = 0
        self._confidence_sum = 0.0

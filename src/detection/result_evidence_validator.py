from domain.roulette_result import (
    ResultEvidence,
    ValidatedResult,
)
from domain.roulette_rules import (
    expected_color,
)


class ResultEvidenceValidator:

    def validate(
        self,
        evidence: ResultEvidence,
    ) -> ValidatedResult | None:

        if evidence.status_number is None:
            return None

        if evidence.number_roi_number is None:
            # Some result layouts render the secondary number ROI differently
            # even though the status ROI is clear. Let the stabilizer accept
            # repeated, high-confidence status evidence in that case. A
            # readable conflicting number is still rejected below.
            if evidence.status_confidence is None or evidence.status_confidence < 0.60:
                return None
            expected = expected_color(evidence.status_number)
            if evidence.status_color is not None and evidence.status_color != expected:
                return None
            return ValidatedResult(
                number=evidence.status_number,
                color=expected,
                confidence=evidence.status_confidence,
            )

        # Both regions must agree on number.
        if (
            evidence.status_number
            != evidence.number_roi_number
        ):
            print(
                "Evidence mismatch: "
                f"status={evidence.status_number}, "
                f"number_roi={evidence.number_roi_number}"
            )

            return None

        expected = expected_color(
            evidence.status_number
        )

        # Status color must also match roulette rules.
        if (
            evidence.status_color is not None
            and evidence.status_color != expected
        ):
            print(
                "Color mismatch: "
                f"number={evidence.status_number}, "
                f"status_color={evidence.status_color.value}, "
                f"expected={expected.value}"
            )

            return None

        confidences = []

        if (
            evidence.status_confidence
            is not None
        ):
            confidences.append(
                evidence.status_confidence
            )

        if (
            evidence.number_roi_confidence
            is not None
        ):
            confidences.append(
                evidence.number_roi_confidence
            )

        confidence = (
            sum(confidences)
            / len(confidences)
            if confidences
            else 0.0
        )

        return ValidatedResult(
            number=evidence.status_number,
            color=expected,
            confidence=confidence,
        )

import re

import cv2
import numpy as np

from detection.number_recognizer import (
    RecognitionResult,
)


class EasyOcrNumberRecognizer:
    def __init__(
        self,
        reader,
        min_confidence: float = 0.60,
    ):
        self.reader = reader
        self.min_confidence = min_confidence

    def recognize(
        self,
        frame: np.ndarray,
    ) -> RecognitionResult | None:

        processed = self._preprocess(
            frame
        )

        results = self.reader.readtext(
            processed,
            detail=1,
            paragraph=False,
            allowlist="0123456789",
        )

        if not results:
            return None

        # Pick the OCR result with
        # the highest confidence.
        best_result = max(
            results,
            key=lambda item: item[2],
        )

        _, text, confidence = (
            best_result
        )

        confidence = float(
            confidence
        )

        normalized = self._normalize(
            text
        )

        if normalized is None:
            return None

        if (
            confidence
            < self.min_confidence
        ):
            return None

        return RecognitionResult(
            number=normalized,
            confidence=confidence,
        )

    def _preprocess(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        return gray

    def _normalize(
        self,
        value: str,
    ) -> str | None:

        value = value.strip()

        value = re.sub(
            r"[^0-9]",
            "",
            value,
        )

        if not value:
            return None

        # American roulette support
        if value == "00":
            return "00"

        try:
            number = int(
                value
            )

        except ValueError:
            return None

        if 0 <= number <= 36:
            return str(number)

        return None

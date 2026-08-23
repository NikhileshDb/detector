import re

import cv2
import easyocr

from domain.roulette_result import (
    RouletteColor,
    StatusResult,
)


class StatusResultRecognizer:
    def __init__(
        self,
        reader,
        min_confidence: float = 0.50,
    ):
        self.reader = reader
        self.min_confidence = min_confidence

    def recognize(
        self,
        frame,
    ) -> StatusResult | None:

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        results = self.reader.readtext(
            gray,
            detail=1,
            paragraph=False,
        )

        if not results:
            return None

        pieces = []
        confidences = []

        for _, text, confidence in results:
            pieces.append(text)
            confidences.append(
                float(confidence)
            )

        raw_text = " ".join(pieces)

        normalized = (
            raw_text
            .upper()
            .replace("\n", " ")
            .strip()
        )

        print(
            f"STATUS RESULT OCR: {normalized}"
        )

        match = re.search(
            r"\b(00|[0-9]|[12][0-9]|3[0-6])\b"
            r".*?"
            r"\b(RED|BLACK|GREEN)\b",
            normalized,
        )

        if match is None:
            return None

        number = match.group(1)

        color = RouletteColor(
            match.group(2)
        )

        confidence = (
            sum(confidences)
            / len(confidences)
        )

        if confidence < self.min_confidence:
            return None

        return StatusResult(
            number=number,
            color=color,
            confidence=confidence,
        )

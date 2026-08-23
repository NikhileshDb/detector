from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class RecognitionResult:
    number: str
    confidence: float


class NumberRecognizer(Protocol):
    def recognize(
        self,
        frame: np.ndarray,
    ) -> RecognitionResult | None:
        ...

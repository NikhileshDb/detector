from dataclasses import dataclass
from datetime import datetime


@dataclass
class RouletteRound:
    id: int

    started_at: datetime

    result: str | None = None

    confidence: float | None = None

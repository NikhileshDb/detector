import dataclasses
import json
from dataclasses import dataclass
from typing import ClassVar, Union


@dataclass(frozen=True)
class RoundStartedEvent:
    round_id: int

    TYPE: ClassVar[str] = "round_started"


@dataclass(frozen=True)
class StateChangedEvent:
    state: str
    round_id: int

    TYPE: ClassVar[str] = "state_changed"


@dataclass(frozen=True)
class SpinConfirmedEvent:
    round_id: int
    number: str
    color: str
    confidence: float

    TYPE: ClassVar[str] = "spin_confirmed"


@dataclass(frozen=True)
class ManualResultEvent:
    round_id: int
    number: str
    color: str

    TYPE: ClassVar[str] = "manual_result"


@dataclass(frozen=True)
class CorrectionAppliedEvent:
    round_id: int
    corrected_number: str
    corrected_color: str

    TYPE: ClassVar[str] = "correction_applied"


DetectorEvent = Union[
    RoundStartedEvent,
    StateChangedEvent,
    SpinConfirmedEvent,
    ManualResultEvent,
    CorrectionAppliedEvent,
]


def serialize_event(event: DetectorEvent) -> str:

    payload = {
        "type": event.TYPE,
        "data": dataclasses.asdict(event),
    }

    return json.dumps(payload)

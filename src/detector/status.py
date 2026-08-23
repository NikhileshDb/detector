import threading

from domain.detector_state import DetectorState


class DetectorStatusHolder:
    """Thread-safe: written by the detector loop (main thread), read by
    API request handlers (API server thread)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._state = DetectorState.UNKNOWN
        self._round_id = 0

    def update(self, state: DetectorState, round_id: int) -> None:

        with self._lock:
            self._state = state
            self._round_id = round_id

    def snapshot(self) -> tuple[str | None, int | None]:

        with self._lock:
            return (
                self._state.name,
                self._round_id if self._round_id else None,
            )

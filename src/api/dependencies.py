from fastapi import Request

from events.event_publisher import EventPublisher
from storage.correction_service import CorrectionService
from storage.manual_result_service import ManualResultService
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository
from storage.session_repository import SessionRepository


def get_round_repository(
    request: Request,
) -> RoundRepository:

    return request.app.state.round_repository


def get_database(request: Request):
    return request.app.state.database


def get_spin_repository(
    request: Request,
) -> SpinRepository:

    return request.app.state.spin_repository


def get_session_repository(request: Request) -> SessionRepository:
    return request.app.state.session_repository


def get_manual_result_service(
    request: Request,
) -> ManualResultService:

    return request.app.state.manual_result_service


def get_correction_service(
    request: Request,
) -> CorrectionService:

    return request.app.state.correction_service


def get_event_publisher(
    request: Request,
) -> EventPublisher:

    return request.app.state.event_publisher


def get_detector_status(
    request: Request,
) -> tuple[str | None, int | None]:
    """Returns (state_name, round_id). Wired to a real DetectorStatusHolder
    once main.py constructs one; until then app.state has none and this
    reports unknown."""

    holder = getattr(
        request.app.state,
        "detector_status_holder",
        None,
    )

    if holder is None:
        return None, None

    return holder.snapshot()

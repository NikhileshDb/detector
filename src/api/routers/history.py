from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_event_publisher,
    get_manual_result_service,
    get_round_repository,
)
from api.schemas import ManualResultIn, RoundOut, SpinOut
from events.event_publisher import EventPublisher
from events.event_types import ManualResultEvent
from storage.manual_result_service import ManualResultService
from storage.round_repository import RoundRepository


router = APIRouter(prefix="/api/rounds", tags=["history"])


@router.get("", response_model=list[RoundOut])
def list_rounds(
    limit: int = 50,
    round_repository: RoundRepository = Depends(get_round_repository),
) -> list[RoundOut]:

    rounds = round_repository.recent(limit)

    return [RoundOut.from_domain(item) for item in rounds]


@router.get("/latest", response_model=RoundOut)
def get_latest_round(
    round_repository: RoundRepository = Depends(get_round_repository),
) -> RoundOut:

    round_item = round_repository.latest()

    if round_item is None:
        raise HTTPException(status_code=404, detail="No rounds recorded yet.")

    return RoundOut.from_domain(round_item)


@router.get("/{round_id}", response_model=RoundOut)
def get_round(
    round_id: int,
    round_repository: RoundRepository = Depends(get_round_repository),
) -> RoundOut:

    round_item = round_repository.get_by_id(round_id)

    if round_item is None:
        raise HTTPException(status_code=404, detail=f"Round {round_id} not found.")

    return RoundOut.from_domain(round_item)


@router.post("/{round_id}/manual-result", response_model=SpinOut)
def add_manual_result(
    round_id: int,
    body: ManualResultIn,
    manual_result_service: ManualResultService = Depends(get_manual_result_service),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> SpinOut:

    try:
        spin = manual_result_service.add_missing_result(
            round_id=round_id,
            number=body.number,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=_status_for_value_error(exc),
            detail=str(exc),
        ) from exc

    event_publisher.publish(
        ManualResultEvent(
            round_id=round_id,
            number=spin.number,
            color=spin.color,
        )
    )

    return SpinOut.from_domain(spin)


def _status_for_value_error(exc: ValueError) -> int:

    message = str(exc)

    if "not found" in message:
        return 404

    if "already has a result" in message:
        return 409

    return 400

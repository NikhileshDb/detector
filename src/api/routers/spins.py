from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_correction_service,
    get_event_publisher,
    get_spin_repository,
    get_round_repository,
)
from api.schemas import CorrectionIn, SpinOut
from events.event_publisher import EventPublisher
from events.event_types import CorrectionAppliedEvent
from storage.correction_service import CorrectionService
from storage.spin_repository import SpinRepository
from storage.round_repository import RoundRepository


router = APIRouter(prefix="/api/spins", tags=["spins"])


@router.get("", response_model=list[SpinOut])
def list_spins(
    limit: int = 100,
    session_id: int | None = None,
    spin_repository: SpinRepository = Depends(get_spin_repository),
) -> list[SpinOut]:

    spins = spin_repository.recent(limit, session_id=session_id)

    return [SpinOut.from_domain(item) for item in spins]


@router.get("/round/{round_id}", response_model=SpinOut)
def get_spin_for_round(
    round_id: int,
    spin_repository: SpinRepository = Depends(get_spin_repository),
) -> SpinOut:

    spin = spin_repository.get_by_round(round_id)

    if spin is None:
        raise HTTPException(
            status_code=404,
            detail=f"No spin recorded for round {round_id}.",
        )

    return SpinOut.from_domain(spin)


@router.delete("/round/{round_id}", status_code=204)
def delete_spin(
    round_id: int,
    round_repository: RoundRepository = Depends(get_round_repository),
) -> None:
    if not round_repository.delete(round_id):
        raise HTTPException(status_code=404, detail="Spin round not found.")


@router.patch("/round/{round_id}/correction", response_model=SpinOut)
def correct_spin(
    round_id: int,
    body: CorrectionIn,
    correction_service: CorrectionService = Depends(get_correction_service),
    spin_repository: SpinRepository = Depends(get_spin_repository),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> SpinOut:

    try:
        correction_service.correct_result(
            round_id=round_id,
            corrected_number=body.corrected_number,
        )

    except ValueError as exc:
        message = str(exc)

        if "not found" in message or "No spin exists" in message:
            status_code = 404

        else:
            status_code = 400

        raise HTTPException(status_code=status_code, detail=message) from exc

    spin = spin_repository.get_by_round(round_id)

    event_publisher.publish(
        CorrectionAppliedEvent(
            round_id=round_id,
            corrected_number=spin.number,
            corrected_color=spin.color,
        )
    )

    return SpinOut.from_domain(spin)

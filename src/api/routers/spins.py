from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_correction_service,
    get_event_publisher,
    get_spin_repository,
)
from api.schemas import CorrectionIn, SpinOut
from events.event_publisher import EventPublisher
from events.event_types import CorrectionAppliedEvent
from storage.correction_service import CorrectionService
from storage.spin_repository import SpinRepository


router = APIRouter(prefix="/api/spins", tags=["spins"])


@router.get("", response_model=list[SpinOut])
def list_spins(
    limit: int = 100,
    spin_repository: SpinRepository = Depends(get_spin_repository),
) -> list[SpinOut]:

    spins = spin_repository.recent(limit)

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

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_spin_repository
from api.schemas import SpinOut
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

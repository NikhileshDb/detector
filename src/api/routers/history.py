from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_round_repository
from api.schemas import RoundOut
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

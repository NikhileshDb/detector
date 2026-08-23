from fastapi import APIRouter, Depends

from analytics.dashboard_summary import compute_dashboard_summary
from analytics.street_analytics import compute_street_stats
from api.dependencies import get_detector_status, get_spin_repository
from api.schemas import DashboardSummaryOut, DetectorStatusOut, StreetStatsOut
from storage.spin_repository import SpinRepository


router = APIRouter(tags=["dashboard"])


@router.get("/api/status", response_model=DetectorStatusOut)
def get_status(
    detector_status: tuple[str | None, int | None] = Depends(get_detector_status),
) -> DetectorStatusOut:

    state, round_id = detector_status

    return DetectorStatusOut(state=state, round_id=round_id)


@router.get("/api/dashboard/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(
    limit: int = 100,
    spin_repository: SpinRepository = Depends(get_spin_repository),
    detector_status: tuple[str | None, int | None] = Depends(get_detector_status),
) -> DashboardSummaryOut:

    current_state, current_round_id = detector_status

    summary = compute_dashboard_summary(
        spins=spin_repository.recent(limit),
        current_state=current_state,
        current_round_id=current_round_id,
    )

    return DashboardSummaryOut.from_domain(summary)


@router.get("/api/analytics/streets", response_model=list[StreetStatsOut])
def get_street_analytics(
    limit: int = 100,
    spin_repository: SpinRepository = Depends(get_spin_repository),
) -> list[StreetStatsOut]:

    stats = compute_street_stats(spin_repository.recent(limit))

    return [StreetStatsOut.from_domain(item) for item in stats]

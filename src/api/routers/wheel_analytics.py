from fastapi import APIRouter, Depends, Query

from api.dependencies import get_spin_repository
from analytics.wheel_motion.service import WheelMotionService

router = APIRouter(prefix="/api/analytics/wheel", tags=["wheel motion analytics"])


def service(repository=Depends(get_spin_repository)):
    return WheelMotionService(repository)


@router.get("/current")
def current(window: int = Query(1000, ge=2), min_occurrences: int = Query(1, ge=1), analytics: WheelMotionService = Depends(service)):
    return analytics.current(window, min_occurrences)


@router.get("/movements")
def movements(window: int = Query(100, ge=3), analytics: WheelMotionService = Depends(service)):
    return {"items": analytics.movements(window)}

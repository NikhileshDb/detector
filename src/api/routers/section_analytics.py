from fastapi import APIRouter, Depends, Query

from api.dependencies import get_spin_repository
from analytics.sections.markov_service import SectionMarkovService

router = APIRouter(prefix="/api/analytics/sections", tags=["section analytics"])


def service(repository=Depends(get_spin_repository)):
    return SectionMarkovService(repository)


@router.get("/markov/matrix")
def matrix(window: int = Query(500, ge=1), analytics: SectionMarkovService = Depends(service)):
    return analytics.matrix(window)


@router.get("/markov/current")
def current(order: int = Query(3, ge=1, le=5), window: int = Query(1000, ge=1), min_occurrences: int = Query(20, ge=1), analytics: SectionMarkovService = Depends(service)):
    return analytics.current(window, order, min_occurrences)


@router.get("/recent")
def recent(limit: int = Query(50, ge=1), analytics: SectionMarkovService = Depends(service)):
    return {"items": analytics.recent(limit)}


@router.get("/markov/contexts")
def contexts(order: int = Query(3, ge=1, le=5), window: int = Query(1000, ge=1), min_occurrences: int = Query(20, ge=1), analytics: SectionMarkovService = Depends(service)):
    return {"contexts": analytics.contexts(window, order, min_occurrences)}


@router.get("/overview")
def overview(window: int = Query(100, ge=1), analytics: SectionMarkovService = Depends(service)):
    return analytics.overview(window)


@router.get("/patterns/current")
def current_pattern(length: int = Query(4, ge=3, le=6), window: int = Query(1000, ge=1), min_occurrences: int = Query(20, ge=1), analytics: SectionMarkovService = Depends(service)):
    return analytics.current_pattern(length, window, min_occurrences)


@router.get("/patterns")
def patterns(length: int = Query(4, ge=3, le=6), window: int = Query(1000, ge=1), min_occurrences: int = Query(20, ge=1), sort: str = Query("occurrences"), analytics: SectionMarkovService = Depends(service)):
    return {"patterns": analytics.patterns(length, window, min_occurrences, sort)}


@router.get("/validation/models")
def validation(start_after: int = Query(20, ge=1), window: int = Query(1000, ge=1), min_occurrences: int = Query(20, ge=1), analytics: SectionMarkovService = Depends(service)):
    return analytics.validation(start_after, window, min_occurrences)

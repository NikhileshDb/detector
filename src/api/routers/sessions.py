from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_session_repository
from storage.session_repository import SessionRepository

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("")
def list_sessions(repository: SessionRepository = Depends(get_session_repository)) -> list[dict]:
    return repository.list()


@router.get("/active")
def active_session(repository: SessionRepository = Depends(get_session_repository)) -> dict:
    return repository.active()


@router.post("")
def start_session(repository: SessionRepository = Depends(get_session_repository), name: str | None = None) -> dict:
    return repository.start(name)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, repository: SessionRepository = Depends(get_session_repository)) -> None:
    try:
        deleted = repository.delete(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")

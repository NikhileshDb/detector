from fastapi import Request

from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository


def get_round_repository(
    request: Request,
) -> RoundRepository:

    return request.app.state.round_repository


def get_spin_repository(
    request: Request,
) -> SpinRepository:

    return request.app.state.spin_repository

from fastapi import FastAPI

from api.routers import history, spins
from storage.database import Database
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository


def create_app(
    database: Database,
    round_repository: RoundRepository,
    spin_repository: SpinRepository,
) -> FastAPI:

    app = FastAPI(title="Roulette Analytics API")

    app.state.database = database
    app.state.round_repository = round_repository
    app.state.spin_repository = spin_repository

    app.include_router(history.router)
    app.include_router(spins.router)

    return app

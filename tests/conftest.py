import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from storage.database import Database
from storage.round_repository import RoundRepository
from storage.spin_repository import SpinRepository


@pytest.fixture
def database(tmp_path):

    db = Database(path=str(tmp_path / "test.db"))
    db.initialize()

    return db


@pytest.fixture
def round_repository(database):

    return RoundRepository(database)


@pytest.fixture
def spin_repository(database):

    return SpinRepository(database)


@pytest.fixture
def app(database, round_repository, spin_repository):

    return create_app(
        database=database,
        round_repository=round_repository,
        spin_repository=spin_repository,
    )


@pytest.fixture
def client(app):

    return TestClient(app)

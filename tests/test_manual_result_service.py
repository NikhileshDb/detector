import pytest

from storage.manual_result_service import ManualResultService
from storage.models import SpinSource


@pytest.fixture
def service(database, round_repository, spin_repository):

    return ManualResultService(
        database=database,
        round_repository=round_repository,
        spin_repository=spin_repository,
    )


def test_add_missing_result_happy_path(service, round_repository):

    r = round_repository.create(sequence=1)

    spin = service.add_missing_result(round_id=r.id, number="23")

    assert spin.number == "23"
    assert spin.color == "RED"
    assert spin.source == SpinSource.MANUAL
    assert round_repository.get_by_id(r.id).status.value == "COMPLETED"


def test_add_missing_result_round_not_found(service):

    with pytest.raises(ValueError, match="not found"):
        service.add_missing_result(round_id=999, number="23")


def test_add_missing_result_conflict(service, round_repository):

    r = round_repository.create(sequence=1)

    service.add_missing_result(round_id=r.id, number="23")

    with pytest.raises(ValueError, match="already has a result"):
        service.add_missing_result(round_id=r.id, number="5")


def test_add_missing_result_invalid_number_rolls_back(
    service,
    round_repository,
    spin_repository,
):

    r = round_repository.create(sequence=1)

    with pytest.raises(ValueError):
        service.add_missing_result(round_id=r.id, number="99")

    assert spin_repository.get_by_round(r.id) is None
    assert round_repository.get_by_id(r.id).status.value == "ACTIVE"

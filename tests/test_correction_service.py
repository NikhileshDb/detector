import pytest

from storage.correction_service import CorrectionService
from storage.models import SpinSource


@pytest.fixture
def service(database, round_repository, spin_repository):

    return CorrectionService(
        database=database,
        round_repository=round_repository,
        spin_repository=spin_repository,
    )


def test_correct_result_happy_path(service, round_repository, spin_repository):

    r = round_repository.create(sequence=1)

    spin_repository.create(
        round_id=r.id,
        number="17",
        color="BLACK",
        source=SpinSource.AUTO,
    )

    service.correct_result(round_id=r.id, corrected_number="23")

    updated = spin_repository.get_by_round(r.id)

    assert updated.number == "23"
    assert updated.color == "RED"
    assert updated.source == SpinSource.CORRECTED


def test_correct_result_round_not_found(service):

    with pytest.raises(ValueError, match="not found"):
        service.correct_result(round_id=999, corrected_number="23")


def test_correct_result_no_spin(service, round_repository):

    r = round_repository.create(sequence=1)

    with pytest.raises(ValueError, match="No spin exists"):
        service.correct_result(round_id=r.id, corrected_number="23")


def test_correct_result_invalid_number_leaves_spin_untouched(
    service,
    round_repository,
    spin_repository,
):

    r = round_repository.create(sequence=1)

    spin_repository.create(
        round_id=r.id,
        number="17",
        color="BLACK",
        source=SpinSource.AUTO,
    )

    with pytest.raises(ValueError):
        service.correct_result(round_id=r.id, corrected_number="abc")

    unchanged = spin_repository.get_by_round(r.id)

    assert unchanged.number == "17"
    assert unchanged.source == SpinSource.AUTO

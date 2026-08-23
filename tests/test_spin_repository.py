import pytest

from storage.models import SpinSource


def test_create_and_get_by_round(round_repository, spin_repository):

    r = round_repository.create(sequence=1)

    spin = spin_repository.create(
        round_id=r.id,
        number="17",
        color="BLACK",
        source=SpinSource.AUTO,
        confidence=0.9,
    )

    fetched = spin_repository.get_by_round(r.id)

    assert fetched.id == spin.id
    assert fetched.number == "17"


def test_get_by_round_missing_returns_none(spin_repository):

    assert spin_repository.get_by_round(999) is None


def test_recent_orders_desc(round_repository, spin_repository):

    for index, number in enumerate(["1", "2", "3"], start=1):

        r = round_repository.create(sequence=index)

        spin_repository.create(
            round_id=r.id,
            number=number,
            color="RED",
            source=SpinSource.AUTO,
        )

    recent = spin_repository.recent(limit=10)

    assert [item.number for item in recent] == ["3", "2", "1"]


def test_update_correction(round_repository, spin_repository):

    r = round_repository.create(sequence=1)

    spin_repository.create(
        round_id=r.id,
        number="17",
        color="BLACK",
        source=SpinSource.AUTO,
    )

    spin_repository.update_correction(
        round_id=r.id,
        corrected_number="23",
        corrected_color="RED",
    )

    updated = spin_repository.get_by_round(r.id)

    assert updated.number == "23"
    assert updated.original_number == "17"
    assert updated.source == SpinSource.CORRECTED


def test_update_correction_raises_when_missing(spin_repository):

    with pytest.raises(ValueError):
        spin_repository.update_correction(
            round_id=999,
            corrected_number="1",
            corrected_color="RED",
        )

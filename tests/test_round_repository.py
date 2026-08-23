from storage.models import RoundStatus


def test_create_and_get_by_id(round_repository):

    r = round_repository.create(sequence=1)
    fetched = round_repository.get_by_id(r.id)

    assert fetched.sequence == 1
    assert fetched.status == RoundStatus.ACTIVE


def test_get_by_sequence(round_repository):

    r = round_repository.create(sequence=5)
    fetched = round_repository.get_by_sequence(5)

    assert fetched.id == r.id


def test_get_by_id_missing_returns_none(round_repository):

    assert round_repository.get_by_id(999) is None


def test_latest_returns_highest_sequence(round_repository):

    round_repository.create(sequence=1)
    r2 = round_repository.create(sequence=2)

    assert round_repository.latest().id == r2.id


def test_mark_completed_sets_status_and_timestamp(round_repository):

    r = round_repository.create(sequence=1)
    round_repository.mark_completed(r.id)

    updated = round_repository.get_by_id(r.id)

    assert updated.status == RoundStatus.COMPLETED
    assert updated.completed_at is not None


def test_mark_missing(round_repository):

    r = round_repository.create(sequence=1)
    round_repository.mark_missing(r.id)

    assert round_repository.get_by_id(r.id).status == RoundStatus.MISSING


def test_recent_orders_desc_by_sequence(round_repository):

    for sequence in range(1, 4):
        round_repository.create(sequence=sequence)

    recent = round_repository.recent(limit=2)

    assert [item.sequence for item in recent] == [3, 2]

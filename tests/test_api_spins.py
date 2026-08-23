from storage.models import SpinSource


def test_list_spins_empty(client):

    resp = client.get("/api/spins")

    assert resp.status_code == 200
    assert resp.json() == []


def test_get_spin_for_round_not_found(client):

    resp = client.get("/api/spins/round/999")

    assert resp.status_code == 404


def test_correction_endpoint(client, round_repository, spin_repository):

    r = round_repository.create(sequence=1)

    spin_repository.create(
        round_id=r.id,
        number="17",
        color="BLACK",
        source=SpinSource.AUTO,
    )

    resp = client.patch(
        f"/api/spins/round/{r.id}/correction",
        json={"corrected_number": "23"},
    )

    assert resp.status_code == 200
    assert resp.json()["number"] == "23"
    assert resp.json()["source"] == "CORRECTED"


def test_correction_endpoint_no_spin(client, round_repository):

    r = round_repository.create(sequence=1)

    resp = client.patch(
        f"/api/spins/round/{r.id}/correction",
        json={"corrected_number": "23"},
    )

    assert resp.status_code == 404

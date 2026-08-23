def test_list_rounds_empty(client):

    resp = client.get("/api/rounds")

    assert resp.status_code == 200
    assert resp.json() == []


def test_get_round_not_found(client):

    resp = client.get("/api/rounds/999")

    assert resp.status_code == 404


def test_latest_round_not_found_when_empty(client):

    resp = client.get("/api/rounds/latest")

    assert resp.status_code == 404


def test_get_round_after_create(client, round_repository):

    r = round_repository.create(sequence=1)

    resp = client.get(f"/api/rounds/{r.id}")

    assert resp.status_code == 200
    assert resp.json()["sequence"] == 1


def test_manual_result_endpoint(client, round_repository):

    r = round_repository.create(sequence=1)

    resp = client.post(
        f"/api/rounds/{r.id}/manual-result",
        json={"number": "17"},
    )

    assert resp.status_code == 200
    assert resp.json()["number"] == "17"
    assert resp.json()["source"] == "MANUAL"


def test_manual_result_not_found(client):

    resp = client.post(
        "/api/rounds/999/manual-result",
        json={"number": "17"},
    )

    assert resp.status_code == 404


def test_manual_result_conflict(client, round_repository):

    r = round_repository.create(sequence=1)

    client.post(f"/api/rounds/{r.id}/manual-result", json={"number": "17"})

    resp = client.post(f"/api/rounds/{r.id}/manual-result", json={"number": "5"})

    assert resp.status_code == 409


def test_manual_result_invalid_number(client, round_repository):

    r = round_repository.create(sequence=1)

    resp = client.post(f"/api/rounds/{r.id}/manual-result", json={"number": "99"})

    assert resp.status_code == 400

def test_status_defaults_to_unknown(client):

    resp = client.get("/api/status")

    assert resp.status_code == 200
    assert resp.json() == {"state": None, "round_id": None}


def test_dashboard_summary_empty(client):

    resp = client.get("/api/dashboard/summary")

    assert resp.status_code == 200

    body = resp.json()

    assert body["window_size"] == 0
    assert len(body["street_stats"]) == 12


def test_analytics_streets_empty(client):

    resp = client.get("/api/analytics/streets")

    assert resp.status_code == 200
    assert len(resp.json()) == 12

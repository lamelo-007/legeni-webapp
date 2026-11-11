from app import app

client = app.test_client()


def test_index_ok():
    assert client.get("/").status_code == 200


def test_index_shows_version():
    assert b"Version" in client.get("/").data


def test_health():
    assert client.get("/health").get_json() == {"status": "ok"}


def test_ready():
    assert client.get("/ready").status_code == 200


def test_info_keys():
    data = client.get("/api/info").get_json()
    assert {"env", "version", "hostname"} <= set(data)


def test_unknown_route_404():
    assert client.get("/nexiste-pas").status_code == 404

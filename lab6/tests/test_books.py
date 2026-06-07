from fastapi.testclient import TestClient

SAMPLE = {
    "title": "Kobzar", "author": "Taras Shevchenko",
    "year": 1840, "pages": 312, "status": "free",
}


# ── No token — public GET ─────────────────────────────────────────────────────

def test_get_list_no_auth_200(client: TestClient):
    assert client.get("/books/").status_code == 200


def test_get_single_no_auth_200(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.get(f"/books/{uid}").status_code == 200


# ── Auth required for writes ──────────────────────────────────────────────────

def test_post_no_token_401(client: TestClient):
    assert client.post("/books/", json=SAMPLE).status_code == 401


def test_delete_no_token_401(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.delete(f"/books/{uid}").status_code == 401


def test_invalid_token_401(client: TestClient):
    headers = {"Authorization": "Bearer not.valid.token"}
    assert client.post("/books/", json=SAMPLE, headers=headers).status_code == 401


# ── Authenticated user can do full CRUD ──────────────────────────────────────

def test_post_with_auth_201(client: TestClient, headers_a):
    assert client.post("/books/", json=SAMPLE, headers=headers_a).status_code == 201


def test_post_fields(client: TestClient, headers_a):
    data = client.post("/books/", json=SAMPLE, headers=headers_a).json()
    assert data["title"] == SAMPLE["title"]
    assert data["pages"] == SAMPLE["pages"]
    assert data["status"] == "free"


def test_post_unique_ids(client: TestClient, headers_a):
    a = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    b = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert a != b


def test_any_user_can_post(client: TestClient, headers_b):
    assert client.post("/books/", json=SAMPLE, headers=headers_b).status_code == 201


def test_get_list_with_auth_200(client: TestClient, headers_a):
    assert client.get("/books/", headers=headers_a).status_code == 200


def test_get_list_structure(client: TestClient, headers_a):
    client.post("/books/", json=SAMPLE, headers=headers_a)
    data = client.get("/books/").json()
    assert all(k in data for k in ("items", "total", "limit", "offset"))


def test_filter_status_free(client: TestClient, headers_a):
    client.post("/books/", json={**SAMPLE, "status": "free"}, headers=headers_a)
    client.post("/books/", json={**SAMPLE, "title": "B", "status": "on_loan"}, headers=headers_a)
    data = client.get("/books/?status=free").json()
    assert data["total"] == 1 and data["items"][0]["status"] == "free"


def test_filter_status_on_loan(client: TestClient, headers_a):
    client.post("/books/", json={**SAMPLE, "status": "on_loan"}, headers=headers_a)
    client.post("/books/", json={**SAMPLE, "title": "B", "status": "free"}, headers=headers_a)
    data = client.get("/books/?status=on_loan").json()
    assert data["total"] == 1


def test_pagination(client: TestClient, headers_a):
    for i in range(5):
        client.post("/books/", json={**SAMPLE, "title": f"Book{i}"}, headers=headers_a)
    data = client.get("/books/?limit=3").json()
    assert len(data["items"]) == 3 and data["total"] == 5


def test_get_single_200(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.get(f"/books/{uid}").status_code == 200


def test_get_single_404(client: TestClient):
    assert client.get("/books/00000000-0000-0000-0000-000000000000").status_code == 404


def test_delete_204(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.delete(f"/books/{uid}", headers=headers_a).status_code == 204


def test_delete_removes(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    client.delete(f"/books/{uid}", headers=headers_a)
    assert client.get(f"/books/{uid}").status_code == 404


def test_delete_idempotent(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    client.delete(f"/books/{uid}", headers=headers_a)
    assert client.delete(f"/books/{uid}", headers=headers_a).status_code == 204


def test_post_missing_title_422(client: TestClient, headers_a):
    book = {k: v for k, v in SAMPLE.items() if k != "title"}
    assert client.post("/books/", json=book, headers=headers_a).status_code == 422


def test_post_invalid_status_422(client: TestClient, headers_a):
    assert client.post("/books/", json={**SAMPLE, "status": "broken"}, headers=headers_a).status_code == 422

from fastapi.testclient import TestClient

SAMPLE = {
    "title": "Kobzar", "author": "Taras Shevchenko",
    "year": 1840, "pages": 312, "status": "free",
}


def test_get_list_no_auth_200(client: TestClient):
    assert client.get("/books/").status_code == 200


def test_post_no_token_401(client: TestClient):
    assert client.post("/books/", json=SAMPLE).status_code == 401


def test_delete_no_token_401(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.delete(f"/books/{uid}").status_code == 401


def test_post_with_auth_201(client: TestClient, headers_a):
    assert client.post("/books/", json=SAMPLE, headers=headers_a).status_code == 201


def test_post_fields(client: TestClient, headers_a):
    data = client.post("/books/", json=SAMPLE, headers=headers_a).json()
    assert data["title"] == SAMPLE["title"] and data["pages"] == SAMPLE["pages"]


def test_any_auth_user_can_post(client: TestClient, headers_b):
    assert client.post("/books/", json=SAMPLE, headers=headers_b).status_code == 201


def test_list_structure(client: TestClient, headers_a):
    client.post("/books/", json=SAMPLE, headers=headers_a)
    data = client.get("/books/").json()
    assert all(k in data for k in ("items", "total", "limit", "offset"))


def test_filter_status_free(client: TestClient, headers_a):
    client.post("/books/", json={**SAMPLE, "status": "free"}, headers=headers_a)
    client.post("/books/", json={**SAMPLE, "title": "B", "status": "on_loan"}, headers=headers_a)
    data = client.get("/books/?status=free").json()
    assert data["total"] == 1 and data["items"][0]["status"] == "free"


def test_filter_on_loan(client: TestClient, headers_a):
    client.post("/books/", json={**SAMPLE, "status": "on_loan"}, headers=headers_a)
    client.post("/books/", json={**SAMPLE, "title": "B", "status": "free"}, headers=headers_a)
    assert client.get("/books/?status=on_loan").json()["total"] == 1


def test_get_single_200(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.get(f"/books/{uid}").status_code == 200


def test_get_single_404(client: TestClient):
    assert client.get("/books/00000000-0000-0000-0000-000000000000").status_code == 404


def test_delete_204(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    assert client.delete(f"/books/{uid}", headers=headers_a).status_code == 204


def test_delete_idempotent(client: TestClient, headers_a):
    uid = client.post("/books/", json=SAMPLE, headers=headers_a).json()["id"]
    client.delete(f"/books/{uid}", headers=headers_a)
    assert client.delete(f"/books/{uid}", headers=headers_a).status_code == 204


def test_post_invalid_status_422(client: TestClient, headers_a):
    assert client.post("/books/", json={**SAMPLE, "status": "broken"}, headers=headers_a).status_code == 422

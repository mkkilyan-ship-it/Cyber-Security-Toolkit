import io

import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_password_endpoint(client):
    response = client.post("/api/password", json={"length": 20})
    assert response.status_code == 200
    assert len(response.get_json()["password"]) == 20


def test_hash_endpoint(client):
    data = {"file": (io.BytesIO(b"hello"), "test.txt")}
    response = client.post("/api/hash", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert "sha256" in response.get_json()["hashes"]


def test_encrypt_decrypt_roundtrip(client):
    data = {"file": (io.BytesIO(b"secret data"), "test.txt"), "password": "pwd123"}
    encrypt_resp = client.post("/api/encrypt", data=data, content_type="multipart/form-data")
    assert encrypt_resp.status_code == 200

    encrypted_bytes = encrypt_resp.data
    decrypt_data = {
        "file": (io.BytesIO(encrypted_bytes), "test.txt.enc"),
        "password": "pwd123",
    }
    decrypt_resp = client.post("/api/decrypt", data=decrypt_data, content_type="multipart/form-data")
    assert decrypt_resp.status_code == 200
    assert decrypt_resp.data == b"secret data"


def test_scan_missing_host(client):
    response = client.post("/api/scan", json={})
    assert response.status_code == 400

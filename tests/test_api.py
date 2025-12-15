import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import get_redis


class DummyRedis:
    def __init__(self):
        self.data = {}
        self.available = True

    async def get(self, key: str):
        return self.data.get(key)

    async def set(self, key: str, value: str, nx: bool = False, xx: bool = False):
        if not self.available:
            raise ConnectionError("Redis unavailable")
        exists = key in self.data
        if nx and exists:
            return None
        if xx and not exists:
            return None
        self.data[key] = value
        return True

    async def delete(self, key: str):
        if not self.available:
            raise ConnectionError("Redis unavailable")
        return 1 if self.data.pop(key, None) is not None else 0

    async def ping(self):
        if not self.available:
            raise ConnectionError("Redis unavailable")
        return True

    async def aclose(self):
        return None


@pytest.fixture
def dummy_redis():
    return DummyRedis()


@pytest.fixture
def client(dummy_redis):
    async def _override():
        return dummy_redis

    app.dependency_overrides[get_redis] = _override
    return TestClient(app)


def test_create_and_get(client):
    resp = client.post("/phones", json={"phone": "+12345678901", "address": "One"})
    assert resp.status_code == 201
    resp = client.get("/phones/+12345678901")
    assert resp.status_code == 200
    assert resp.json()["address"] == "One"


def test_create_duplicate(client):
    client.post("/phones", json={"phone": "+12345678902", "address": "Two"})
    resp = client.post("/phones", json={"phone": "+12345678902", "address": "Two"})
    assert resp.status_code == 409


def test_update_and_get(client):
    client.post("/phones", json={"phone": "+12345678903", "address": "Old"})
    resp = client.put("/phones/+12345678903", json={"address": "New"})
    assert resp.status_code == 200
    resp = client.get("/phones/+12345678903")
    assert resp.json()["address"] == "New"


def test_update_missing(client):
    resp = client.put("/phones/+12345678999", json={"address": "X"})
    assert resp.status_code == 404


def test_delete(client):
    client.post("/phones", json={"phone": "+12345678904", "address": "Addr"})
    resp = client.delete("/phones/+12345678904")
    assert resp.status_code == 204
    resp = client.get("/phones/+12345678904")
    assert resp.status_code == 404


def test_validation_errors(client):
    resp = client.post("/phones", json={"phone": "abc", "address": "A"})
    assert resp.status_code == 422
    resp = client.post("/phones", json={"phone": "+12345678905", "address": " "})
    assert resp.status_code == 422


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"redis": True}


def test_redis_unavailable(client, dummy_redis):
    dummy_redis.available = False
    resp = client.get("/phones/+12345678901")
    assert resp.status_code == 503


"""Fixtures: base de datos SQLite temporal, aislada del archivo ai_assistant.db real."""
import os
import tempfile

_DB_DIR = tempfile.mkdtemp(prefix="assistant-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_DIR}/test.db"
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def client():
    from main import app
    with TestClient(app) as c:
        yield c


_counter = {"n": 0}


@pytest.fixture()
def auth(client):
    """Registra un usuario nuevo y devuelve (headers, user_id)."""
    _counter["n"] += 1
    body = {"email": f"user{_counter['n']}@test.com", "password": "Test-pass-123", "full_name": f"Usuario {_counter['n']}"}
    r = client.post("/api/auth/register", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]["id"]

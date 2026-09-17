import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db, SemanticCacheEntry, SyncHistoryEntry
from backend.main import app

TEST_DB_PATH = "test_api_runner.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_lan_endpoint():
    res = client.get("/api/infrastructure/lan")
    assert res.status_code == 200
    data = res.json()
    assert data["hub_status"] == "online"
    assert "lan_url" in data


def test_lan_qr_endpoint():
    res = client.get("/api/infrastructure/lan/qr")
    assert res.status_code == 200
    data = res.json()
    assert "qr_code_base64" in data
    assert "lan_url" in data


def test_hardware_endpoint():
    res = client.get("/api/infrastructure/hardware")
    assert res.status_code == 200
    data = res.json()
    assert "ram_gb" in data
    assert "cpu_name" in data


def test_model_selection_endpoint():
    res = client.get("/api/infrastructure/model-selection")
    assert res.status_code == 200
    data = res.json()
    assert "configuration" in data
    assert "model" in data


def test_model_configurations_endpoint():
    res = client.get("/api/infrastructure/model-configurations")
    assert res.status_code == 200
    data = res.json()
    assert "low_resource" in data
    assert "standard" in data
    assert "performance" in data


def test_cache_endpoints_flow():
    # 1. Check stats empty
    stats_res = client.get("/api/infrastructure/cache/stats")
    assert stats_res.status_code == 200
    assert stats_res.json()["total_entries"] == 0

    # 2. Store approved entry
    store_res = client.post(
        "/api/infrastructure/cache/store",
        json={
            "question": "What causes rain?",
            "answer": "Rain is caused when water vapor condenses into water droplets in clouds.",
            "subject": "Science",
            "class_grade": "Grade 5",
            "approved": True
        }
    )
    assert store_res.status_code == 201
    entry = store_res.json()
    entry_id = entry["id"]

    # 3. Lookup question
    lookup_res = client.post(
        "/api/infrastructure/cache/lookup",
        json={
            "question": "What causes rain?",
            "subject": "Science",
            "class_grade": "Grade 5"
        }
    )
    assert lookup_res.status_code == 200
    lookup_data = lookup_res.json()
    assert lookup_data["hit"] is True
    assert "water droplets" in lookup_data["answer"]

    # 4. Delete entry
    del_res = client.delete(f"/api/infrastructure/cache/{entry_id}")
    assert del_res.status_code == 200

    # 5. Lookup again should miss
    lookup_res2 = client.post(
        "/api/infrastructure/cache/lookup",
        json={"question": "What causes rain?"}
    )
    assert lookup_res2.json()["hit"] is False


def test_hub_health_endpoint():
    res = client.get("/api/infrastructure/hub-health")
    assert res.status_code == 200
    data = res.json()
    assert data["hub"] == "online"
    assert data["offline_mode"] is True


def test_sync_endpoints():
    status_res = client.get("/api/infrastructure/sync/status")
    assert status_res.status_code == 200

    check_res = client.post("/api/infrastructure/sync/check")
    assert check_res.status_code == 200

    hist_res = client.get("/api/infrastructure/sync/history")
    assert hist_res.status_code == 200
    assert isinstance(hist_res.json(), list)

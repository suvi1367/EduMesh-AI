import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.infrastructure.sync_manager import (
    check_internet_available,
    validate_update,
    check_for_updates,
    record_sync_history,
    get_sync_history
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_check_internet_available():
    is_online = check_internet_available(timeout=0.2)
    assert isinstance(is_online, bool)


def test_validate_update_metadata():
    valid = {
        "version": "1.1.0",
        "component_type": "curriculum",
        "checksum_sha256": "abc123def4567890"
    }
    assert validate_update(valid) is True

    invalid_type = {
        "version": "1.1.0",
        "component_type": "malicious_script",
        "checksum_sha256": "abc123"
    }
    assert validate_update(invalid_type) is False

    missing_checksum = {
        "version": "1.1.0",
        "component_type": "model"
    }
    assert validate_update(missing_checksum) is False


def test_check_for_updates_offline_resilience(db_session):
    result = check_for_updates(db_session)
    assert isinstance(result, dict)
    assert "internet_available" in result
    assert "status" in result
    assert "current_manifest" in result


def test_record_and_get_sync_history(db_session):
    record_sync_history(
        db=db_session,
        sync_type="manual_check",
        status="success",
        details="Manual test sync check executed"
    )

    history = get_sync_history(db_session, limit=10)
    assert len(history) == 1
    assert history[0]["sync_type"] == "manual_check"
    assert history[0]["status"] == "success"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.infrastructure.semantic_cache import (
    cache_store,
    cache_lookup,
    approve_cache_entry,
    invalidate_cache_entry,
    get_cache_stats
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


def test_cache_miss_on_empty_db(db_session):
    result = cache_lookup(db_session, question="What is gravity?", threshold=0.85)
    assert result["hit"] is False
    assert result["answer"] is None
    assert result["similarity"] == 0.0


def test_cache_hit_and_similarity(db_session):
    # Store approved entry
    cache_store(
        db=db_session,
        question="What is photosynthesis in plants?",
        answer="Photosynthesis is the chemical process where green plants convert sunlight into energy.",
        subject="Science",
        class_grade="Grade 6",
        language="en",
        approved=True
    )

    # Lookup identical/similar question
    result = cache_lookup(
        db=db_session,
        question="What is photosynthesis in plants?",
        subject="Science",
        class_grade="Grade 6",
        threshold=0.80
    )

    assert result["hit"] is True
    assert result["similarity"] >= 0.80
    assert "chemical process" in result["answer"]
    assert result["cache_entry_id"] is not None


def test_unapproved_entry_rejection(db_session):
    # Store UNAPPROVED entry
    entry = cache_store(
        db=db_session,
        question="What is the capital of France?",
        answer="Paris",
        approved=False
    )

    # Lookup should MISS
    result = cache_lookup(db_session, question="What is the capital of France?", threshold=0.70)
    assert result["hit"] is False

    # Approve entry
    approve_cache_entry(db_session, entry.id)

    # Lookup should now HIT
    result2 = cache_lookup(db_session, question="What is the capital of France?", threshold=0.70)
    assert result2["hit"] is True
    assert result2["answer"] == "Paris"


def test_cache_invalidation(db_session):
    entry = cache_store(
        db=db_session,
        question="What is 2 + 2?",
        answer="4",
        approved=True
    )
    assert cache_lookup(db_session, "What is 2 + 2?", threshold=0.80)["hit"] is True

    # Invalidate
    deleted = invalidate_cache_entry(db_session, entry.id)
    assert deleted is True

    # Now lookup should miss
    assert cache_lookup(db_session, "What is 2 + 2?", threshold=0.80)["hit"] is False


def test_cache_stats(db_session):
    cache_store(db_session, "Q1", "A1", approved=True, response_latency_ms=10.0)
    cache_store(db_session, "Q2", "A2", approved=False, response_latency_ms=20.0)

    stats = get_cache_stats(db_session)
    assert stats["total_entries"] == 2
    assert stats["approved_entries"] == 1
    assert stats["unapproved_entries"] == 1
    assert stats["avg_cache_response_latency_ms"] == 15.0

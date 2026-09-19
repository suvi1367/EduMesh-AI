import math
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import SemanticCacheEntry


def _simple_deterministic_vector(text: str, dim: int = 128) -> List[float]:
    """
    Generates a deterministic unit-length feature vector for text matching.
    Provides fast, lightweight offline semantic-hash vectorization when heavyweight ML models are absent.
    """
    cleaned = re.sub(r'[^\w\s]', '', text.lower()).strip()
    words = cleaned.split()
    vector = [0.0] * dim
    if not words:
        return vector

    # Character n-grams and word hashing
    for word in words:
        for idx in range(len(word)):
            # Hash slice to index
            char_hash = hash(word[idx:idx+3]) % dim
            vector[char_hash] += 1.0

    # Calculate L2 norm and normalize to unit vector
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def compute_embedding(text: str) -> List[float]:
    """
    Computes embedding vector for input text.
    Uses sentence_transformers if available, else falls back to lightweight deterministic vectorizer.
    """
    try:
        from sentence_transformers import SentenceTransformer
        # If loaded globally or initialized
        if not hasattr(compute_embedding, "_model"):
            compute_embedding._model = SentenceTransformer("all-MiniLM-L6-v2")
        vec = compute_embedding._model.encode(text).tolist()
        return vec
    except Exception:
        return _simple_deterministic_vector(text, dim=128)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculates cosine similarity between two vector lists."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def cache_lookup(
    db: Session,
    question: str,
    subject: Optional[str] = None,
    class_grade: Optional[str] = None,
    language: Optional[str] = None,
    threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Performs semantic lookup in the cache.
    Returns answer only if similarity >= threshold and entry is approved.
    """
    q_embedding = compute_embedding(question)

    query = db.query(SemanticCacheEntry).filter(SemanticCacheEntry.approved == True)
    if subject:
        query = query.filter(SemanticCacheEntry.subject == subject)
    if class_grade:
        query = query.filter(SemanticCacheEntry.class_grade == class_grade)
    if language:
        query = query.filter(SemanticCacheEntry.language == language)

    entries = query.all()
    if not entries:
        return {
            "hit": False,
            "similarity": 0.0,
            "answer": None,
            "cache_entry_id": None
        }

    best_entry = None
    best_similarity = -1.0

    for entry in entries:
        if not entry.embedding:
            continue
        sim = cosine_similarity(q_embedding, entry.embedding)
        if sim > best_similarity:
            best_similarity = sim
            best_entry = entry

    if best_entry and best_similarity >= threshold:
        # Update statistics
        best_entry.hit_count += 1
        best_entry.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(best_entry)

        return {
            "hit": True,
            "similarity": round(best_similarity, 4),
            "answer": best_entry.answer,
            "cache_entry_id": best_entry.id,
            "evidence_metadata": best_entry.evidence_metadata or {},
            "subject": best_entry.subject,
            "class_grade": best_entry.class_grade,
            "language": best_entry.language
        }

    return {
        "hit": False,
        "similarity": round(max(0.0, best_similarity), 4),
        "answer": None,
        "cache_entry_id": None
    }


def cache_store(
    db: Session,
    question: str,
    answer: str,
    evidence_metadata: Optional[Dict[str, Any]] = None,
    subject: Optional[str] = None,
    class_grade: Optional[str] = None,
    language: Optional[str] = None,
    curriculum: Optional[str] = None,
    approved: bool = True,
    response_latency_ms: Optional[float] = None
) -> SemanticCacheEntry:
    """
    Stores a new Q&A pair in the semantic cache.
    """
    q_embedding = compute_embedding(question)
    entry = SemanticCacheEntry(
        question=question,
        embedding=q_embedding,
        answer=answer,
        evidence_metadata=evidence_metadata or {},
        subject=subject,
        class_grade=class_grade,
        language=language,
        curriculum=curriculum,
        approved=approved,
        created_at=datetime.utcnow(),
        last_used_at=datetime.utcnow(),
        hit_count=0,
        response_latency_ms=response_latency_ms or 0.0
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def approve_cache_entry(db: Session, entry_id: int) -> Optional[SemanticCacheEntry]:
    """Approves a cache entry so it can be served to students."""
    entry = db.query(SemanticCacheEntry).filter(SemanticCacheEntry.id == entry_id).first()
    if entry:
        entry.approved = True
        db.commit()
        db.refresh(entry)
    return entry


def invalidate_cache_entry(db: Session, entry_id: int) -> bool:
    """Deletes or invalidates a cache entry."""
    entry = db.query(SemanticCacheEntry).filter(SemanticCacheEntry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False


def get_cache_stats(db: Session) -> Dict[str, Any]:
    """Returns aggregated cache performance statistics."""
    total_entries = db.query(SemanticCacheEntry).count()
    approved_entries = db.query(SemanticCacheEntry).filter(SemanticCacheEntry.approved == True).count()
    unapproved_entries = total_entries - approved_entries

    entries = db.query(SemanticCacheEntry).all()
    total_hits = sum(e.hit_count for e in entries)
    
    avg_latency = 0.0
    latencies = [e.response_latency_ms for e in entries if e.response_latency_ms and e.response_latency_ms > 0]
    if latencies:
        avg_latency = round(sum(latencies) / len(latencies), 2)

    return {
        "total_entries": total_entries,
        "approved_entries": approved_entries,
        "unapproved_entries": unapproved_entries,
        "total_hits": total_hits,
        "avg_cache_response_latency_ms": avg_latency
    }

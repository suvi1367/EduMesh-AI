from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.infrastructure.lan_utils import get_lan_hub_info, generate_qr_code_base64
from app.infrastructure.hardware_profiler import get_hardware_profile
from app.infrastructure.model_selector import select_model, get_model_configurations
from app.infrastructure.semantic_cache import (
    cache_lookup,
    cache_store,
    approve_cache_entry,
    invalidate_cache_entry,
    get_cache_stats,
)
from app.infrastructure.sync_manager import (
    check_internet_available,
    check_for_updates,
    get_sync_history,
    load_sync_manifest,
)

router = APIRouter(prefix="/api/infrastructure", tags=["Infrastructure & Hub"])


# --- Request Pydantic Schemas ---

class CacheLookupRequest(BaseModel):
    question: str = Field(..., example="What is photosynthesis?")
    subject: Optional[str] = Field(None, example="Science")
    class_grade: Optional[str] = Field(None, example="Grade 6")
    language: Optional[str] = Field(None, example="en")
    threshold: Optional[float] = Field(0.85, ge=0.0, le=1.0)


class CacheStoreRequest(BaseModel):
    question: str = Field(..., example="What is photosynthesis?")
    answer: str = Field(..., example="Photosynthesis is the process by which plants use sunlight...")
    evidence_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    subject: Optional[str] = Field(None, example="Science")
    class_grade: Optional[str] = Field(None, example="Grade 6")
    language: Optional[str] = Field("en", example="en")
    curriculum: Optional[str] = Field(None, example="NCERT")
    approved: bool = Field(True)
    response_latency_ms: Optional[float] = Field(0.0)


# --- 1. LAN HUB DEPLOYMENT ENDPOINTS ---

@router.get("/lan")
def get_lan_status():
    """Returns classroom LAN IP address, access URLs, and network interfaces."""
    return get_lan_hub_info()


@router.get("/lan/qr")
def get_lan_qr_code():
    """Generates QR code for classroom LAN connection URL."""
    hub_info = get_lan_hub_info()
    lan_url = hub_info["lan_url"]
    qr_base64 = generate_qr_code_base64(lan_url)
    return {
        "lan_url": lan_url,
        "qr_code_base64": qr_base64
    }


# --- 2. HARDWARE PROFILER ENDPOINT ---

@router.get("/hardware")
def get_hardware_details():
    """Returns normalized host hardware profiling data (RAM, CPU, Storage, GPU)."""
    return get_hardware_profile()


# --- 3. SMART MODEL SELECTION ENDPOINTS ---

@router.get("/model-selection")
def get_selected_model_config():
    """Evaluates current hardware profile and returns recommended local model tier."""
    hw_profile = get_hardware_profile()
    return select_model(hw_profile)


@router.get("/model-configurations")
def list_available_model_configurations():
    """Returns registry of all supported model configurations (low_resource, standard, performance)."""
    return get_model_configurations()


# --- 4. SEMANTIC CACHE ENDPOINTS ---

@router.get("/cache/stats")
def get_semantic_cache_statistics(db: Session = Depends(get_db)):
    """Returns aggregate semantic cache performance metrics."""
    return get_cache_stats(db)


@router.post("/cache/lookup")
def perform_cache_lookup(payload: CacheLookupRequest, db: Session = Depends(get_db)):
    """
    Searches semantic cache for approved answers to student questions.
    Returns hit: true with answer if similarity >= threshold, else hit: false.
    """
    result = cache_lookup(
        db=db,
        question=payload.question,
        subject=payload.subject,
        class_grade=payload.class_grade,
        language=payload.language,
        threshold=payload.threshold or 0.85
    )
    return result


@router.post("/cache/store", status_code=status.HTTP_201_CREATED)
def store_cache_entry(payload: CacheStoreRequest, db: Session = Depends(get_db)):
    """Stores a new Q&A entry into the semantic answer cache."""
    entry = cache_store(
        db=db,
        question=payload.question,
        answer=payload.answer,
        evidence_metadata=payload.evidence_metadata,
        subject=payload.subject,
        class_grade=payload.class_grade,
        language=payload.language,
        curriculum=payload.curriculum,
        approved=payload.approved,
        response_latency_ms=payload.response_latency_ms
    )
    return entry.to_dict()


@router.post("/cache/{entry_id}/approve")
def approve_cache_item(entry_id: int, db: Session = Depends(get_db)):
    """Approves a pending cache entry for classroom access."""
    entry = approve_cache_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Cache entry {entry_id} not found.")
    return {"message": f"Cache entry {entry_id} approved successfully.", "entry": entry.to_dict()}


@router.delete("/cache/{entry_id}")
def delete_cache_item(entry_id: int, db: Session = Depends(get_db)):
    """Invalidates or removes an entry from the semantic cache."""
    success = invalidate_cache_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Cache entry {entry_id} not found.")
    return {"message": f"Cache entry {entry_id} deleted successfully."}


# --- 5. CLASSROOM SHARING & HUB HEALTH ---

@router.get("/hub-health")
def check_hub_health(db: Session = Depends(get_db)):
    """Returns basic health and offline readiness of Classroom Hub."""
    is_online = check_internet_available()
    return {
        "hub": "online",
        "offline_mode": True,
        "internet_available": is_online,
        "cache_available": True
    }


# --- 6. SYNC MANAGER ENDPOINTS ---

@router.get("/sync/status")
def get_sync_status():
    """Returns current internet availability and local sync manifest."""
    is_online = check_internet_available()
    manifest = load_sync_manifest()
    return {
        "internet_available": is_online,
        "status": "online" if is_online else "offline",
        "last_sync": manifest.get("last_sync"),
        "software_version": manifest.get("software_version"),
        "model_version": manifest.get("model_version"),
        "language_version": manifest.get("language_version"),
        "curriculum_version": manifest.get("curriculum_version"),
        "updates_count": len(manifest.get("updates_available", []))
    }


@router.post("/sync/check")
def trigger_sync_check(db: Session = Depends(get_db)):
    """Triggers an update check without blocking offline classroom operations."""
    return check_for_updates(db)


@router.get("/sync/history")
def list_sync_history(limit: int = 20, db: Session = Depends(get_db)):
    """Returns audit log of recent synchronization checks and events."""
    return get_sync_history(db, limit=limit)
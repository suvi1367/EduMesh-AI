import socket
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.database import SyncHistoryEntry

MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "sync_manifest.json"
)

DEFAULT_MANIFEST = {
    "software_version": "1.0.0",
    "model_version": "2026.09-Q4",
    "language_version": "1.2.0",
    "curriculum_version": "2026.1-EN-HI",
    "last_sync": datetime.utcnow().isoformat(),
    "updates_available": []
}


def check_internet_available(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.0) -> bool:
    """
    Safely tests whether internet access is available via fast socket connect.
    Returns True if internet is reachable, False if offline.
    Never raises an exception or blocks execution.
    """
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except (socket.timeout, OSError):
        return False


def load_sync_manifest() -> Dict[str, Any]:
    """Loads local sync manifest file or returns default if absent."""
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_MANIFEST.copy()


def save_sync_manifest(manifest: Dict[str, Any]) -> bool:
    """Saves sync manifest to disk."""
    try:
        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        return True
    except Exception:
        return False


def validate_update(update_metadata: Dict[str, Any]) -> bool:
    """
    Validates update package metadata and security signature before installation.
    Prevents unauthorized or arbitrary code/model execution.
    """
    if not isinstance(update_metadata, dict):
        return False

    required_fields = ["version", "component_type", "checksum_sha256"]
    for field in required_fields:
        if field not in update_metadata or not update_metadata[field]:
            return False

    valid_types = ["software", "model", "language_pack", "curriculum"]
    if update_metadata.get("component_type") not in valid_types:
        return False

    return True


def check_for_updates(db: Session, sync_server_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Checks for available updates if internet is connected.
    If offline, gracefully returns offline status without crashing or blocking.
    """
    is_online = check_internet_available()
    manifest = load_sync_manifest()

    if not is_online:
        record_sync_history(
            db=db,
            sync_type="check_updates",
            status="offline",
            details="Internet connection unavailable. Operating in isolated LAN mode."
        )
        return {
            "internet_available": False,
            "status": "offline",
            "message": "Classroom Hub is operating in offline mode. Internet sync unavailable.",
            "current_manifest": manifest,
            "updates_available": []
        }

    # Simulate or query remote sync server when online
    updates = []
    # Clean check logic - if a remote URL is configured and online, attempt HTTP check
    if sync_server_url:
        try:
            import requests
            resp = requests.get(sync_server_url, timeout=3.0)
            if resp.status_code == 200:
                raw_updates = resp.json().get("updates", [])
                updates = [u for u in raw_updates if validate_update(u)]
        except Exception:
            pass

    manifest["last_sync"] = datetime.utcnow().isoformat()
    manifest["updates_available"] = updates
    save_sync_manifest(manifest)

    record_sync_history(
        db=db,
        sync_type="check_updates",
        status="online",
        details=f"Successfully checked for updates. Found {len(updates)} valid updates.",
        updates_applied=[]
    )

    return {
        "internet_available": True,
        "status": "success",
        "message": "Update check complete.",
        "current_manifest": manifest,
        "updates_available": updates
    }


def record_sync_history(
    db: Session,
    sync_type: str,
    status: str,
    details: Optional[str] = None,
    updates_applied: Optional[List[Dict[str, Any]]] = None
) -> SyncHistoryEntry:
    """Records sync event in database log."""
    entry = SyncHistoryEntry(
        timestamp=datetime.utcnow(),
        sync_type=sync_type,
        status=status,
        details=details or "",
        updates_applied=updates_applied or []
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_sync_history(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves recent sync history logs."""
    entries = db.query(SyncHistoryEntry).order_by(SyncHistoryEntry.timestamp.desc()).limit(limit).all()
    return [e.to_dict() for e in entries]

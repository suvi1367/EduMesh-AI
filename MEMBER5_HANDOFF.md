# EduMesh AI — Member 5 Integration Handoff Checklist

This document provides concise integration instructions for Team Members 1–4 to incorporate the **Member 5 (Infrastructure, Deployment, Hardware Profiling, Semantic Cache, and Sync)** module into the main EduMesh AI repository.

---

## 1. Summary of Deliverables

### Files Created
- [`config/infrastructure_config.json`](file:///d:/EduMesh%20AI/config/infrastructure_config.json)
- [`backend/database.py`](file:///d:/EduMesh%20AI/backend/database.py)
- [`backend/infrastructure/__init__.py`](file:///d:/EduMesh%20AI/backend/infrastructure/__init__.py)
- [`backend/infrastructure/hardware_profiler.py`](file:///d:/EduMesh%20AI/backend/infrastructure/hardware_profiler.py)
- [`backend/infrastructure/model_selector.py`](file:///d:/EduMesh%20AI/backend/infrastructure/model_selector.py)
- [`backend/infrastructure/semantic_cache.py`](file:///d:/EduMesh%20AI/backend/infrastructure/semantic_cache.py)
- [`backend/infrastructure/sync_manager.py`](file:///d:/EduMesh%20AI/backend/infrastructure/sync_manager.py)
- [`backend/infrastructure/lan_utils.py`](file:///d:/EduMesh%20AI/backend/infrastructure/lan_utils.py)
- [`backend/api/infrastructure_routes.py`](file:///d:/EduMesh%20AI/backend/api/infrastructure_routes.py)
- [`backend/main.py`](file:///d:/EduMesh%20AI/backend/main.py)
- [`frontend/infrastructure_status.html`](file:///d:/EduMesh%20AI/frontend/infrastructure_status.html)
- [`scripts/start_hub.bat`](file:///d:/EduMesh%20AI/scripts/start_hub.bat)
- [`scripts/start_hub.ps1`](file:///d:/EduMesh%20AI/scripts/start_hub.ps1)
- [`tests/test_api.py`](file:///d:/EduMesh%20AI/tests/test_api.py)
- [`tests/test_hardware_profiler.py`](file:///d:/EduMesh%20AI/tests/test_hardware_profiler.py)
- [`tests/test_lan_hub.py`](file:///d:/EduMesh%20AI/tests/test_lan_hub.py)
- [`tests/test_model_selector.py`](file:///d:/EduMesh%20AI/tests/test_model_selector.py)
- [`tests/test_semantic_cache.py`](file:///d:/EduMesh%20AI/tests/test_semantic_cache.py)
- [`tests/test_sync_manager.py`](file:///d:/EduMesh%20AI/tests/test_sync_manager.py)
- [`README_MEMBER5.md`](file:///d:/EduMesh%20AI/README_MEMBER5.md)
- [`MEMBER5_HANDOFF.md`](file:///d:/EduMesh%20AI/MEMBER5_HANDOFF.md)
- [`.gitignore`](file:///d:/EduMesh%20AI/.gitignore)

---

## 2. Integration Checklist for Team Members

### How to Mount Member 5 Router into Existing FastAPI Application
If your team already has a central FastAPI `app` in `backend/main.py`:

```python
from backend.api.infrastructure_routes import router as infrastructure_router
from backend.database import init_db

# 1. Initialize tables on startup
@app.on_event("startup")
def startup():
    init_db()

# 2. Mount router
app.include_router(infrastructure_router)
```

### How to Wrap Existing Answer Generation Pipeline with Semantic Cache
In your question-answering handler (e.g., Member 2 RAG/LLM route):

```python
from backend.infrastructure.semantic_cache import cache_lookup, cache_store

@router.post("/ask")
def ask_question(question: str, subject: str = None, class_grade: str = None, db: Session = Depends(get_db)):
    # 1. Check semantic cache first
    cache_result = cache_lookup(db, question=question, subject=subject, class_grade=class_grade, threshold=0.85)
    if cache_result["hit"]:
        return {
            "source": "semantic_cache",
            "answer": cache_result["answer"],
            "cache_entry_id": cache_result["cache_entry_id"]
        }

    # 2. On miss, invoke existing RAG/LLM pipeline
    answer = generate_rag_llm_answer(question)  # Existing Member 2 pipeline

    # 3. Store new answer in cache for future students
    cache_store(db, question=question, answer=answer, subject=subject, class_grade=class_grade, approved=True)

    return {"source": "rag_llm", "answer": answer}
```

---

## 3. Dependencies Added

Add the following packages to `requirements.txt`:
```txt
fastapi>=0.115.0
uvicorn>=0.35.0
psutil>=7.0.0
sqlalchemy>=2.0.0
qrcode>=8.2.0
pillow>=12.0.0
requests>=2.32.0
pytest>=8.4.0
```

---

## 4. API Endpoints Added

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/infrastructure/lan` | GET | Retrieve LAN IP, binding host/port, network interfaces. |
| `/api/infrastructure/lan/qr` | GET | Base64 PNG QR code for LAN connection. |
| `/api/infrastructure/hardware` | GET | Host hardware profiler breakdown. |
| `/api/infrastructure/model-selection` | GET | Selected model tier (`low_resource`, `standard`, `performance`). |
| `/api/infrastructure/model-configurations` | GET | Available model configuration registry. |
| `/api/infrastructure/cache/stats` | GET | Cache hit rate & aggregate performance stats. |
| `/api/infrastructure/cache/lookup` | POST | Semantic similarity lookup. |
| `/api/infrastructure/cache/store` | POST | Store new Q&A pair in cache. |
| `/api/infrastructure/cache/{id}/approve` | POST | Approve pending cache entry. |
| `/api/infrastructure/cache/{id}` | DELETE | Invalidate cache entry. |
| `/api/infrastructure/hub-health` | GET | Offline Hub readiness health check. |
| `/api/infrastructure/sync/status` | GET | Internet availability & sync manifest. |
| `/api/infrastructure/sync/check` | POST | Non-blocking background update check. |
| `/api/infrastructure/sync/history` | GET | Audit log of sync checks. |

---

## 5. Environment Variables Added

- `EDUMESH_HOST` (default: `0.0.0.0`)
- `EDUMESH_PORT` (default: `8000`)
- `EDUMESH_DATABASE_URL` (default: `sqlite:///data/edumesh.db`)
- `EDUMESH_CACHE_THRESHOLD` (default: `0.85`)

---

## 6. Commands to Run & Test

### Run Server
```bash
python -m backend.main
```
or launch via PowerShell: `.\scripts\start_hub.ps1`

### Run Tests
```bash
pytest -v
```

---

## 7. Git Handoff Steps

1. Create a branch: `git checkout -b feature/member-5-infrastructure`
2. Add files: `git add backend/ config/ frontend/ scripts/ tests/ README_MEMBER5.md MEMBER5_HANDOFF.md .gitignore`
3. Commit: `git commit -m "feat(infrastructure): complete EduMesh AI Member 5 module"`
4. Merge to main branch via PR.

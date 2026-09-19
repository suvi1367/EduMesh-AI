# EduMesh AI — Backend

Central FastAPI backend for EduMesh AI. Owns the database, all classroom/question/document/approval/analytics APIs, teacher authentication, and now the merged infrastructure module (hardware profiling, model selection, semantic caching, sync management, LAN utilities).

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

## Running

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Local: http://localhost:8000
- LAN: http://<your-ip>:8000
- Interactive docs: http://localhost:8000/docs

## API areas

| Area | Prefix | Source |
|---|---|---|
| Auth | `/signup`, `/login` | Member 2 |
| Institutions/Classes/Subjects | `/institutions/*` | Member 2 |
| Classrooms | `/classrooms/*` | Member 2 |
| Documents | `/documents/*` | Member 2 |
| Questions | `/questions/*` | Member 2 |
| Approvals | `/answers/*` | Member 2 |
| Analytics | `/analytics/*` | Member 2 |
| Infrastructure & Hub | `/api/infrastructure/*` | Member 5 (merged) |

### Infrastructure & Hub endpoints (Member 5, merged into this backend)

- `GET /api/infrastructure/lan` — LAN IP, local/LAN URLs, network interfaces
- `GET /api/infrastructure/lan/qr` — QR code for classroom LAN join URL
- `GET /api/infrastructure/hardware` — detected RAM, CPU, storage, GPU
- `GET /api/infrastructure/model-selection` — recommended model tier based on hardware
- `GET /api/infrastructure/model-configurations` — all supported model tiers
- `GET /api/infrastructure/cache/stats` — semantic cache performance metrics
- `POST /api/infrastructure/cache/lookup` — semantic similarity search for approved answers
- `POST /api/infrastructure/cache/store` — store a new Q&A pair in the semantic cache
- `POST /api/infrastructure/cache/{id}/approve` — approve a pending cache entry
- `DELETE /api/infrastructure/cache/{id}` — remove a cache entry
- `GET /api/infrastructure/hub-health` — offline readiness check
- `GET /api/infrastructure/sync/status` — internet availability + sync manifest
- `POST /api/infrastructure/sync/check` — trigger an update check
- `GET /api/infrastructure/sync/history` — recent sync event log

## Database

SQLite at `data/edumesh.db`, 16 tables total (13 core + `session_participants` + `semantic_cache_entries` + `sync_history_log`). Auto-created on first run.

## Integration notes

- `app/infrastructure/` contains Member 5's hardware/LAN/model-selection/cache/sync logic, adapted to import from `app.models`/`app.database` instead of a standalone app.
- `app/services/rag_client.py` still returns a mock answer pending Member 3's real RAG service — swap the function body once ready (real implementation already commented in the file).
- The exact-text `cache_entries` table (Phase 6 approval flow) and the semantic `semantic_cache_entries` table (Member 5) currently coexist. `/questions/ask` uses the simple exact-match cache; `/api/infrastructure/cache/*` uses the semantic one. Migrating `/questions/ask` to use semantic matching is a follow-up task.

## Known limitations

- Teacher auth is minimal (username/password, no session tokens/JWT).
- RAG answers are mocked pending Member 3's generation step.
- Two cache systems currently coexist (see integration notes above).
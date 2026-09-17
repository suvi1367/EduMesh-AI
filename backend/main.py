import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from backend.database import init_db
from backend.api.infrastructure_routes import router as infrastructure_router
from backend.infrastructure.lan_utils import get_lan_hub_info, get_local_lan_ip
from backend.infrastructure.sync_manager import check_internet_available

app = FastAPI(
    title="EduMesh AI Classroom Hub",
    description="Offline, Multilingual, Curriculum-Aware AI Hub for Low-Resource Classrooms (Member 5 Infrastructure)",
    version="1.0.0"
)

# Enable CORS for local classroom LAN devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Mount infrastructure routes
app.include_router(infrastructure_router)

# Mount frontend static directory if exists
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    """Serves the Hub Status UI or redirects to status page."""
    status_page = os.path.join(FRONTEND_DIR, "infrastructure_status.html")
    if os.path.exists(status_page):
        return FileResponse(status_page)
    return {
        "service": "EduMesh AI Classroom Hub",
        "status": "online",
        "lan_url": f"http://{get_local_lan_ip()}:8000",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    host = os.getenv("EDUMESH_HOST", "0.0.0.0")
    port = int(os.getenv("EDUMESH_PORT", 8000))
    lan_ip = get_local_lan_ip()
    internet_status = "AVAILABLE" if check_internet_available() else "OFFLINE"

    print("=" * 60)
    print("EduMesh AI Hub")
    print("Status: ONLINE")
    print(f"LAN URL: http://{lan_ip}:{port}")
    print(f"Local URL: http://localhost:{port}")
    print(f"Internet: {internet_status}")
    print("=" * 60)

    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

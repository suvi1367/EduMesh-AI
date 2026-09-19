import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import init_db
from app.logging_conf import setup_logging
from app.routers import institutions, classrooms, documents, questions, approvals, analytics, auth, infrastructure

setup_logging()
logger = logging.getLogger("edumesh")

app = FastAPI(title="EduMesh AI Backend")

@app.on_event("startup")
def startup():
    logger.info("Starting up EduMesh AI Backend...")
    init_db()
    logger.info("Database initialized successfully.")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact the backend team."},
    )

app.include_router(auth.router)
app.include_router(institutions.router)
app.include_router(classrooms.router)
app.include_router(documents.router)
app.include_router(questions.router)
app.include_router(approvals.router)
app.include_router(analytics.router)
app.include_router(infrastructure.router)

@app.get("/health")
def health():
    return {"status": "ok"}
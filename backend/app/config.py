import os

class Settings:
    DATA_DIR = os.getenv("EDUMESH_DATA_DIR", "./data")
    DB_PATH = os.getenv("EDUMESH_DB_PATH", "./data/edumesh.db")
    DOCS_DIR = os.getenv("EDUMESH_DOCS_DIR", "./data/documents")
    RAG_SERVICE_URL = os.getenv("EDUMESH_RAG_URL", "http://localhost:9000")
    MAX_UPLOAD_MB = int(os.getenv("EDUMESH_MAX_UPLOAD_MB", "50"))

settings = Settings()
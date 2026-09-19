import random

async def ask_rag(question_text: str, subject_id: int, language: str = "en"):
    """
    STUB / MOCK implementation.
    Once the AI/RAG teammate's real service is ready, replace this
    function's body with an actual HTTP call to their endpoint
    (see commented example at the bottom of this file).
    """
    return {
        "answer": f"[MOCK ANSWER] This is a placeholder response to: '{question_text}'",
        "language": language,
        "style": "explanatory",
        "verified": random.choice([True, False]),
        "verification_status": random.choice(["verified", "pending", "failed"]),
        "sources": [
            {"chapter": "Chapter 3", "page": 42},
            {"chapter": "Chapter 4", "page": 51},
        ],
    }


# ---- Real implementation (uncomment and use once AI/RAG service is ready) ----
# import httpx
# from app.config import settings
#
# async def ask_rag(question_text: str, subject_id: int, language: str = "en"):
#     async with httpx.AsyncClient(timeout=30) as client:
#         resp = await client.post(f"{settings.RAG_SERVICE_URL}/query", json={
#             "question": question_text,
#             "subject_id": subject_id,
#             "language": language,
#         })
#         resp.raise_for_status()
#         return resp.json()
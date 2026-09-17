import numpy as np
from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Below this cosine similarity, we don't trust the answer is grounded
SUPPORT_THRESHOLD = 0.30


def verify_answer(answer, evidence_chunks):
    """
    Checks whether the LLM's answer is semantically supported by
    at least one retrieved evidence chunk.

    Returns a dict with status and details. This is NOT mathematical
    proof of truth — it's a similarity heuristic to catch answers that
    drift away from the retrieved evidence.
    """
    if answer.strip().startswith("INSUFFICIENT EVIDENCE"):
        return {
            "status": "insufficient_evidence",
            "best_similarity": None,
            "note": "Model itself reported insufficient evidence."
        }

    answer_embedding = embed_model.encode([answer], convert_to_numpy=True)[0]

    best_score = -1.0
    best_chunk_id = None

    for chunk in evidence_chunks:
        chunk_embedding = embed_model.encode([chunk["text"][:800]], convert_to_numpy=True)[0]

        # cosine similarity
        score = np.dot(answer_embedding, chunk_embedding) / (
            np.linalg.norm(answer_embedding) * np.linalg.norm(chunk_embedding)
        )

        if score > best_score:
            best_score = score
            best_chunk_id = chunk["chunk_id"]

    if best_score >= SUPPORT_THRESHOLD:
        status = "supported"
    else:
        status = "needs_review"

    return {
        "status": status,
        "best_similarity": float(best_score),
        "best_matching_chunk_id": best_chunk_id,
        "note": "Similarity-based heuristic, not proof of factual correctness."
    }
"""
Similarity Service for EduMesh AI
-----------------------------------
This module exposes question-embedding and similarity-checking
functionality for use by other modules (e.g. Member 5's local-LAN
answer caching system).

Usage by another module:
    from similarity_service import SimilarityService

    service = SimilarityService()
    embedding = service.embed_question("What is the SI unit of length?")
    is_match = service.is_similar(
        "What is the SI unit of length?",
        "What unit is used to measure length?",
        threshold=0.85
    )

KNOWN LIMITATION (see test_similarity.py for full results):
Testing on real question pairs showed that similarity threshold alone
is NOT reliable for cache-matching decisions:

- FALSE POSITIVE (dangerous): "What is photosynthesis?" vs
  "What is not photosynthesis?" scored 0.9071 similarity — well above
  a typical 0.85 threshold — despite requiring opposite answers.
  Caching on this match would serve a wrong answer.

- FALSE NEGATIVE (inefficient): "What is the SI unit of length?" vs
  "What unit is used to measure length?" scored only 0.7023 despite
  being the same question rephrased. A threshold high enough to avoid
  the false positive above will miss this legitimate cache hit.

RECOMMENDATION for Member 5: Do not rely on similarity score alone for
cache hits on negated or short questions. Consider combining this score
with simple keyword checks (e.g. detecting "not", "isn't", "except")
before trusting a high-similarity cache match.
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class SimilarityService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_question(self, question: str) -> np.ndarray:
        """
        Converts a question into an embedding vector.
        Member 5's cache can store this vector alongside the cached answer.
        """
        return self.model.encode([question], convert_to_numpy=True)[0]

    def cosine_similarity(self, embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
        """Returns cosine similarity between two embedding vectors (-1 to 1)."""
        return float(
            np.dot(embedding_a, embedding_b) /
            (np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b))
        )

    def is_similar(self, question_a: str, question_b: str, threshold: float = 0.85) -> bool:
        """
        Checks if two questions are similar enough to be treated as
        the same cached question. Threshold is configurable by the
        caller (Member 5) depending on how strict the cache should be.

        NOTE: High textual/topical similarity does not guarantee the
        same correct answer applies to both questions. See known
        false-positive cases documented in test_similarity.py.
        """
        emb_a = self.embed_question(question_a)
        emb_b = self.embed_question(question_b)
        score = self.cosine_similarity(emb_a, emb_b)
        return score >= threshold

    def similarity_score(self, question_a: str, question_b: str) -> float:
        """Returns the raw similarity score without applying a threshold."""
        emb_a = self.embed_question(question_a)
        emb_b = self.embed_question(question_b)
        return self.cosine_similarity(emb_a, emb_b)
from similarity_service import SimilarityService

service = SimilarityService()

test_pairs = [
    ("What is the SI unit of length?", "What unit is used to measure length?", True),
    ("What is a mixture?", "Define mixture.", True),
    ("What is photosynthesis?", "What is not photosynthesis?", False),
    ("Is air a mixture?", "Is air a pure substance?", False),
]

print("Testing question similarity pairs:\n")

for q1, q2, expected_match in test_pairs:
    score = service.similarity_score(q1, q2)
    is_match_085 = score >= 0.85

    print(f"Q1: {q1}")
    print(f"Q2: {q2}")
    print(f"Similarity score: {score:.4f}")
    print(f"Expected to match: {expected_match} | At threshold 0.85, matched: {is_match_085}")

    if is_match_085 != expected_match:
        print("⚠️  MISMATCH - this pair behaves differently than expected. Document this case.")

    print()
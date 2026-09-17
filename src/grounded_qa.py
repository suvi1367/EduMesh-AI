import json
import re
import subprocess
import faiss
from sentence_transformers import SentenceTransformer
from verify import verify_answer

INDEX_FILE = "vector_store/index.faiss"
METADATA_FILE = "vector_store/metadata.json"
MODEL_NAME = "qwen2.5:1.5b"

print("Loading FAISS index...")
index = faiss.read_index(INDEX_FILE)

print("Loading metadata...")
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query, top_k=3):
    query_embedding = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx < 0:
            continue
        results.append({
            "chunk_id": chunks[idx]["chunk_id"],
            "chapter": chunks[idx].get("chapter", "unknown"),
            "pages": chunks[idx].get("pages", []),
            "text": chunks[idx]["text"],
            "distance": float(distance)
        })
    return results

def build_prompt(question, evidence_chunks):
    evidence_text = ""
    for i, chunk in enumerate(evidence_chunks, start=1):
        evidence_text += f"\n[Evidence {i} - Chapter: {chunk['chapter']}, Page(s): {chunk['pages']}]\n{chunk['text'][:800]}\n"

    prompt = f"""You are a strict textbook assistant. You must answer using ONLY facts, sentences, and examples that are explicitly written in the Evidence below. 

Rules:
- Do NOT add any example, fact, or explanation that is not directly present in the Evidence text.
- Do NOT use general knowledge, even if it seems related or correct.
- If the Evidence does not fully answer the question, respond with exactly: "INSUFFICIENT EVIDENCE: I cannot find this in the textbook."
- Keep your answer short and directly tied to specific sentences in the Evidence.

Evidence:
{evidence_text}

Student's Question: {question}

Answer using ONLY the Evidence above (no outside examples):"""
    return prompt


def ask_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", MODEL_NAME, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60
    )
    return result.stdout.strip()


def grounded_answer(question):
    print(f"\nRetrieving evidence for: '{question}'...")
    evidence_chunks = retrieve(question, top_k=3)

    print("Generating grounded answer...")
    prompt = build_prompt(question, evidence_chunks)
    answer = ask_llm(prompt)

    print("\n===== GROUNDED ANSWER =====\n")
    print(answer)

    print("\n===== SOURCES =====")
    for chunk in evidence_chunks:
        print(f"- Chapter: {chunk['chapter']}, Page(s): {chunk['pages']} (Chunk {chunk['chunk_id']}, distance {chunk['distance']:.4f})")

    verification = verify_answer(answer, evidence_chunks)
    print("\n===== VERIFICATION =====")
    print(f"Status: {verification['status']}")
    if verification['best_similarity'] is not None:
        print(f"Best similarity to evidence: {verification['best_similarity']:.4f}")
    print(f"Note: {verification['note']}")

    if verification['status'] == 'needs_review':
        print("\n⚠️  This answer should be routed to a teacher for review.")

    return answer, evidence_chunks, verification


if __name__ == "__main__":
    question = input("\nEnter your question: ")
    grounded_answer(question)
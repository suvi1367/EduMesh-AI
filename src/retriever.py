import json
import faiss
from sentence_transformers import SentenceTransformer

INDEX_FILE = "vector_store/index.faiss"
METADATA_FILE = "vector_store/metadata.json"

# Load FAISS index
print("Loading FAISS index...")
index = faiss.read_index(INDEX_FILE)

# Load chunk metadata
print("Loading metadata...")
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query, top_k=3):
    # Convert the question into an embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_embedding, top_k)

    results = []

    for distance, idx in zip(distances[0], indices[0]):
        if idx < 0:
            continue

        results.append({
            "chunk_id": chunks[idx]["chunk_id"],
            "document": chunks[idx].get("document", "unknown"),
            "subject": chunks[idx].get("subject", "unknown"),
            "class": chunks[idx].get("class", "unknown"),
            "chapter": chunks[idx].get("chapter", "unknown"),
            "pages": chunks[idx].get("pages", []),
            "text": chunks[idx]["text"],
            "distance": float(distance)
        })

    return results


# Test the retriever
question = input("\nEnter your question: ")

results = search(question)

print("\n===== SEARCH RESULTS =====\n")

for i, result in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print(f"Chunk ID: {result['chunk_id']}")
    print(f"Chapter: {result['chapter']} | Pages: {result['pages']}")
    print(f"Distance: {result['distance']:.4f}")
    print(result["text"][:1000])
    print()
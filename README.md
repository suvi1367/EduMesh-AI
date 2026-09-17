# EduMesh AI — Member 3 Module
Curriculum Processing, RAG, Local LLM & Verification

## What this module does
Takes a curriculum PDF, indexes it, retrieves relevant chunks for a student's
question, generates a grounded answer using a local LLM, verifies the answer
against evidence, and exposes similarity-checking for Member 5's cache.

## Setup (run once)

1. Install Python 3.11+
2. Create and activate a virtual environment:
3. Install dependencies:
4. Install Ollama (local LLM runtime): https://ollama.com
5. Pull the model:

## Pipeline — run in this order

| Step | Script | Input | Output |
|---|---|---|---|
| 1. Extract text | `python src/extract_text.py` | `sample.pdf` | `extracted_raw.txt`, `extracted_clean.txt` |
| 2. Chunk text | `python src/chunker.py` | `extracted_clean.txt` | `chunks.json` |
| 3. Generate embeddings | `python src/embedder.py` | `chunks.json` | `vector_store/index.faiss`, `vector_store/metadata.json` |
| 4. Enrich metadata | `python src/enrich_metadata.py` | `vector_store/metadata.json` | `vector_store/metadata.json` (adds chapter/page/subject/class) |
| 5. Test retrieval | `python src/retriever.py` | question (typed) | top-k relevant chunks |
| 6. Benchmark LLM | `python src/benchmark_llm.py` | — | RAM/CPU/response time |
| 7. Ask a grounded question | `python src/grounded_qa.py` | question (typed) | answer + sources + verification status |
| 8. Test similarity edge cases | `python src/test_similarity.py` | — | prints known false-positive/negative pairs |

## Main interfaces for other members

### For Member 5 (caching) — `src/similarity_service.py`
```python
from similarity_service import SimilarityService

service = SimilarityService()
embedding = service.embed_question("some question")
is_match = service.is_similar(question_a, question_b, threshold=0.85)
```
**Known limitation:** see docstring in `similarity_service.py` — similarity
score alone can misfire on negated questions (e.g. "what is X" vs "what is
not X"). Do not use for cache-hit decisions without a secondary check.

### For any member needing grounded answers — `src/grounded_qa.py`
```python
from grounded_qa import grounded_answer

answer, sources, verification = grounded_answer("What is the SI unit of length?")
```
Returns:
- `answer` (str): the LLM's response, or `"INSUFFICIENT EVIDENCE: ..."` if unsupported
- `sources` (list): each with `chunk_id`, `chapter`, `pages`, `text`, `distance`
- `verification` (dict): `status` (`supported` / `needs_review` / `insufficient_evidence`), `best_similarity`, `note`

## Models used
- Embedding: `all-MiniLM-L6-v2` (via sentence-transformers)
- LLM: `qwen2.5:1.5b` (via Ollama) — measured 1.2 GB RAM, ~10s response time on 8GB machine (see benchmark_llm.py output)

## Known limitations (documented honestly, not hidden)
1. Verification (Phase 6) uses embedding similarity as a heuristic — it can
   miss topically-similar hallucinations (see test results in project notes).
   Threshold set to 0.30 after calibration against real Q&A pairs.
2. Similarity service (Phase 7) can false-positive-match negated questions
   with high similarity scores — see docstring for details.
3. Chapter/page boundaries in metadata were manually calibrated against
   this specific PDF's page numbering; a different PDF will need re-calibration
   of the `CHAPTERS` list in `enrich_metadata.py`.

## File structure

## Do NOT commit to GitHub
- `venv/` folder
- `sample.pdf` if it contains licensed textbook content — check with team
- `vector_store/index.faiss` if large — consider regenerating from chunks.json instead
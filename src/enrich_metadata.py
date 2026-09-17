import json
import re

METADATA_FILE = "vector_store/metadata.json"
OUTPUT_FILE = "vector_store/metadata.json"  # overwrite in place

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

CHAPTERS = [
    (1, 17, "Measurements"),
    (18, 37, "Force and Motion"),
    (38, 58, "Matter Around Us"),
    (59, 71, "The World of Plants"),
    (72, 83, "The World of Animals"),
    (84, 99, "Health and Hygiene"),
    (100, 108, "Computer - An Introduction"),
]

def get_pages(text):
    matches = re.findall(r'---\s*Page\s*(\d+)\s*---', text)
    return [int(m) for m in matches]

def get_chapter(page_num):
    for start, end, name in CHAPTERS:
        if start <= page_num <= end:
            return name
    return "Unknown"

enriched = []

for chunk in chunks:
    pages = get_pages(chunk["text"])
    primary_page = pages[0] if pages else None

    enriched_chunk = {
        "chunk_id": chunk["chunk_id"],
        "document": "6th_Science_Term1.pdf",
        "subject": "Science",
        "class": "6",
        "chapter": get_chapter(primary_page) if primary_page else "Unknown",
        "pages": pages,
        "text": chunk["text"]
    }
    enriched.append(enriched_chunk)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)

print(f"Enriched {len(enriched)} chunks with metadata.")
print(f"\nExample (chunk 1):")
print(json.dumps(enriched[1], indent=2, ensure_ascii=False)[:500])
import json
import re

INPUT_FILE = "extracted_clean.txt"
OUTPUT_FILE = "chunks.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def create_chunks(text, page_number):
    words = text.split()
    chunks = []

    start = 0
    chunk_id = 0

    while start < len(words):
        end = start + CHUNK_SIZE

        chunk_text = " ".join(words[start:end])

        chunks.append({
            "chunk_id": chunk_id,
            "page": page_number,
            "text": chunk_text
        })

        chunk_id += 1
        start = end - CHUNK_OVERLAP

    return chunks


# Read the page-aware extracted text
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    full_text = f.read()


# Split the document using the page markers
pages = re.split(r"--- Page (\d+) ---", full_text)

all_chunks = []

# pages looks like:
# [text_before_page, page_number, page_text, page_number, page_text, ...]

for i in range(1, len(pages), 2):

    page_number = int(pages[i])
    page_text = pages[i + 1]

    page_text = clean_text(page_text)

    if not page_text:
        continue

    page_chunks = create_chunks(page_text, page_number)

    all_chunks.extend(page_chunks)


# Give every chunk a unique ID
for new_id, chunk in enumerate(all_chunks):
    chunk["chunk_id"] = new_id


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        all_chunks,
        f,
        indent=2,
        ensure_ascii=False
    )


print(f"Created {len(all_chunks)} chunks.")
print("Saved to:", OUTPUT_FILE)

if all_chunks:
    print("\nExample chunk:")
    print(json.dumps(all_chunks[0], indent=2, ensure_ascii=False))
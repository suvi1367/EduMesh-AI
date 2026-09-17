import fitz
import re

doc = fitz.open("sample.pdf")
print(f"This PDF has {len(doc)} pages.\n")

# Patterns that match junk lines we want to remove
junk_patterns = [
    r'.*\.indd\s+\d+\s*$',           # e.g. "6th Science_EM_Unit 1.indd   1"
    r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}[.:]\d{2}[.:]\d{2}\s*(AM|PM)?\s*$',  # timestamps
    r'^www\.\S+\.(in|com|org)\s*$',   # website lines
]

def is_junk_line(line):
    line = line.strip()
    if not line:
        return False
    for pattern in junk_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    return False

def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not is_junk_line(line)]
    return '\n'.join(cleaned_lines)

all_pages = []

for page_number in range(len(doc)):
    page = doc[page_number]
    raw_text = page.get_text()
    cleaned = clean_text(raw_text)
    all_pages.append(cleaned)

doc.close()

with open("extracted_clean.txt", "w", encoding="utf-8") as f:
    for i, text in enumerate(all_pages):
        f.write(f"--- Page {i + 1} ---\n")
        f.write(text)
        f.write("\n\n")

print("Done! Check extracted_clean.txt")
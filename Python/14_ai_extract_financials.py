import fitz
import os

PDF = "Data/downloaded_reports/Commonwealth Bank Australia/2025.pdf"

OUTPUT = "Data/Extracted/2025_financial_pages.txt"

KEYWORDS = [

    "financial highlights",
    "five-year financial summary",
    "statement of financial position",
    "consolidated balance sheet",
    "balance sheet",
    "statement of profit or loss",
    "income statement",
    "statement of comprehensive income",
    "key financial data",
    "net profit after tax",
    "total assets",
    "shareholders' equity",
    "deposits",
    "loans and advances"

]

doc = fitz.open(PDF)

pages_to_keep = []

for page_number, page in enumerate(doc):

    text = page.get_text()

    lower = text.lower()

    if any(keyword in lower for keyword in KEYWORDS):

        pages_to_keep.append((page_number + 1, text))

doc.close()

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:

    for page, text in pages_to_keep:

        f.write("=" * 80 + "\n")
        f.write(f"PAGE {page}\n")
        f.write("=" * 80 + "\n\n")
        f.write(text)
        f.write("\n\n")

print(f"Found {len(pages_to_keep)} relevant pages.")
print(f"Saved to {OUTPUT}")
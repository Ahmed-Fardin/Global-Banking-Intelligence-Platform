import csv


import xml.etree.ElementTree as ET
from pathlib import Path

# ==========================================
# GLEIF XML FILE
# ==========================================

GLEIF_FILE = Path("Data/Raw/20260726-gleif-concatenated-file-lei2.xml")

print("=" * 60)
print("GBIP - GLEIF XML Explorer")
print("=" * 60)

# ==========================================
# READ ONLY THE FIRST FEW XML EVENTS
# ==========================================

output_file = "Data/processed/gleif_preview.csv"

csv_file = open(output_file, "w", newline="", encoding="utf-8")

writer = csv.DictWriter(
    csv_file,
    fieldnames=[
        "lei_code",
        "legal_name",
        "country",
        "city",
        "legal_jurisdiction",
        "entity_status"
    ]
)

writer.writeheader()

count = 0

context = ET.iterparse(GLEIF_FILE, events=("start", "end"))

# ==========================================
# FIND THE FIRST LEI RECORD
# ==========================================

for event, element in context:

    tag = element.tag.split("}")[-1]

    if event == "end" and tag == "LEIRecord":

        ns = {"g": "http://www.gleif.org/data/schema/leidata/2016"}

        record = {
            "lei_code": element.findtext("g:LEI", namespaces=ns),
            "legal_name": element.findtext("g:Entity/g:LegalName", namespaces=ns),
            "country": element.findtext("g:Entity/g:HeadquartersAddress/g:Country", namespaces=ns),
            "city": element.findtext("g:Entity/g:HeadquartersAddress/g:City", namespaces=ns),
            "legal_jurisdiction": element.findtext("g:Entity/g:LegalJurisdiction", namespaces=ns),
            "entity_status": element.findtext("g:Entity/g:EntityStatus", namespaces=ns),
        }

        writer.writerow(record)

        count += 1

        if count >= 100:
            break


csv_file.close()

print(f"Exported {count} records to {output_file}")
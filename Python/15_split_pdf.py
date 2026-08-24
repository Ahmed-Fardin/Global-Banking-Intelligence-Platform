import fitz
import os

PDF_FOLDER = "Data/downloaded_reports"
OUTPUT_FOLDER = "Data/Extracted_Text"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def pdf_to_text(pdf_path, output_path):

    print(f"\nReading: {os.path.basename(pdf_path)}")

    doc = fitz.open(pdf_path)

    text = []

    for page in doc:
        text.append(page.get_text())

    doc.close()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text))

    print(f"Saved: {output_path}")


for root, dirs, files in os.walk(PDF_FOLDER):

    for file in files:

        if not file.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(root, file)

        bank_name = os.path.basename(root)

        bank_output_folder = os.path.join(
            OUTPUT_FOLDER,
            bank_name
        )

        os.makedirs(bank_output_folder, exist_ok=True)

        output_file = os.path.splitext(file)[0] + ".txt"

        output_path = os.path.join(
            bank_output_folder,
            output_file
        )

        pdf_to_text(
            pdf_path,
            output_path
        )

print("\n===================================")
print("ALL PDFS CONVERTED")
print("===================================")
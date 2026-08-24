"""
===========================================================
Global Banking Intelligence Platform (GBIP)

Script:
11_extract_financials_from_pdf.py

Purpose:
Extract standardized financial metrics from official
bank annual reports.

Author:
Fardin Ahmed

CHANGES IN THIS VERSION:
- extract_pdf_pages() now falls back to local OCR (Tesseract, via
  pytesseract + pdf2image) when a page has little/no native text —
  i.e. scanned PDFs. Free, no API, runs locally.
- extract_metric_from_text() now matches aliases even when spacing is
  off (e.g. OCR turning "Total Assets" into "TotalAssets"), which was
  silently failing before.
===========================================================
"""

# ==========================
# IMPORTS
# ==========================

import re
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_path


# ==========================
# FINANCIAL METRIC ALIASES
# ==========================

METRIC_ALIASES = {

    "total_assets": [
        "Total Assets",
        "Assets",
        "Group Total Assets"
    ],

    "total_deposits": [
        "Customer Deposits",
        "Deposits from Customers",
        "Total Deposits"
    ],

    "total_loans": [
        "Group Loans",
        "Loans",
        "Loans and Advances",
        "Gross Loans",
        "Gross Financing",
        "Financing",
        "Net Loans"
    ],

    "shareholders_equity": [
        "Total Equity",
        "Shareholders' Equity",
        "Total Shareholders' Equity",
        "Equity Attributable to Owners"
    ],

    "operating_income": [
        "Operating Income",
        "Total Operating Income",
        "Operating Revenue"
    ],

    "operating_expenses": [
        "Operating Expenses",
        "Total Operating Expenses",
        "Operating Costs"
    ],

    "net_income": [
        "Net Income",
        "Net Profit",
        "Profit After Tax",
        "Profit for the Financial Year",
        "Profit Attributable to Equity Holders"
    ],

    "roe_percent": [
        "ROE",
        "Return on Equity"
    ],

    "roa_percent": [
        "ROA",
        "Return on Assets"
    ],

    "capital_adequacy_percent": [
        "Capital Adequacy Ratio",
        "CAR",
        "Total Capital Ratio"
    ],

    "cost_income_ratio": [
        "Cost to Income Ratio",
        "Cost-Income Ratio"
    ],

    "loan_to_deposit_ratio": [
        "Loan to Deposit Ratio",
        "LDR"
    ],

    "npl_ratio": [
        "Gross Impaired Loans Ratio",
        "Gross NPL Ratio",
        "Non Performing Loan Ratio",
        "NPL Ratio"
    ],

    "employees": [
        "Employees",
        "Number of Employees",
        "Staff"
    ],

    "branches": [
        "Branches",
        "Network",
        "Domestic Branches"
    ]
}


# ==========================
# SEARCH TERMS
# ==========================

SEARCH_TERMS = [

    # Financial Position
    "Total Assets",
    "Loans",
    "Loans and Advances",
    "Deposits",
    "Deposits from Customers",
    "Shareholders' Equity",

    # Profitability
    "Operating Income",
    "Operating Revenue",
    "Net Income",
    "Profit After Tax",

    # Ratios
    "Return on Equity",
    "ROE",
    "Return on Assets",
    "ROA",
    "Capital Ratio",
    "Cost to Income",
    "Loan to Deposit",
    "NPL",

    # Common Titles
    "Financial Highlights",
    "Financial Performance",
    "Five-Year"
]


# ==========================
# OCR CONFIG
# ==========================

# If a page's native text layer has fewer real characters than this,
# treat it as scanned/image-only and OCR it instead.
MIN_CHARS_FOR_TEXT_PAGE = 30

# OCR is slow (~1-3s/page). Cap how many pages we're willing to OCR
# per report so one giant scanned PDF doesn't hang the whole run.
OCR_MAX_PAGES = 40


def _ocr_page(pdf_path, page_number):
    """Rasterize a single page and run local Tesseract OCR on it."""
    try:
        images = convert_from_path(
            pdf_path,
            dpi=200,
            first_page=page_number,
            last_page=page_number,
        )
        if not images:
            return ""
        return pytesseract.image_to_string(images[0]) or ""
    except Exception as e:
        print(f"  OCR failed on page {page_number}: {e}")
        return ""


# ==========================
# PDF PAGE EXTRACTOR
# ==========================

def extract_pdf_pages(pdf_path, use_ocr_fallback=True):
    """
    Extract text from every page separately.

    Tries the native text layer first (fast). If a page comes back
    with almost nothing, falls back to local OCR automatically —
    this is what makes scanned annual reports work.

    Returns:
        {
            1: "...",
            2: "...",
            ...
        }
    """

    pages = {}
    ocr_count = 0

    with pdfplumber.open(pdf_path) as pdf:

        print(f"\nReading PDF... ({len(pdf.pages)} pages)\n")

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            if len(text.strip()) < MIN_CHARS_FOR_TEXT_PAGE and use_ocr_fallback:
                if ocr_count < OCR_MAX_PAGES:
                    print(f"  Page {page_number}: little/no text found, running OCR...")
                    ocr_text = _ocr_page(pdf_path, page_number)
                    if ocr_text.strip():
                        text = ocr_text
                        ocr_count += 1

            pages[page_number] = text

    if ocr_count:
        print(f"\nOCR was used on {ocr_count} page(s).")

    return pages


# ==========================
# FIND BEST FINANCIAL PAGES
# ==========================

def find_best_pages(pages, top_n=5):
    """
    Score every page based on financial keywords.
    """

    page_scores = []

    for page_number, text in pages.items():

        score = 0

        text_lower = text.lower()

        for term in SEARCH_TERMS:

            if term.lower() in text_lower:
                score += 1

        page_scores.append((page_number, score))

    page_scores.sort(key=lambda x: x[1], reverse=True)

    return page_scores[:top_n]


def extract_tables(pdf_path, page_numbers):

    rows = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_number in page_numbers:

            page = pdf.pages[page_number - 1]

            found_tables = page.find_tables()

            print(f"Page {page_number}: {len(found_tables)} table(s) found")

            for table in found_tables:

                data = table.extract()

                if not data:
                    continue

                for row in data:

                    cleaned = []

                    for cell in row:

                        if cell is None:
                            cleaned.append("")
                        else:
                            cleaned.append(str(cell).strip())

                    rows.append(cleaned)

    return rows


# ==========================
# TEXT METRIC EXTRACTOR
# ==========================

def _flexible_alias_pattern(alias):
    """
    Build a regex for `alias` that tolerates spacing differences —
    OCR commonly drops or merges spaces (e.g. "Total Assets" becomes
    "TotalAssets"). Matches word-by-word with optional whitespace
    between them instead of requiring an exact literal match.
    """
    words = alias.split()
    return r"\s*".join(re.escape(w) for w in words)


def extract_metrics_from_tables(rows):

    metrics = {}

    targets = {
        "total_assets": ["total assets"],
        "total_deposits": ["deposits"],
        "total_loans": ["total group lending", "total loans", "loans"],
        "total_liabilities": ["total liabilities"],
        "shareholders_equity": ["shareholders' equity", "shareholders equity", "total equity"],
        "net_income": ["net profit after tax", "net income", "profit after tax"],
        "operating_income": ["total operating income", "operating income"],
        "operating_expenses": ["operating expenses"]
    }

    for row in rows:

        row_text = " | ".join(row).lower()

        for metric, keywords in targets.items():

            if metric in metrics:
                continue

            if not any(keyword in row_text for keyword in keywords):
                continue

            for cell in row[1:]:

                numbers = re.findall(r"\b\d[\d,]*\b", row_text)
                numbers = [n for n in numbers if len(n.replace(",", "")) >= 5]      

                if numbers:

                    metrics[metric] = max(numbers, key=lambda x: len(x.replace(",", "")))
                    break

    return metrics



# ==========================
# TEST
# ==========================

if __name__ == "__main__":

    pdf_path = "Data/downloaded_reports/Commonwealth Bank Australia/2025.pdf"

    # Read PDF
    pages = extract_pdf_pages(pdf_path)

    # Find candidate pages
    best_pages = find_best_pages(pages)

    tables = extract_tables(
    pdf_path,
    [page for page, score in best_pages]
)

    print(f"\nExtracted {len(tables)} rows\n")

    for row in tables[:50]:
        print(row)
    for page_number, score in best_pages:
        print(f"Page {page_number} | Score = {score}")

    metrics = extract_metrics_from_tables(tables)
print("\nEXTRACTED METRICS\n")

for key, value in metrics.items():
            print(f"{key}: {value}")

   
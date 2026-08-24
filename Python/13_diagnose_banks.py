"""
Diagnostic tool: run this on a handful of banks that YOU know have
findable annual reports (ones you found manually) to see exactly
where the automated search is failing.

Usage:
    python 13_diagnose_bank.py "https://www.bankacredins.com"
"""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

CANDIDATE_PATHS = [
    "", "investor-relations", "investors", "investor",
    "about-us/investor-relations", "about/investor-relations",
    "annual-report", "annual-reports", "financial-statements",
    "financial-reports", "reports", "media/reports",
    "about/financial-reports", "en/investor-relations",
    "en/annual-report", "ir", "publications",
]


def diagnose(website):
    website = website.rstrip("/")
    print(f"\n{'='*70}\nDiagnosing: {website}\n{'='*70}")

    any_page_loaded = False
    total_links_seen = 0
    total_pdf_links = 0

    for path in CANDIDATE_PATHS:
        url = f"{website}/{path}".rstrip("/")
        try:
            resp = requests.get(url, timeout=15, headers=HEADERS)
        except requests.RequestException as e:
            print(f"  [{path or 'homepage'}] REQUEST FAILED: {e}")
            continue

        if resp.status_code != 200:
            print(f"  [{path or 'homepage'}] HTTP {resp.status_code}")
            continue

        any_page_loaded = True
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=True)
        total_links_seen += len(links)

        pdf_links = [urljoin(url, a["href"]) for a in links if a["href"].lower().endswith(".pdf")]
        total_pdf_links += len(pdf_links)

        report_word_links = [
            (a.get_text(' ', strip=True), urljoin(url, a["href"]))
            for a in links
            if any(w in a.get_text(' ', strip=True).lower() or w in a["href"].lower()
                   for w in ["annual", "report", "financial"])
        ]

        print(f"  [{path or 'homepage'}] OK — {len(links)} links, {len(pdf_links)} end in .pdf, "
              f"{len(report_word_links)} mention annual/report/financial")

        if pdf_links:
            print(f"     ALL .pdf links on this page (not just filtered matches):")
            for link in pdf_links[:15]:
                print(f"       {link}")

    print(f"\n--- SUMMARY ---")
    print(f"Any page loaded successfully: {any_page_loaded}")
    print(f"Total links seen across all pages checked: {total_links_seen}")
    print(f"Total .pdf-ending links found: {total_pdf_links}")

    if not any_page_loaded:
        print("DIAGNOSIS: Site is blocking requests entirely (bot detection, "
              "requires JS, wrong URL, or firewall). Try opening it in a normal "
              "browser vs what Python sees.")
    elif total_links_seen < 5:
        print("DIAGNOSIS: Very few links found at all — likely a JavaScript-"
              "rendered site. The HTML Python received is probably just an "
              "empty shell/loading page.")
    elif total_pdf_links == 0:
        print("DIAGNOSIS: Links exist, but none end in .pdf directly — the "
              "report is probably behind an extra click (a 'Reports' page "
              "that itself links to the PDF), or it's not a PDF at all "
              "(e.g. an HTML annual report, or embedded viewer).")
    else:
        print("DIAGNOSIS: PDF links exist — check if the phrase-matching "
              "filter is too strict for this bank's wording.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python 13_diagnose_bank.py \"https://www.bankwebsite.com\"")
    diagnose(sys.argv[1])
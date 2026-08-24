from playwright.sync_api import sync_playwright
import requests
import os
import re

BANK_NAME = "Commonwealth Bank Australia"
BANK_URL = "https://www.commbank.com.au/"

KEYWORDS = [
    "investor",
    "investors",
    "annual report",
    "annual reports",
    "historical annual reports",
    "results"
]

BLACKLIST = [
    "support",
    "financial-hardship",
    "insurance",
    "brighter",
    "cost-of-living"
]

DOWNLOAD_FOLDER = os.path.join(
    "Data",
    "downloaded_reports",
    BANK_NAME
)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

ANNUAL_REPORTS = []


def get_links(page):
    return page.locator("a").evaluate_all("""
        elements => elements.map(e => ({
            text: e.innerText,
            href: e.href
        }))
    """)


def filter_links(links):

    matches = []

    for link in links:

        text = (link.get("text") or "").lower()
        href = (link.get("href") or "").lower()

        if not href:
            continue

        if any(word in href for word in BLACKLIST):
            continue

        if any(word in text or word in href for word in KEYWORDS):
            matches.append(link)

    return matches


def save_report(text, href):

    text_lower = text.lower()

    if "sustainability" in text_lower:
        return

    if "pages" in text_lower:
        return

    year = re.search(r"(20\d{2})", text)

    if not year:
        year = re.search(r"(20\d{2})", href)

    if not year:
        fy = re.search(r"fy(\d{2})", href.lower())
        if fy:
            year = "20" + fy.group(1)
        else:
            return
    else:
        year = year.group(1)

    if int(year) < 2020 or int(year) > 2025:
        return

    for report in ANNUAL_REPORTS:
        if report["year"] == year:
            return

    ANNUAL_REPORTS.append({
        "year": year,
        "title": text,
        "url": href
    })


def scan_page(page):

    links = get_links(page)

    for link in links:

        text = (link.get("text") or "").strip()
        href = (link.get("href") or "").strip()

        if not href.lower().endswith(".pdf"):
            continue

        if "annual report" not in text.lower():
            continue

        save_report(text, href)


def download_reports():

    print("\nDownloading PDFs...\n")

    for report in ANNUAL_REPORTS:

        filename = f"{report['year']}.pdf"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        if os.path.exists(filepath):
            print(f"Skipped {filename}")
            continue

        try:

            response = requests.get(report["url"], timeout=60)

            response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"Downloaded {filename}")

        except Exception as e:

            print(f"Failed {filename}")
            print(e)


def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto(BANK_URL, wait_until="networkidle")

        visited = set()

        homepage = filter_links(get_links(page))

        for first in homepage:

            url = first["href"]

            if url in visited:
                continue

            visited.add(url)

            try:

                page.goto(url, wait_until="networkidle")

                scan_page(page)

                second = filter_links(get_links(page))

                for nxt in second:

                    url2 = nxt["href"]

                    if url2 in visited:
                        continue

                    visited.add(url2)

                    try:

                        page.goto(url2, wait_until="networkidle")

                        scan_page(page)

                    except:
                        pass

            except:
                pass

        browser.close()

    ANNUAL_REPORTS.sort(key=lambda x: x["year"], reverse=True)

    print("\nFINAL REPORTS\n")

    for report in ANNUAL_REPORTS:
        print(report)

    download_reports()


if __name__ == "__main__":
    main()
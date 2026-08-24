import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse



# Load banks dataset
banks_df = pd.read_csv("Data/Raw/Banks/banks.csv")

# Remove spaces from column names
banks_df.columns = banks_df.columns.str.strip()

# -----------------------------
# Get first bank
# -----------------------------
TEST_BANK = "Bangladesh Bank"

first_bank = banks_df[
    banks_df["bank_name"] == TEST_BANK
].iloc[0]

bank_name = first_bank["bank_name"]
website = first_bank["official_website"]

# Extract the domain from the website
domain = urlparse(website).netloc

# Remove "www."
domain = domain.replace("www.", "")

print(f"Domain: {domain}")

search_query = f"site:{domain} annual report"

print(f"Search Query: {search_query}")

print(f"Bank: {bank_name}")
print(f"Website: {website}")

# -----------------------------
# Connect to website
# -----------------------------
print("\nConnecting to website...")

try:
    response = requests.get(
        website,
        timeout=15,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    print(f"Status Code: {response.status_code}")

    # Parse webpage
    soup = BeautifulSoup(response.text, "html.parser")

    print("\nLinks found on homepage:\n")

    links_found = set()

    for link in soup.find_all("a", href=True):

        href = link["href"].strip()

        if href:
            links_found.add(href)

    for link in sorted(links_found):
        print(link)

except Exception as e:
    print(f"Connection failed: {e}")
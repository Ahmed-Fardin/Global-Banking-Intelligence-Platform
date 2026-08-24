import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("REST_COUNTRIES_API_KEY")

# ==========================================
# REST COUNTRIES API
# ==========================================

url = "https://api.restcountries.com/countries/v5"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

all_countries = []

offset = 0
limit = 100

while True:

    url = f"https://api.restcountries.com/countries/v5?limit={limit}&offset={offset}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    raw_data = response.json()

    print(raw_data["data"]["meta"])

    all_countries.extend(raw_data["data"]["objects"])

    print(f"Total countries collected: {len(all_countries)}")

    print(
        f"Downloaded {len(raw_data['data']['objects'])} countries "
        f"(Offset: {offset})"
    )

    if not raw_data["data"]["meta"]["more"]:
        break

    offset += limit

print(raw_data["data"]["meta"])

with open("Data/Raw/countries.json", "w", encoding="utf-8") as file:
    json.dump(all_countries, file, indent=4, ensure_ascii=False)

print("Raw JSON saved successfully.")

# ==========================================
# EXTRACT REQUIRED FIELDS
# ==========================================

country = raw_data["data"]["objects"][0]

# ==========================================
# EXTRACT ALL COUNTRIES
# ==========================================

countries = all_countries
country_records = []

for country in countries:

    if country["currencies"]:
        currency_name = country["currencies"][0]["name"]
        currency_code = country["currencies"][0]["code"]
        currency_symbol = country["currencies"][0]["symbol"]
    else:
        currency_name = None
        currency_code = None
        currency_symbol = None

    country_record = {
        "country_name": country["names"]["common"],
        "iso2_code": country["codes"]["alpha_2"],
        "iso3_code": country["codes"]["alpha_3"],
        "continent": country["continents"][0],
        "region": country["region"],
        "latitude": country["coordinates"]["lat"],
        "longitude": country["coordinates"]["lng"],

        "currency_name": currency_name,
        "currency_code": currency_code,
        "currency_symbol": currency_symbol,

        "country_flag_url": country["flag"]["url_png"],
        "official_website": country["links"]["official"]
    }

    country_records.append(country_record)

print(f"Countries Processed: {len(country_records)}")
# ==========================================
# CREATE DATAFRAME
# ==========================================

import pandas as pd

countries_df = pd.DataFrame(country_records)

print(countries_df.head())


# ==========================================
# SAVE PROCESSED DATA
# ==========================================

output_file = Path("Data/processed/countries.csv")

countries_df.to_csv(output_file, index=False)

print(f"\nProcessed dataset saved to:\n{output_file}")


print("Status Code:", response.status_code)
 

print("\n========== DOWNLOAD SUMMARY ==========")
print(f"Countries Downloaded : {len(all_countries)}")
print(f"Countries Processed  : {len(country_records)}")
print(f"Output CSV           : Data/processed/countries.csv")
print(f"Output JSON          : Data/Raw/countries.json")
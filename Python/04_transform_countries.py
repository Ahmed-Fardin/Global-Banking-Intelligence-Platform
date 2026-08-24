import pandas as pd
from config import get_connection

# ==========================================
# CONNECT TO POSTGRESQL
# ==========================================

conn = get_connection()

regions_df = pd.read_sql(
    """
    SELECT
        region_id,
        region_name
    FROM regions;
    """,
    conn
)

currencies_df = pd.read_sql(
    """
    SELECT
        currency_id,
        currency_code
    FROM currencies;
    """,
    conn
)

print(regions_df)
print(currencies_df.head())


# ==========================================
# CREATE LOOKUP DICTIONARIES
# ==========================================

region_lookup = dict(
    zip(
        regions_df["region_name"],
        regions_df["region_id"]
    )
)

currency_lookup = dict(
    zip(
        currencies_df["currency_code"],
        currencies_df["currency_id"]
    )
)

# ==========================================
# LOAD COUNTRIES DATA
# ==========================================

countries_df = pd.read_csv("Data/processed/countries.csv")

print(countries_df.head())



countries_df["region_id"] = (
    countries_df["region"]
    .map(region_lookup)
)

# ==========================================
# MAP CURRENCY IDs
# ==========================================

countries_df["currency_id"] = (
    countries_df["currency_code"]
    .map(currency_lookup)
)

print(
    countries_df[
        [
            "country_name",
            "currency_code",
            "currency_id"
        ]
    ].head()
)

print(
    countries_df[
        [
            "country_name",
            "region",
            "region_id"
        ]
    ].head()
)


# ==========================================
# REMOVE OLD TEXT COLUMNS
# ==========================================

countries_df = countries_df.drop(
    columns=[
        "region",
        "currency_code"
    ]
)


# ==========================================
# REORDER COLUMNS
# ==========================================

countries_df = countries_df[
    [
        "country_name",
        "iso2_code",
        "iso3_code",
        "continent",
        "region_id",
        "currency_id",
        "latitude",
        "longitude",
        "country_flag_url",
        "official_website"
    ]
]

print(countries_df.head())

# ==========================================
# SAVE FINAL COUNTRIES DATASET
# ==========================================

countries_df.to_csv(
    "Data/processed/countries_final.csv",
    index=False
)

print("\nCountries transformation completed.")
print("Saved to: Data/processed/countries_final.csv")

# ==========================================
# CHECK FOR MISSING LOOKUPS
# ==========================================

print("\nMissing Regions:")
print(countries_df["region_id"].isna().sum())

print("\nMissing Currencies:")
print(countries_df["currency_id"].isna().sum())


# # ==========================================
# # SHOW MISSING CURRENCIES
# # ==========================================

# missing_currency = countries_df[
#     countries_df["currency_id"].isna()
# ]

# print("\nCountries With Missing Currency:")

# print(
#     missing_currency[
#         [
#             "country_name",
#             "currency_name",
#             "currency_id"
#         ]
#     ]
# )



print(region_lookup)
print(currency_lookup)


print("Connected successfully.")
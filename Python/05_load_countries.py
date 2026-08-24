import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 05 — LOAD COUNTRIES INTO POSTGRESQL
# ============================================================


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# FILES
# ============================================================

WORLD_BANK_FILE = (
    "Data/Raw/Banks/"
    "world_bank_data_2020_2025_final.csv"
)

BANKS_FILE = (
    "Data/Raw/Banks/"
    "banks.csv"
)


# ============================================================
# DATABASE CONFIG
# ============================================================

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


# ============================================================
# CHECK ENVIRONMENT
# ============================================================

required_variables = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DATABASE",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]

missing_variables = [
    variable
    for variable in required_variables
    if not os.getenv(variable)
]

if missing_variables:
    raise ValueError(
        "Missing environment variables:\n"
        + "\n".join(missing_variables)
    )


# ============================================================
# LOAD DATASETS
# ============================================================

world = pd.read_csv(
    WORLD_BANK_FILE,
    low_memory=False
)

banks = pd.read_csv(
    BANKS_FILE,
    low_memory=False
)


print("=" * 70)
print("COUNTRY SOURCE DATA LOADED")
print("=" * 70)

print("World Bank rows:", len(world))
print("Banks rows:", len(banks))


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

world.columns = world.columns.str.strip()
banks.columns = banks.columns.str.strip()


# ============================================================
# STANDARDIZE ISO3
# ============================================================

for df in [world, banks]:

    df["iso3_code"] = (
        df["iso3_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )


# ============================================================
# EXTRACT WORLD BANK COUNTRIES
# ============================================================

world_countries = (
    world[
        [
            "iso3_code",
            "country_name"
        ]
    ]
    .dropna(
        subset=[
            "iso3_code",
            "country_name"
        ]
    )
    .copy()
)


# ============================================================
# REMOVE INVALID WORLD BANK ISO3
# ============================================================

world_invalid = world_countries[
    world_countries["iso3_code"].str.len() != 3
].copy()


world_countries = world_countries[
    world_countries["iso3_code"].str.len() == 3
].copy()


# ============================================================
# EXTRACT BANK COUNTRIES
# ============================================================

bank_countries = (
    banks[
        [
            "iso3_code",
            "country_name"
        ]
    ]
    .dropna(
        subset=[
            "iso3_code",
            "country_name"
        ]
    )
    .copy()
)


# ============================================================
# REMOVE INVALID BANK ISO3
# ============================================================

bank_invalid = bank_countries[
    bank_countries["iso3_code"].str.len() != 3
].copy()


bank_countries = bank_countries[
    bank_countries["iso3_code"].str.len() == 3
].copy()


# ============================================================
# COMBINE COUNTRY SOURCES
#
# This is important:
#
# World Bank contains countries without banks.
# Banks contains countries without World Bank records.
#
# Therefore countries = UNION of both datasets.
# ============================================================

countries = pd.concat(
    [
        world_countries,
        bank_countries
    ],
    ignore_index=True
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

countries = (
    countries
    .drop_duplicates(
        subset=["iso3_code"],
        keep="first"
    )
    .sort_values("iso3_code")
    .reset_index(drop=True)
)


# ============================================================
# CHECK COUNTRY NAME CONFLICTS
# ============================================================

conflicts = (
    pd.concat(
        [
            world_countries,
            bank_countries
        ],
        ignore_index=True
    )
    .drop_duplicates()
    .groupby("iso3_code")["country_name"]
    .nunique()
)

conflicts = conflicts[
    conflicts > 1
]


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("COUNTRY EXTRACTION")
print("=" * 70)

print(
    "World Bank countries:",
    world_countries["iso3_code"].nunique()
)

print(
    "Bank countries:",
    bank_countries["iso3_code"].nunique()
)

print(
    "Combined countries:",
    len(countries)
)

print(
    "Invalid World Bank ISO3 records:",
    len(world_invalid)
)

print(
    "Invalid Bank ISO3 records:",
    len(bank_invalid)
)

print(
    "Country name conflicts:",
    len(conflicts)
)


# ============================================================
# SHOW IMPORTANT COVERAGE DIFFERENCES
# ============================================================

world_codes = set(
    world_countries["iso3_code"]
)

bank_codes = set(
    bank_countries["iso3_code"]
)


banks_missing_world = sorted(
    bank_codes - world_codes
)

world_missing_banks = sorted(
    world_codes - bank_codes
)


print("\n" + "=" * 70)
print("SOURCE COVERAGE DIFFERENCES")
print("=" * 70)

print(
    "Bank countries missing from World Bank:",
    len(banks_missing_world)
)

if banks_missing_world:
    print(banks_missing_world)


print(
    "\nWorld Bank countries without banks:",
    len(world_missing_banks)
)


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print("\n" + "=" * 70)
print("POSTGRESQL CONNECTION")
print("=" * 70)

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(
    **DB_CONFIG
)

cursor = conn.cursor()

print(
    "Connected to database:",
    DB_CONFIG["database"]
)


# ============================================================
# INSERT / UPDATE COUNTRIES
# ============================================================

insert_sql = """
INSERT INTO countries (
    iso3_code,
    country_name
)
VALUES (
    %s,
    %s
)
ON CONFLICT (iso3_code)
DO UPDATE SET
    country_name = EXCLUDED.country_name;
"""


processed = 0


for _, row in countries.iterrows():

    cursor.execute(
        insert_sql,
        (
            row["iso3_code"],
            row["country_name"]
        )
    )

    processed += 1


# ============================================================
# COMMIT
# ============================================================

conn.commit()


# ============================================================
# VERIFY DATABASE
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM countries;
    """
)

database_count = cursor.fetchone()[0]


# ============================================================
# VERIFY INVALID DATABASE ISO3
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM countries
    WHERE LENGTH(TRIM(iso3_code)) != 3;
    """
)

invalid_database_codes = cursor.fetchone()[0]


# ============================================================
# VERIFY TWN
# ============================================================

cursor.execute(
    """
    SELECT
        iso3_code,
        country_name
    FROM countries
    WHERE iso3_code = 'TWN';
    """
)

taiwan = cursor.fetchone()


# ============================================================
# CLOSE
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("COUNTRIES LOAD COMPLETE")
print("=" * 70)

print(
    "Countries processed:",
    processed
)

print(
    "Countries currently in database:",
    database_count
)

print(
    "Invalid ISO3 codes in database:",
    invalid_database_codes
)

print(
    "TWN in countries table:",
    taiwan
)

print(
    "Database:",
    DB_CONFIG["database"]
)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
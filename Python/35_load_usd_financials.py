import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from decimal import Decimal, InvalidOperation


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 35 — LOAD USD BANK FINANCIALS
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = Path(
    "Data/Raw/Banks/Mains/bank_financials_synthetic_usd.csv"
)

DB_NAME = "gbip"
DB_USER = "postgres"
DB_PASSWORD = "XXX"
DB_HOST = "localhost"
DB_PORT = 5432

TABLE_NAME = "bank_financials_usd"


EXPECTED_COLUMNS = [
    "iso3_code",
    "bank_name",
    "fiscal_year",
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income",
    "roe_percent",
    "roa_percent",
    "capital_adequacy_percent",
    "cost_income_ratio",
    "loan_to_deposit_ratio",
    "npl_ratio",
    "employees",
    "branches",
    "reporting_currency",
    "source",
]

MONETARY_COLUMNS = [
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income",
]

RATIO_COLUMNS = [
    "roe_percent",
    "roa_percent",
    "capital_adequacy_percent",
    "cost_income_ratio",
    "loan_to_deposit_ratio",
    "npl_ratio",
]

INTEGER_COLUMNS = [
    "fiscal_year",
    "employees",
    "branches",
]


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_decimal(value):
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text == "":
        return None

    if text.lower() in {
        "nan",
        "none",
        "null",
        "na",
        "n/a",
        "pending public data",
    }:
        return None

    text = text.replace(",", "")

    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValueError(
            f"Invalid numeric value: {value!r}"
        )


def clean_integer(value):
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text == "":
        return None

    if text.lower() in {
        "nan",
        "none",
        "null",
        "na",
        "n/a",
        "pending public data",
    }:
        return None

    numeric = float(text)

    if not numeric.is_integer():
        raise ValueError(
            f"Non-integer value in integer field: {value!r}"
        )

    return int(numeric)


def fail(message):
    raise ValueError(message)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("GLOBAL BANKING INTELLIGENCE")
print("35 — LOAD USD BANK FINANCIALS")
print("=" * 70)

print()
print("Input file:")
print(CSV_FILE)


# ============================================================
# FILE CHECK
# ============================================================

if not CSV_FILE.exists():
    fail(
        f"USD CSV file not found:\n{CSV_FILE}"
    )


# ============================================================
# LOAD CSV
# ============================================================

df = pd.read_csv(
    CSV_FILE,
    dtype=str,
    keep_default_na=True,
)

print()
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# COLUMN CHECK
# ============================================================

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in df.columns
]

extra_columns = [
    column
    for column in df.columns
    if column not in EXPECTED_COLUMNS
]

print()
print("Expected columns:", len(EXPECTED_COLUMNS))
print("Actual columns:", len(df.columns))
print("Missing columns:", len(missing_columns))
print("Extra columns:", len(extra_columns))

if missing_columns:
    fail(
        f"Missing columns: {missing_columns}"
    )

if extra_columns:
    fail(
        f"Unexpected columns: {extra_columns}"
    )

df = df[EXPECTED_COLUMNS].copy()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

for column in [
    "iso3_code",
    "bank_name",
    "reporting_currency",
    "source",
]:
    df[column] = df[column].apply(clean_text)


df["iso3_code"] = (
    df["iso3_code"]
    .str.upper()
)


# ============================================================
# KEY CHECKS
# ============================================================

blank_iso3 = (
    df["iso3_code"].isna()
    | (df["iso3_code"] == "")
).sum()

blank_bank_names = (
    df["bank_name"].isna()
    | (df["bank_name"] == "")
).sum()

invalid_iso3 = (
    df["iso3_code"].notna()
    & (df["iso3_code"].str.len() != 3)
).sum()

print()
print("Blank ISO3:", blank_iso3)
print("Invalid ISO3 length:", invalid_iso3)
print("Blank bank names:", blank_bank_names)

if blank_iso3 > 0:
    fail("Blank ISO3 values detected.")

if invalid_iso3 > 0:
    fail("Invalid ISO3 codes detected.")

if blank_bank_names > 0:
    fail("Blank bank names detected.")


# ============================================================
# FISCAL YEAR
# ============================================================

df["fiscal_year"] = df["fiscal_year"].apply(
    clean_integer
)

invalid_years = (
    df["fiscal_year"].isna()
    | ~df["fiscal_year"].between(2020, 2025)
).sum()

print()
print("Invalid fiscal years:", invalid_years)

if invalid_years > 0:
    fail("Invalid fiscal years detected.")


# ============================================================
# MONETARY FIELDS
# ============================================================

print()
print("Normalizing monetary fields...")

for column in MONETARY_COLUMNS:
    df[column] = df[column].apply(clean_decimal)

    print(f"{column}: normalized")


# ============================================================
# RATIO FIELDS
# ============================================================

for column in RATIO_COLUMNS:
    df[column] = df[column].apply(clean_decimal)


# ============================================================
# INTEGER FIELDS
# ============================================================

for column in [
    "employees",
    "branches",
]:
    df[column] = df[column].apply(clean_integer)


# ============================================================
# USD CHECK
# ============================================================

non_usd_currency = (
    df["reporting_currency"]
    .notna()
    &
    (
        df["reporting_currency"].str.upper()
        != "USD"
    )
).sum()

print()
print("Non-USD reporting currency records:", non_usd_currency)

if non_usd_currency > 0:
    fail(
        "USD dataset contains non-USD reporting currencies."
    )


# ============================================================
# DUPLICATE CHECK
# ============================================================

duplicates = df.duplicated(
    subset=[
        "iso3_code",
        "bank_name",
        "fiscal_year",
    ],
    keep=False,
)

duplicate_count = duplicates.sum()

print()
print("Duplicate bank/year rows:", duplicate_count)

if duplicate_count > 0:
    fail(
        "Duplicate bank/year records detected."
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

print()
print("=" * 70)
print("POSTGRESQL CONNECTION")
print("=" * 70)

print("Connecting to PostgreSQL...")

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)

connection.autocommit = False

print("Connected to database:", DB_NAME)


# ============================================================
# TABLE CHECK
# ============================================================

cursor = connection.cursor()

cursor.execute(
    """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = %s
    );
    """,
    (TABLE_NAME,),
)

table_exists = cursor.fetchone()[0]

if not table_exists:
    connection.rollback()
    connection.close()

    fail(
        f"PostgreSQL table '{TABLE_NAME}' does not exist."
    )


# ============================================================
# BANK REFERENCE CHECK
# ============================================================

cursor.execute(
    """
    SELECT iso3_code, bank_name
    FROM banks;
    """
)

bank_rows = cursor.fetchall()

bank_reference = {
    (
        str(row[0]).strip().upper(),
        str(row[1]).strip(),
    )
    for row in bank_rows
}

missing_banks = []

for row in df[
    ["iso3_code", "bank_name"]
].itertuples(index=False):

    key = (
        row.iso3_code,
        row.bank_name,
    )

    if key not in bank_reference:
        missing_banks.append(key)


print()
print("Missing bank references:", len(missing_banks))

if missing_banks:
    print("First missing references:")
    for item in missing_banks[:20]:
        print(item)

    connection.rollback()
    connection.close()

    fail(
        "USD dataset contains bank references "
        "that do not exist in the banks table."
    )


# ============================================================
# COUNTRY REFERENCE CHECK
# ============================================================

cursor.execute(
    """
    SELECT iso3_code
    FROM countries;
    """
)

country_codes = {
    str(row[0]).strip().upper()
    for row in cursor.fetchall()
}

missing_countries = sorted(
    set(df["iso3_code"].dropna())
    - country_codes
)

print(
    "Missing country references:",
    len(missing_countries)
)

if missing_countries:
    print(
        "Missing ISO3 codes:",
        missing_countries
    )

    connection.rollback()
    connection.close()

    fail(
        "USD dataset contains missing country references."
    )


# ============================================================
# PREPARE DATABASE RECORDS
# ============================================================

records = []

for row in df.itertuples(
    index=False,
    name=None,
):

    cleaned_row = []

    for value in row:

        if pd.isna(value):
            cleaned_row.append(None)
        else:
            cleaned_row.append(value)

    records.append(tuple(cleaned_row))


# ============================================================
# FINAL NAN CHECK
# ============================================================

nan_remaining = 0

for row in records:
    for value in row:
        if isinstance(value, float) and np.isnan(value):
            nan_remaining += 1

print()
print("NaN values remaining:", nan_remaining)

if nan_remaining > 0:
    connection.rollback()
    connection.close()

    fail(
        "NaN values remain before database load."
    )


# ============================================================
# CLEAR EXISTING USD DATA
# ============================================================

cursor.execute(
    f"""
    SELECT COUNT(*)
    FROM {TABLE_NAME};
    """
)

existing_records = cursor.fetchone()[0]

print()
print("Existing USD records:", existing_records)

cursor.execute(
    f"""
    TRUNCATE TABLE {TABLE_NAME}
    RESTART IDENTITY;
    """
)


# ============================================================
# INSERT
# ============================================================

insert_sql = f"""
INSERT INTO {TABLE_NAME}
(
    iso3_code,
    bank_name,
    fiscal_year,
    total_assets,
    total_deposits,
    total_loans,
    shareholders_equity,
    operating_income,
    net_income,
    roe_percent,
    roa_percent,
    capital_adequacy_percent,
    cost_income_ratio,
    loan_to_deposit_ratio,
    npl_ratio,
    employees,
    branches,
    reporting_currency,
    source
)
VALUES %s;
"""


print()
print("=" * 70)
print("LOADING USD FINANCIAL RECORDS")
print("=" * 70)

try:

    execute_values(
        cursor,
        insert_sql,
        records,
        page_size=500,
    )

    connection.commit()

except Exception:

    connection.rollback()

    print()
    print("DATABASE LOAD FAILED")
    print("Transaction rolled back.")

    raise


# ============================================================
# POST-LOAD VALIDATION
# ============================================================

cursor.execute(
    f"""
    SELECT COUNT(*)
    FROM {TABLE_NAME};
    """
)

database_count = cursor.fetchone()[0]

print()
print("CSV records:", len(df))
print("Database records:", database_count)

if database_count != len(df):

    connection.rollback()
    connection.close()

    fail(
        "CSV/database record count mismatch."
    )


# ============================================================
# DUPLICATE DATABASE CHECK
# ============================================================

cursor.execute(
    f"""
    SELECT
        iso3_code,
        bank_name,
        fiscal_year,
        COUNT(*)
    FROM {TABLE_NAME}
    GROUP BY
        iso3_code,
        bank_name,
        fiscal_year
    HAVING COUNT(*) > 1;
    """
)

database_duplicates = cursor.fetchall()

print(
    "Duplicate database groups:",
    len(database_duplicates)
)

if database_duplicates:

    connection.rollback()
    connection.close()

    fail(
        "Duplicate bank/year groups detected."
    )


# ============================================================
# USD CURRENCY CHECK
# ============================================================

cursor.execute(
    f"""
    SELECT COUNT(*)
    FROM {TABLE_NAME}
    WHERE reporting_currency <> 'USD';
    """
)

non_usd_database = cursor.fetchone()[0]

print(
    "Non-USD database records:",
    non_usd_database
)

if non_usd_database > 0:

    connection.rollback()
    connection.close()

    fail(
        "Non-USD records found in USD table."
    )


# ============================================================
# COMMIT
# ============================================================

connection.commit()

cursor.close()
connection.close()


# ============================================================
# DONE
# ============================================================

print()
print("=" * 70)
print("USD FINANCIAL DATA LOAD COMPLETE")
print("=" * 70)

print()
print("CSV records:", len(df))
print("Database records:", database_count)
print("Database:", DB_NAME)
print("Table:", TABLE_NAME)

print()
print("STATUS: PASS")
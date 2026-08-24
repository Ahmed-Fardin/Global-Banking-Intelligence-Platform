import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 30 — LOAD SYNTHETIC BANK FINANCIALS
# ============================================================


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# MAIN DATA FILE
# ============================================================

FINANCIALS_FILE = (
    "Data/Raw/Banks/Mains/"
    "bank_financials_synthetic.csv"
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


# ============================================================
# LOAD DATA
# ============================================================

financials = pd.read_csv(
    FINANCIALS_FILE,
    low_memory=False
)

financials.columns = (
    financials.columns
    .str.strip()
)


print("=" * 70)
print("BANK FINANCIALS — SYNTHETIC DATA LOADED")
print("=" * 70)

print("Rows:", len(financials))

print("Columns:", len(financials.columns))

print(
    "Column names:"
)

print(
    financials.columns.tolist()
)


# ============================================================
# EXPECTED 20 COLUMNS
# ============================================================

expected_columns = [
    "financial_id",
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


# ============================================================
# COLUMN VALIDATION
# ============================================================

missing_columns = [
    column
    for column in expected_columns
    if column not in financials.columns
]


extra_columns = [
    column
    for column in financials.columns
    if column not in expected_columns
]


if missing_columns:

    raise ValueError(
        "Missing required financial columns:\n"
        + "\n".join(missing_columns)
    )


if extra_columns:

    print("\nWARNING — EXTRA COLUMNS FOUND:")
    print(extra_columns)


if len(financials.columns) != 20:

    raise ValueError(
        f"Expected 20 columns, "
        f"but found {len(financials.columns)}."
    )


# ============================================================
# STANDARDIZE ISO3
# ============================================================

financials["iso3_code"] = (
    financials["iso3_code"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# ISO3 VALIDATION
# ============================================================

invalid_iso3 = financials[
    financials["iso3_code"].isna()
    |
    (financials["iso3_code"].str.len() != 3)
].copy()


print("\n" + "=" * 70)
print("ISO3 CHECK")
print("=" * 70)

print(
    "Invalid ISO3 records:",
    len(invalid_iso3)
)


if len(invalid_iso3) > 0:

    print(
        invalid_iso3[
            [
                "financial_id",
                "iso3_code",
                "bank_name"
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "Invalid ISO3 codes found."
    )


# ============================================================
# FINANCIAL ID CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINANCIAL ID CHECK")
print("=" * 70)

print(
    "Missing financial IDs:",
    financials["financial_id"].isna().sum()
)

print(
    "Duplicate financial IDs:",
    financials["financial_id"].duplicated().sum()
)


if financials["financial_id"].isna().any():

    raise ValueError(
        "Missing financial_id values found."
    )


if financials["financial_id"].duplicated().any():

    raise ValueError(
        "Duplicate financial_id values found."
    )


# ============================================================
# BANK/YEAR DUPLICATE CHECK
# ============================================================

duplicate_groups = financials[
    financials.duplicated(
        subset=[
            "iso3_code",
            "bank_name",
            "fiscal_year"
        ],
        keep=False
    )
].copy()


print("\n" + "=" * 70)
print("BANK / YEAR DUPLICATE CHECK")
print("=" * 70)

print(
    "Duplicate bank/year records:",
    len(duplicate_groups)
)


if len(duplicate_groups) > 0:

    print(
        duplicate_groups[
            [
                "financial_id",
                "iso3_code",
                "bank_name",
                "fiscal_year"
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "Duplicate bank/year financial records found."
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
# CHECK BANK REFERENCES
# ============================================================

cursor.execute(
    """
    SELECT
        iso3_code,
        bank_name
    FROM banks;
    """
)


database_banks = {
    (
        row[0].strip().upper(),
        row[1].strip()
    )
    for row in cursor.fetchall()
}


financial_banks = {
    (
        row["iso3_code"],
        str(row["bank_name"]).strip()
    )
    for _, row in financials.iterrows()
}


missing_banks = sorted(
    financial_banks
    - database_banks
)


print("\n" + "=" * 70)
print("BANK REFERENCE CHECK")
print("=" * 70)

print(
    "Financial bank records without bank master:",
    len(missing_banks)
)


if missing_banks:

    print(
        missing_banks[:100]
    )

    cursor.close()
    conn.close()

    raise ValueError(
        "Financial records reference banks "
        "that do not exist in banks table."
    )


# ============================================================
# CHECK DATABASE TABLE COLUMNS
# ============================================================

cursor.execute(
    """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'bank_financials'
    ORDER BY ordinal_position;
    """
)


database_columns = [
    row[0]
    for row in cursor.fetchall()
]


print("\n" + "=" * 70)
print("BANK FINANCIALS TABLE")
print("=" * 70)

print(
    "Database columns:",
    database_columns
)


# ============================================================
# VERIFY REQUIRED DATABASE COLUMNS
# ============================================================

missing_database_columns = [
    column
    for column in expected_columns
    if column not in database_columns
]


if missing_database_columns:

    cursor.close()
    conn.close()

    raise ValueError(
        "The PostgreSQL bank_financials table "
        "is missing these required columns:\n"
        + "\n".join(missing_database_columns)
    )


# ============================================================
# INSERT QUERY
# ============================================================

insert_query = """
INSERT INTO bank_financials (
    financial_id,
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
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s
)
ON CONFLICT (financial_id)
DO UPDATE SET
    iso3_code = EXCLUDED.iso3_code,
    bank_name = EXCLUDED.bank_name,
    fiscal_year = EXCLUDED.fiscal_year,
    total_assets = EXCLUDED.total_assets,
    total_deposits = EXCLUDED.total_deposits,
    total_loans = EXCLUDED.total_loans,
    shareholders_equity = EXCLUDED.shareholders_equity,
    operating_income = EXCLUDED.operating_income,
    net_income = EXCLUDED.net_income,
    roe_percent = EXCLUDED.roe_percent,
    roa_percent = EXCLUDED.roa_percent,
    capital_adequacy_percent =
        EXCLUDED.capital_adequacy_percent,
    cost_income_ratio =
        EXCLUDED.cost_income_ratio,
    loan_to_deposit_ratio =
        EXCLUDED.loan_to_deposit_ratio,
    npl_ratio = EXCLUDED.npl_ratio,
    employees = EXCLUDED.employees,
    branches = EXCLUDED.branches,
    reporting_currency =
        EXCLUDED.reporting_currency,
    source = EXCLUDED.source;
"""


# ============================================================
# INSERT RECORDS
# ============================================================

loaded = 0


for _, row in financials.iterrows():

    cursor.execute(
        insert_query,
        (
            row["financial_id"],
            row["iso3_code"],
            row["bank_name"],
            row["fiscal_year"],
            row["total_assets"],
            row["total_deposits"],
            row["total_loans"],
            row["shareholders_equity"],
            row["operating_income"],
            row["net_income"],
            row["roe_percent"],
            row["roa_percent"],
            row["capital_adequacy_percent"],
            row["cost_income_ratio"],
            row["loan_to_deposit_ratio"],
            row["npl_ratio"],
            row["employees"],
            row["branches"],
            row["reporting_currency"],
            row["source"],
        )
    )

    loaded += 1


# ============================================================
# COMMIT
# ============================================================

conn.commit()


# ============================================================
# DATABASE VERIFICATION
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials;
    """
)

database_count = cursor.fetchone()[0]


# ============================================================
# VERIFY DUPLICATE BANK/YEAR GROUPS
# ============================================================

cursor.execute(
    """
    SELECT
        iso3_code,
        bank_name,
        fiscal_year,
        COUNT(*)
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name,
        fiscal_year
    HAVING COUNT(*) > 1;
    """
)

duplicate_database_groups = cursor.fetchall()


# ============================================================
# VERIFY FINANCIAL IDs
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials
    WHERE financial_id IS NULL;
    """
)

null_financial_ids = cursor.fetchone()[0]


# ============================================================
# CLOSE DATABASE
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("BANK FINANCIALS LOAD COMPLETE")
print("=" * 70)

print(
    "Source rows:",
    len(financials)
)

print(
    "Financial records processed:",
    loaded
)

print(
    "Financial records in database:",
    database_count
)

print(
    "Duplicate bank/year groups in database:",
    len(duplicate_database_groups)
)

print(
    "NULL financial IDs:",
    null_financial_ids
)

print(
    "Database:",
    DB_CONFIG["database"]
)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
import os
import pandas as pd
import psycopg2


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 33 — FINAL FINANCIAL VALIDATION
# ============================================================

DB_NAME = "gbip"
DB_USER = "postgres"
DB_PASSWORD = "1204"
DB_HOST = "localhost"
DB_PORT = 5432

CSV_PATH = (
    "Data/Raw/Banks/Mains/"
    "bank_financials_synthetic.csv"
)

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

NUMERIC_COLUMNS = [
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
]

INTEGER_COLUMNS = [
    "fiscal_year",
    "employees",
    "branches",
]

COUNT_COLUMNS = [
    "employees",
    "branches",
]

POSTGRES_INTEGER_MIN = -2147483648
POSTGRES_INTEGER_MAX = 2147483647

MISSING_DATA_MARKERS = {
    "",
    "Pending Public Data",
    "pending public data",
    "N/A",
    "n/a",
    "NA",
    "na",
    "NULL",
    "null",
}


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("GLOBAL BANKING INTELLIGENCE")
print("33 — FINAL FINANCIAL VALIDATION")
print("=" * 70)


# ============================================================
# LOAD CSV
# ============================================================

print()
print("Input file:")
print(CSV_PATH)

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(
        f"CSV file not found: {CSV_PATH}"
    )

financials = pd.read_csv(
    CSV_PATH,
    dtype=str,
    keep_default_na=False
)

print()
print("=" * 70)
print("SOURCE FILE")
print("=" * 70)

print("Rows:", len(financials))
print("Columns:", len(financials.columns))


# ============================================================
# COLUMN CHECK
# ============================================================

print()
print("=" * 70)
print("COLUMN CHECK")
print("=" * 70)

actual_columns = financials.columns.tolist()

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in actual_columns
]

extra_columns = [
    column
    for column in actual_columns
    if column not in EXPECTED_COLUMNS
]

print("Expected columns:", len(EXPECTED_COLUMNS))
print("Actual columns:", len(actual_columns))
print("Missing columns:", len(missing_columns))
print("Extra columns:", len(extra_columns))

if missing_columns:
    print("Missing:", missing_columns)
    raise ValueError(
        "Required columns are missing."
    )

if extra_columns:
    print("Extra:", extra_columns)
    raise ValueError(
        "Unexpected columns found in financial CSV."
    )


# ============================================================
# ISO3 CHECK
# ============================================================

print()
print("=" * 70)
print("ISO3 CHECK")
print("=" * 70)

financials["iso3_code"] = (
    financials["iso3_code"]
    .astype(str)
    .str.strip()
    .str.upper()
)

invalid_iso3_mask = (
    (financials["iso3_code"].eq("")) |
    (financials["iso3_code"].str.len() != 3) |
    (~financials["iso3_code"].str.match(
        r"^[A-Z]{3}$",
        na=False
    ))
)

invalid_iso3 = int(
    invalid_iso3_mask.sum()
)

print(
    "Invalid ISO3 records:",
    invalid_iso3
)

if invalid_iso3:

    print(
        financials.loc[
            invalid_iso3_mask,
            ["iso3_code", "bank_name"]
        ].to_string(index=False)
    )

    raise ValueError(
        "Invalid ISO3 records found."
    )


# ============================================================
# KEY TEXT CHECK
# ============================================================

print()
print("=" * 70)
print("KEY TEXT CHECK")
print("=" * 70)

financials["bank_name"] = (
    financials["bank_name"]
    .astype(str)
    .str.strip()
)

blank_iso3 = int(
    financials["iso3_code"].eq("").sum()
)

blank_bank_names = int(
    financials["bank_name"].eq("").sum()
)

print(
    "Blank ISO3:",
    blank_iso3
)

print(
    "Blank bank names:",
    blank_bank_names
)

if blank_iso3 or blank_bank_names:
    raise ValueError(
        "Blank key fields found."
    )


# ============================================================
# FISCAL YEAR CHECK
# ============================================================

print()
print("=" * 70)
print("FISCAL YEAR CHECK")
print("=" * 70)

financials["fiscal_year"] = pd.to_numeric(
    financials["fiscal_year"],
    errors="coerce"
)

invalid_year_mask = (
    (financials["fiscal_year"].isna()) |
    (financials["fiscal_year"] % 1 != 0) |
    (financials["fiscal_year"] < 1900) |
    (financials["fiscal_year"] > 2100)
)

invalid_years = int(
    invalid_year_mask.sum()
)

years = sorted(
    financials["fiscal_year"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

print(
    "Invalid fiscal years:",
    invalid_years
)

print(
    "Years:",
    years
)

if invalid_years:
    raise ValueError(
        "Invalid fiscal years found."
    )

financials["fiscal_year"] = (
    financials["fiscal_year"]
    .astype(int)
)


# ============================================================
# DUPLICATE CHECK
# ============================================================

print()
print("=" * 70)
print("BANK / YEAR DUPLICATE CHECK")
print("=" * 70)

duplicate_mask = financials.duplicated(
    subset=[
        "iso3_code",
        "bank_name",
        "fiscal_year",
    ],
    keep=False
)

duplicate_rows = int(
    duplicate_mask.sum()
)

duplicate_groups = (
    financials.loc[
        duplicate_mask,
        [
            "iso3_code",
            "bank_name",
            "fiscal_year",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print(
    "Duplicate rows:",
    duplicate_rows
)

print(
    "Duplicate groups:",
    duplicate_groups
)

if duplicate_rows:

    print(
        financials.loc[
            duplicate_mask,
            [
                "iso3_code",
                "bank_name",
                "fiscal_year",
            ]
        ]
        .sort_values(
            [
                "iso3_code",
                "bank_name",
                "fiscal_year",
            ]
        )
        .to_string(index=False)
    )

    raise ValueError(
        "Duplicate bank/year records found."
    )


# ============================================================
# NUMERIC FIELD NORMALIZATION
# ============================================================

print()
print("=" * 70)
print("NUMERIC FIELD CHECK")
print("=" * 70)

numeric_error_count = 0
numeric_missing_count = 0

for column in NUMERIC_COLUMNS:

    financials[column] = (
        financials[column]
        .astype(str)
        .str.strip()
    )

    financials[column] = financials[column].apply(
        lambda value:
            None
            if value in MISSING_DATA_MARKERS
            else value
    )

    original_values = financials[column].copy()

    numeric_values = pd.to_numeric(
        original_values,
        errors="coerce"
    )

    non_missing_mask = (
        original_values.notna()
    )

    invalid_mask = (
        non_missing_mask &
        numeric_values.isna()
    )

    errors = int(
        invalid_mask.sum()
    )

    if errors:

        print()
        print(
            f"{column}: "
            f"{errors} invalid values"
        )

        print(
            financials.loc[
                invalid_mask,
                [
                    "iso3_code",
                    "bank_name",
                    "fiscal_year",
                    column,
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

        numeric_error_count += errors

    financials[column] = numeric_values

    missing_count = int(
        financials[column].isna().sum()
    )

    numeric_missing_count += missing_count

    if missing_count:

        print(
            f"{column}: "
            f"{missing_count} missing/unavailable"
        )


print()
print(
    "Numeric errors:",
    numeric_error_count
)

print(
    "Numeric missing/unavailable values:",
    numeric_missing_count
)

if numeric_error_count:
    raise ValueError(
        "Invalid numeric values found."
    )

print(
    "All numeric fields are valid."
)


# ============================================================
# INTEGER FIELD NORMALIZATION
# ============================================================

print()
print("=" * 70)
print("INTEGER FIELD CHECK")
print("=" * 70)

integer_error_count = 0

for column in COUNT_COLUMNS:

    financials[column] = (
        financials[column]
        .astype(str)
        .str.strip()
    )

    financials[column] = financials[column].apply(
        lambda value:
            None
            if value in MISSING_DATA_MARKERS
            else value
    )

    original_values = financials[column].copy()

    numeric_values = pd.to_numeric(
        original_values,
        errors="coerce"
    )

    non_missing_mask = (
        original_values.notna()
    )

    invalid_mask = (
        non_missing_mask &
        (
            numeric_values.isna() |
            ((numeric_values % 1) != 0)
        )
    )

    errors = int(
        invalid_mask.sum()
    )

    if errors:

        print()
        print(
            f"{column}: "
            f"{errors} invalid values"
        )

        print(
            financials.loc[
                invalid_mask,
                [
                    "iso3_code",
                    "bank_name",
                    "fiscal_year",
                    column,
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

        integer_error_count += errors

    financials[column] = numeric_values


print()
print(
    "Integer errors:",
    integer_error_count
)

if integer_error_count:
    raise ValueError(
        "Invalid integer values found."
    )


# ============================================================
# POSTGRES INTEGER RANGE CHECK
# ============================================================

print()
print("=" * 70)
print("POSTGRESQL INTEGER RANGE CHECK")
print("=" * 70)

range_errors = 0

for column in INTEGER_COLUMNS:

    values = financials[column]

    below_min_mask = (
        values.notna() &
        (values < POSTGRES_INTEGER_MIN)
    )

    above_max_mask = (
        values.notna() &
        (values > POSTGRES_INTEGER_MAX)
    )

    invalid_range_mask = (
        below_min_mask |
        above_max_mask
    )

    errors = int(
        invalid_range_mask.sum()
    )

    if errors:

        print()
        print(
            f"{column}: "
            f"{errors} out-of-range values"
        )

        print(
            financials.loc[
                invalid_range_mask,
                [
                    "iso3_code",
                    "bank_name",
                    "fiscal_year",
                    column,
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

        range_errors += errors


print(
    "Out-of-range INTEGER records:",
    range_errors
)

if range_errors:
    raise ValueError(
        "PostgreSQL INTEGER range violation found."
    )

print(
    "All INTEGER fields are within "
    "PostgreSQL INTEGER range."
)


# ============================================================
# KEY NULL CHECK
# ============================================================

print()
print("=" * 70)
print("KEY NULL CHECK")
print("=" * 70)

null_key_errors = 0

for column in [
    "iso3_code",
    "bank_name",
    "fiscal_year",
]:

    count = int(
        financials[column].isna().sum()
    )

    print(
        f"{column}:",
        count
    )

    null_key_errors += count


if null_key_errors:
    raise ValueError(
        "NULL key values found."
    )


# ============================================================
# FINANCIAL LOGIC CHECK
# ============================================================

print()
print("=" * 70)
print("FINANCIAL LOGIC CHECK")
print("=" * 70)

logic_errors = []


negative_assets = financials[
    financials["total_assets"].notna() &
    (financials["total_assets"] < 0)
]

if len(negative_assets):
    logic_errors.append(
        f"Negative total_assets: "
        f"{len(negative_assets)}"
    )


negative_deposits = financials[
    financials["total_deposits"].notna() &
    (financials["total_deposits"] < 0)
]

if len(negative_deposits):
    logic_errors.append(
        f"Negative total_deposits: "
        f"{len(negative_deposits)}"
    )


negative_loans = financials[
    financials["total_loans"].notna() &
    (financials["total_loans"] < 0)
]

if len(negative_loans):
    logic_errors.append(
        f"Negative total_loans: "
        f"{len(negative_loans)}"
    )


negative_employees = financials[
    financials["employees"].notna() &
    (financials["employees"] < 0)
]

if len(negative_employees):
    logic_errors.append(
        f"Negative employees: "
        f"{len(negative_employees)}"
    )


negative_branches = financials[
    financials["branches"].notna() &
    (financials["branches"] < 0)
]

if len(negative_branches):
    logic_errors.append(
        f"Negative branches: "
        f"{len(negative_branches)}"
    )


for error in logic_errors:

    print(
        "ERROR:",
        error
    )


print(
    "Financial logic errors:",
    len(logic_errors)
)

if logic_errors:
    raise ValueError(
        "Financial logic validation failed."
    )


# ============================================================
# RATIO SANITY CHECK
# ============================================================

print()
print("=" * 70)
print("RATIO SANITY CHECK")
print("=" * 70)

ratio_columns = [
    "roe_percent",
    "roa_percent",
    "capital_adequacy_percent",
    "cost_income_ratio",
    "loan_to_deposit_ratio",
    "npl_ratio",
]

for column in ratio_columns:

    values = financials[column].dropna()

    if len(values) == 0:
        continue

    print(
        f"{column}: "
        f"min={values.min()} | "
        f"max={values.max()}"
    )


# ============================================================
# POSTGRESQL CONNECTION
# ============================================================

print()
print("=" * 70)
print("POSTGRESQL CONNECTION")
print("=" * 70)

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = connection.cursor()

print(
    "Connected to database:",
    DB_NAME
)


# ============================================================
# DATABASE TABLE CHECK
# ============================================================

print()
print("=" * 70)
print("DATABASE TABLE CHECK")
print("=" * 70)

required_tables = [
    "countries",
    "banks",
    "bank_financials",
]

for table in required_tables:

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        )
        """,
        (table,)
    )

    exists = cursor.fetchone()[0]

    print(
        f"{table}:",
        "FOUND" if exists else "MISSING"
    )

    if not exists:

        cursor.close()
        connection.close()

        raise ValueError(
            f"Missing database table: {table}"
        )


# ============================================================
# BANK REFERENCE CHECK
# ============================================================

print()
print("=" * 70)
print("BANK REFERENCE CHECK")
print("=" * 70)

cursor.execute(
    """
    SELECT
        iso3_code,
        bank_name
    FROM banks
    """
)

bank_rows = cursor.fetchall()

bank_keys = {
    (
        str(iso3).strip().upper(),
        str(bank_name).strip()
    )
    for iso3, bank_name in bank_rows
}

csv_bank_keys = set(
    zip(
        financials["iso3_code"],
        financials["bank_name"]
    )
)

missing_banks = (
    csv_bank_keys -
    bank_keys
)

print(
    "Unique financial banks:",
    len(csv_bank_keys)
)

print(
    "Missing bank references:",
    len(missing_banks)
)

if missing_banks:

    for item in sorted(missing_banks):
        print(item)

    raise ValueError(
        "Financial records reference "
        "missing banks."
    )


# ============================================================
# COUNTRY REFERENCE CHECK
# ============================================================

print()
print("=" * 70)
print("COUNTRY REFERENCE CHECK")
print("=" * 70)

cursor.execute(
    """
    SELECT iso3_code
    FROM countries
    """
)

country_rows = cursor.fetchall()

country_codes = {
    str(row[0]).strip().upper()
    for row in country_rows
}

csv_country_codes = set(
    financials["iso3_code"]
)

missing_countries = (
    csv_country_codes -
    country_codes
)

print(
    "Financial countries:",
    len(csv_country_codes)
)

print(
    "Missing country references:",
    len(missing_countries)
)

if missing_countries:

    print(
        sorted(missing_countries)
    )

    raise ValueError(
        "Financial records reference "
        "missing countries."
    )


# ============================================================
# DATABASE FINANCIAL COUNT
# ============================================================

print()
print("=" * 70)
print("DATABASE FINANCIAL COUNT")
print("=" * 70)

cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials
    """
)

database_financial_count = (
    cursor.fetchone()[0]
)

csv_financial_count = len(
    financials
)

print(
    "CSV financial records:",
    csv_financial_count
)

print(
    "Database financial records:",
    database_financial_count
)


# ============================================================
# DATABASE DUPLICATE CHECK
# ============================================================

print()
print("=" * 70)
print("DATABASE DUPLICATE CHECK")
print("=" * 70)

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

    HAVING COUNT(*) > 1
    """
)

database_duplicates = cursor.fetchall()

print(
    "Duplicate database groups:",
    len(database_duplicates)
)

if database_duplicates:

    for row in database_duplicates[:20]:
        print(row)

    raise ValueError(
        "Duplicate bank/year groups "
        "exist in database."
    )


# ============================================================
# DATABASE REFERENTIAL INTEGRITY
# ============================================================

print()
print("=" * 70)
print("DATABASE REFERENTIAL INTEGRITY")
print("=" * 70)

cursor.execute(
    """
    SELECT COUNT(*)

    FROM bank_financials f

    LEFT JOIN banks b
        ON f.iso3_code = b.iso3_code
       AND f.bank_name = b.bank_name

    WHERE b.bank_id IS NULL
    """
)

orphan_banks = cursor.fetchone()[0]


cursor.execute(
    """
    SELECT COUNT(*)

    FROM bank_financials f

    LEFT JOIN countries c
        ON f.iso3_code = c.iso3_code

    WHERE c.iso3_code IS NULL
    """
)

orphan_countries = cursor.fetchone()[0]


print(
    "Orphan financial records:",
    orphan_banks
)

print(
    "Orphan country references:",
    orphan_countries
)

if orphan_banks:
    raise ValueError(
        "Orphan financial records found."
    )

if orphan_countries:
    raise ValueError(
        "Orphan country references found."
    )


# ============================================================
# CSV → DATABASE RECONCILIATION
# ============================================================

print()
print("=" * 70)
print("CSV → DATABASE RECONCILIATION")
print("=" * 70)

if (
    csv_financial_count !=
    database_financial_count
):

    raise ValueError(
        "CSV and PostgreSQL financial "
        "record counts differ."
    )

print(
    "CSV financial records:",
    csv_financial_count
)

print(
    "Database financial records:",
    database_financial_count
)

print(
    "STATUS: PASS"
)


# ============================================================
# ANALYTICAL VIEW CHECK
# ============================================================

print()
print("=" * 70)
print("ANALYTICAL VIEW CHECK")
print("=" * 70)

required_views = [
    "vw_bank_financial_performance",
    "vw_country_financial_summary",
    "vw_global_banking_yearly_summary",
    "vw_latest_bank_financials",
    "vw_bank_yearly_performance",
]

for view_name in required_views:

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name = %s
        )
        """,
        (view_name,)
    )

    exists = cursor.fetchone()[0]

    print(
        f"{view_name}:",
        "FOUND" if exists else "MISSING"
    )

    if not exists:

        raise ValueError(
            f"Required analytical view missing: "
            f"{view_name}"
        )


# ============================================================
# ANALYTICAL VIEW ROW COUNTS
# ============================================================

print()
print("=" * 70)
print("ANALYTICAL VIEW ROW COUNTS")
print("=" * 70)

expected_view_counts = {
    "vw_bank_financial_performance": 5904,
    "vw_country_financial_summary": 1089,
    "vw_global_banking_yearly_summary": 6,
    "vw_latest_bank_financials": 1114,
    "vw_bank_yearly_performance": 5904,
}

for view_name, expected_count in (
    expected_view_counts.items()
):

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {view_name}
        """
    )

    actual_count = cursor.fetchone()[0]

    print(
        f"{view_name}: "
        f"{actual_count:,} rows"
    )

    if actual_count != expected_count:

        raise ValueError(
            f"Unexpected row count in "
            f"{view_name}. "
            f"Expected {expected_count}, "
            f"got {actual_count}."
        )


# ============================================================
# CLOSE DATABASE
# ============================================================

cursor.close()
connection.close()


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 70)
print("FINAL FINANCIAL VALIDATION")
print("=" * 70)

print()
print(
    "CSV records:",
    csv_financial_count
)

print(
    "Database records:",
    database_financial_count
)

print(
    "Invalid ISO3:",
    invalid_iso3
)

print(
    "Duplicate rows:",
    duplicate_rows
)

print(
    "Duplicate groups:",
    duplicate_groups
)

print(
    "Numeric errors:",
    numeric_error_count
)

print(
    "Integer errors:",
    integer_error_count
)

print(
    "INTEGER range errors:",
    range_errors
)

print(
    "Missing banks:",
    len(missing_banks)
)

print(
    "Missing countries:",
    len(missing_countries)
)

print(
    "Orphan banks:",
    orphan_banks
)

print(
    "Orphan countries:",
    orphan_countries
)

print()
print("STATUS: PASS")

print()
print(
    "FINANCIAL DATA IS READY FOR POWER BI."
)

print()
print(
    "Database:",
    DB_NAME
)

print("=" * 70)
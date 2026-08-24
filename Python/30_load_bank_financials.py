import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from decimal import Decimal, InvalidOperation
from pathlib import Path


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 30 — LOAD BANK FINANCIALS TO POSTGRESQL
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = Path(
    "Data/Raw/bank_financials_synthetic.csv"
)

DB_NAME = "gbip"
DB_USER = "postgres"
DB_PASSWORD = "xxxx
DB_HOST = "localhost"
DB_PORT = xxxx


# ============================================================
# EXPECTED CSV STRUCTURE
# ============================================================

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


INSERT_COLUMNS = [
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


POSTGRES_INTEGER_MIN = -2147483648
POSTGRES_INTEGER_MAX = 2147483647


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_missing(value):
    """
    Detect all forms of missing data safely.

    This includes:
    - None
    - NaN
    - pandas NA
    - NaT
    - empty strings
    - NULL
    - none
    - pending public data
    """

    if value is None:
        return True

    try:

        if pd.isna(value):
            return True

    except (TypeError, ValueError):

        pass

    text = str(value).strip()

    if text == "":
        return True

    if text.lower() in {
        "nan",
        "nat",
        "none",
        "null",
        "pending public data",
    }:

        return True

    return False


def clean_text(value):

    if is_missing(value):
        return None

    return str(value).strip()


def clean_integer(value, column_name):

    if is_missing(value):
        return None

    text = str(value).strip()

    try:

        numeric_value = float(text)

    except (ValueError, TypeError):

        raise ValueError(
            f"Invalid integer value in "
            f"{column_name}: {value!r}"
        )

    if not numeric_value.is_integer():

        raise ValueError(
            f"Non-integer value in "
            f"{column_name}: {value!r}"
        )

    integer_value = int(numeric_value)

    if (
        integer_value < POSTGRES_INTEGER_MIN
        or
        integer_value > POSTGRES_INTEGER_MAX
    ):

        raise ValueError(
            f"PostgreSQL INTEGER overflow in "
            f"{column_name}: {integer_value}"
        )

    return integer_value


def clean_numeric(value, column_name):

    if is_missing(value):
        return None

    text = str(value).strip()

    text = (
        text
        .replace(",", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
    )

    try:

        numeric_value = Decimal(text)

    except InvalidOperation:

        raise ValueError(
            f"Invalid numeric value in "
            f"{column_name}: {value!r}"
        )

    if not numeric_value.is_finite():

        raise ValueError(
            f"Non-finite numeric value in "
            f"{column_name}: {value!r}"
        )

    return numeric_value


def postgres_safe_value(value):
    """
    Convert pandas/numpy missing values to Python None.

    This is critical because PostgreSQL accepts:
        None -> SQL NULL

    but does NOT safely accept:
        numpy.nan
    """

    if is_missing(value):
        return None

    # Convert numpy scalar values to normal Python values.
    if hasattr(value, "item"):

        try:
            value = value.item()

        except (ValueError, TypeError):

            pass

    return value


# ============================================================
# INSERT QUERY
# ============================================================

INSERT_QUERY = """
INSERT INTO bank_financials (
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
VALUES %s

ON CONFLICT (
    iso3_code,
    bank_name,
    fiscal_year
)

DO UPDATE SET

    total_assets =
        EXCLUDED.total_assets,

    total_deposits =
        EXCLUDED.total_deposits,

    total_loans =
        EXCLUDED.total_loans,

    shareholders_equity =
        EXCLUDED.shareholders_equity,

    operating_income =
        EXCLUDED.operating_income,

    net_income =
        EXCLUDED.net_income,

    roe_percent =
        EXCLUDED.roe_percent,

    roa_percent =
        EXCLUDED.roa_percent,

    capital_adequacy_percent =
        EXCLUDED.capital_adequacy_percent,

    cost_income_ratio =
        EXCLUDED.cost_income_ratio,

    loan_to_deposit_ratio =
        EXCLUDED.loan_to_deposit_ratio,

    npl_ratio =
        EXCLUDED.npl_ratio,

    employees =
        EXCLUDED.employees,

    branches =
        EXCLUDED.branches,

    reporting_currency =
        EXCLUDED.reporting_currency,

    source =
        EXCLUDED.source
"""


# ============================================================
# START
# ============================================================

print("=" * 70)
print("BANK FINANCIALS — DATABASE LOAD")
print("=" * 70)


# ============================================================
# FILE CHECK
# ============================================================

if not CSV_FILE.exists():

    raise FileNotFoundError(
        f"Financial CSV not found:\n{CSV_FILE}"
    )


print()
print("Input file:")
print(CSV_FILE)


# ============================================================
# LOAD CSV
# ============================================================

financials = pd.read_csv(
    CSV_FILE,
    dtype=str,
    low_memory=False
)


financials.columns = (
    financials.columns
    .str.strip()
)


print()
print("=" * 70)
print("BANK FINANCIALS — SYNTHETIC DATA LOADED")
print("=" * 70)

print(
    "Rows:",
    len(financials)
)

print(
    "Columns:",
    len(financials.columns)
)

print(
    "Column names:"
)

print(
    financials.columns.tolist()
)


# ============================================================
# COLUMN CHECK
# ============================================================

print()
print("=" * 70)
print("COLUMN CHECK")
print("=" * 70)


missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in financials.columns
]


extra_columns = [
    column
    for column in financials.columns
    if column not in EXPECTED_COLUMNS
]


print(
    "Expected CSV columns:",
    len(EXPECTED_COLUMNS)
)

print(
    "Actual CSV columns:",
    len(financials.columns)
)

print(
    "Missing columns:",
    len(missing_columns)
)

print(
    "Extra columns:",
    len(extra_columns)
)


if missing_columns:

    print(
        "Missing columns:",
        missing_columns
    )

    raise ValueError(
        "Required financial columns are missing."
    )


if extra_columns:

    print(
        "Extra columns:",
        extra_columns
    )

    raise ValueError(
        "Unexpected columns found in financial CSV."
    )


financials = financials[
    EXPECTED_COLUMNS
].copy()


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


invalid_iso3 = financials[
    (
        financials["iso3_code"].isna()
    )
    |
    (
        financials["iso3_code"].str.len() != 3
    )
    |
    (
        ~financials["iso3_code"].str.match(
            r"^[A-Z]{3}$",
            na=False
        )
    )
]


print(
    "Invalid ISO3 records:",
    len(invalid_iso3)
)


if len(invalid_iso3) > 0:

    print(
        invalid_iso3[
            [
                "iso3_code",
                "bank_name",
                "fiscal_year",
            ]
        ].to_string(
            index=False
        )
    )

    raise ValueError(
        "Invalid ISO3 records found."
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


duplicate_rows = financials[
    duplicate_mask
]


duplicate_groups = (
    financials[
        duplicate_mask
    ]
    .groupby(
        [
            "iso3_code",
            "bank_name",
            "fiscal_year",
        ]
    )
    .ngroups
)


print(
    "Duplicate rows:",
    len(duplicate_rows)
)

print(
    "Duplicate groups:",
    duplicate_groups
)


if len(duplicate_rows) > 0:

    print(
        duplicate_rows[
            [
                "iso3_code",
                "bank_name",
                "fiscal_year",
            ]
        ].to_string(
            index=False
        )
    )

    raise ValueError(
        "Duplicate bank/year records found."
    )


# ============================================================
# YEAR VALIDATION
# ============================================================

print()
print("=" * 70)
print("YEAR COVERAGE")
print("=" * 70)


year_numeric = pd.to_numeric(
    financials["fiscal_year"],
    errors="coerce"
)


invalid_year = (
    year_numeric.isna()
    |
    (
        year_numeric
        !=
        year_numeric.round()
    )
)


print(
    "Invalid fiscal years:",
    int(invalid_year.sum())
)


if invalid_year.any():

    print(
        financials.loc[
            invalid_year,
            [
                "iso3_code",
                "bank_name",
                "fiscal_year",
            ]
        ].to_string(
            index=False
        )
    )

    raise ValueError(
        "Invalid fiscal year values found."
    )


financials["fiscal_year"] = (
    year_numeric.astype(int)
)


years = sorted(
    financials["fiscal_year"]
    .unique()
    .tolist()
)


print(
    "Years:",
    years
)


# ============================================================
# KEY NORMALIZATION
# ============================================================

print()
print("=" * 70)
print("KEY NULL CHECK")
print("=" * 70)


financials["bank_name"] = (
    financials["bank_name"]
    .astype(str)
    .str.strip()
)


null_key_mask = (
    financials["iso3_code"].eq("")
    |
    financials["bank_name"].eq("")
    |
    financials["fiscal_year"].isna()
)


print(
    "Rows with NULL key values:",
    int(null_key_mask.sum())
)


if null_key_mask.any():

    print(
        financials.loc[
            null_key_mask,
            [
                "iso3_code",
                "bank_name",
                "fiscal_year",
            ]
        ].to_string(
            index=False
        )
    )

    raise ValueError(
        "Financial records contain NULL key values."
    )


# ============================================================
# NUMERIC NORMALIZATION
# ============================================================

print()
print("=" * 70)
print("NUMERIC FIELD NORMALIZATION")
print("=" * 70)


for column in NUMERIC_COLUMNS:

    financials[column] = financials[
        column
    ].apply(
        lambda value,
        column_name=column:
        clean_numeric(
            value,
            column_name
        )
    )


print(
    "Financial numeric fields normalized:",
    len(NUMERIC_COLUMNS)
)


# ============================================================
# INTEGER NORMALIZATION
# ============================================================

print()
print("=" * 70)
print("INTEGER FIELD NORMALIZATION")
print("=" * 70)


for column in [
    "employees",
    "branches",
]:

    financials[column] = financials[
        column
    ].apply(
        lambda value,
        column_name=column:
        clean_integer(
            value,
            column_name
        )
    )


print(
    "Integer fields normalized:"
)

print(
    "employees"
)

print(
    "branches"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

print()
print("=" * 70)
print("TEXT FIELD NORMALIZATION")
print("=" * 70)


for column in [
    "reporting_currency",
    "source",
]:

    financials[column] = financials[
        column
    ].apply(clean_text)


# ============================================================
# INTEGER RANGE CHECK
# ============================================================

print()
print("=" * 70)
print("POSTGRESQL INTEGER RANGE CHECK")
print("=" * 70)


range_errors = []


for column in INTEGER_COLUMNS:

    for index, value in financials[
        column
    ].items():

        if is_missing(value):
            continue

        integer_value = int(value)

        if (
            integer_value < POSTGRES_INTEGER_MIN
            or
            integer_value > POSTGRES_INTEGER_MAX
        ):

            range_errors.append(
                {
                    "csv_row": index + 2,
                    "column": column,
                    "value": integer_value,
                    "iso3_code":
                        financials.loc[
                            index,
                            "iso3_code"
                        ],
                    "bank_name":
                        financials.loc[
                            index,
                            "bank_name"
                        ],
                    "fiscal_year":
                        financials.loc[
                            index,
                            "fiscal_year"
                        ],
                }
            )


print(
    "Out-of-range INTEGER records:",
    len(range_errors)
)


if range_errors:

    print(
        pd.DataFrame(
            range_errors
        ).to_string(
            index=False
        )
    )

    raise ValueError(
        "PostgreSQL INTEGER overflow detected."
    )


print(
    "All INTEGER fields are within PostgreSQL INTEGER range."
)


# ============================================================
# POSTGRESQL CONNECTION
# ============================================================

print()
print("=" * 70)
print("POSTGRESQL CONNECTION")
print("=" * 70)


print(
    "Connecting to PostgreSQL..."
)


connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


connection.autocommit = False


cursor = connection.cursor()


print(
    "Connected to database:",
    DB_NAME
)


# ============================================================
# DATABASE INTEGER COLUMN CHECK
# ============================================================

print()
print("=" * 70)
print("DATABASE INTEGER COLUMN CHECK")
print("=" * 70)


cursor.execute(
    """
    SELECT
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'bank_financials'
      AND data_type IN (
          'integer',
          'bigint',
          'smallint'
      )
    ORDER BY ordinal_position
    """
)


database_integer_columns = (
    cursor.fetchall()
)


for column_name, data_type in (
    database_integer_columns
):

    print(
        f"{column_name}: {data_type}"
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


bank_master = {
    (
        str(row[0]).strip(),
        str(row[1]).strip()
    )
    for row in bank_rows
}


financial_bank_keys = set(
    zip(
        financials["iso3_code"],
        financials["bank_name"]
    )
)


missing_banks = sorted(
    financial_bank_keys
    -
    bank_master
)


print(
    "Unique financial banks:",
    len(financial_bank_keys)
)

print(
    "Financial bank references missing from banks:",
    len(missing_banks)
)


if missing_banks:

    print()

    for bank in missing_banks:
        print(bank)

    connection.rollback()
    cursor.close()
    connection.close()

    raise ValueError(
        "Financial records reference banks "
        "that do not exist in the banks table."
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


country_codes = {
    str(row[0]).strip()
    for row in cursor.fetchall()
}


financial_country_codes = set(
    financials["iso3_code"]
)


missing_countries = sorted(
    financial_country_codes
    -
    country_codes
)


print(
    "Financial countries:",
    len(financial_country_codes)
)

print(
    "Countries missing from countries table:",
    len(missing_countries)
)


if missing_countries:

    print(
        missing_countries
    )

    connection.rollback()
    cursor.close()
    connection.close()

    raise ValueError(
        "Financial records reference countries "
        "that do not exist in countries table."
    )


# ============================================================
# CURRENT DATABASE COUNT
# ============================================================

print()
print("=" * 70)
print("CURRENT DATABASE FINANCIALS")
print("=" * 70)


cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials
    """
)


before_count = cursor.fetchone()[0]


print(
    "Current bank financial records:",
    before_count
)


# ============================================================
# PREPARE RECORDS
# ============================================================

print()
print("=" * 70)
print("PREPARING DATABASE LOAD")
print("=" * 70)


records = []


for _, row in financials.iterrows():

    record = tuple(
        postgres_safe_value(
            row[column]
        )
        for column in INSERT_COLUMNS
    )

    records.append(record)


print(
    "Records prepared:",
    len(records)
)


# ============================================================
# VERIFY NO NaN IS BEING SENT TO POSTGRESQL
# ============================================================

print()
print("=" * 70)
print("POSTGRESQL NULL / NaN SAFETY CHECK")
print("=" * 70)


nan_records = []


for record_number, record in enumerate(
    records,
    start=1
):

    for column_number, value in enumerate(
        record
    ):

        if isinstance(value, float):

            if pd.isna(value):

                nan_records.append(
                    (
                        record_number,
                        INSERT_COLUMNS[
                            column_number
                        ],
                        value
                    )
                )


print(
    "NaN values remaining in records:",
    len(nan_records)
)


if nan_records:

    for item in nan_records[:20]:
        print(item)

    connection.rollback()
    cursor.close()
    connection.close()

    raise ValueError(
        "NaN values remain in prepared "
        "PostgreSQL records."
    )


print(
    "All missing values will be sent as SQL NULL."
)


# ============================================================
# SAVEPOINT BATCH TEST
# ============================================================

def test_batch(batch):

    cursor.execute(
        "SAVEPOINT financial_load_test"
    )

    try:

        execute_values(
            cursor,
            INSERT_QUERY,
            batch,
            page_size=min(
                500,
                max(1, len(batch))
            )
        )

        cursor.execute(
            """
            ROLLBACK TO SAVEPOINT
            financial_load_test
            """
        )

        cursor.execute(
            """
            RELEASE SAVEPOINT
            financial_load_test
            """
        )

        return True, None

    except Exception as error:

        cursor.execute(
            """
            ROLLBACK TO SAVEPOINT
            financial_load_test
            """
        )

        cursor.execute(
            """
            RELEASE SAVEPOINT
            financial_load_test
            """
        )

        return False, error


# ============================================================
# PRE-LOAD DATABASE TEST
# ============================================================

print()
print("=" * 70)
print("PRE-LOAD DATABASE TEST")
print("=" * 70)


full_test_success, full_test_error = (
    test_batch(records)
)


if full_test_success:

    print(
        "Full dataset test: PASS"
    )


else:

    print(
        "Full dataset test: FAILED"
    )

    print()
    print(
        "PostgreSQL error:"
    )

    print(
        full_test_error
    )

    print()
    print(
        "Starting exact-record isolation..."
    )


# ============================================================
# FAILURE ISOLATION
# ============================================================

if not full_test_success:

    bad_records = records[:]

    while len(bad_records) > 1:

        midpoint = len(
            bad_records
        ) // 2

        left_records = (
            bad_records[:midpoint]
        )

        right_records = (
            bad_records[midpoint:]
        )


        left_success, left_error = (
            test_batch(
                left_records
            )
        )


        if not left_success:

            bad_records = left_records

            print(
                "Failure is in LEFT half:",
                len(bad_records),
                "records"
            )

            continue


        right_success, right_error = (
            test_batch(
                right_records
            )
        )


        if not right_success:

            bad_records = right_records

            print(
                "Failure is in RIGHT half:",
                len(bad_records),
                "records"
            )

            continue


        # ----------------------------------------------------
        # If neither half fails, test records individually.
        # ----------------------------------------------------

        break


    # ========================================================
    # INDIVIDUAL FAILURE
    # ========================================================

    if len(bad_records) == 1:

        bad_record = bad_records[0]

        bad_index = records.index(
            bad_record
        )

        bad_row = financials.iloc[
            bad_index
        ]


        print()
        print("=" * 70)
        print("EXACT OFFENDING RECORD")
        print("=" * 70)


        print(
            "CSV row:",
            bad_index + 2
        )

        print(
            "ISO3:",
            bad_row["iso3_code"]
        )

        print(
            "Bank:",
            bad_row["bank_name"]
        )

        print(
            "Fiscal year:",
            bad_row["fiscal_year"]
        )

        print(
            "Employees:",
            bad_row["employees"]
        )

        print(
            "Branches:",
            bad_row["branches"]
        )


        print()
        print(
            "COMPLETE RECORD:"
        )


        for column in INSERT_COLUMNS:

            print(
                f"{column}: "
                f"{bad_row[column]!r}"
            )


        print()
        print("=" * 70)
        print("EXACT POSTGRESQL ERROR")
        print("=" * 70)


        _, exact_error = test_batch(
            [bad_record]
        )


        print(
            exact_error
        )


        connection.rollback()

        cursor.close()
        connection.close()


        raise ValueError(
            "Database load stopped. "
            "Exact offending record printed above."
        )


    # ========================================================
    # FALLBACK — TEST INDIVIDUAL RECORDS
    # ========================================================

    print()
    print(
        "Testing records individually..."
    )


    individual_failure = None


    for position, record in enumerate(
        records,
        start=1
    ):

        success, error = test_batch(
            [record]
        )


        if not success:

            individual_failure = (
                position,
                record,
                error
            )

            break


    if individual_failure is not None:

        position, record, error = (
            individual_failure
        )


        bad_index = position - 1

        bad_row = financials.iloc[
            bad_index
        ]


        print()
        print("=" * 70)
        print("EXACT OFFENDING RECORD")
        print("=" * 70)


        print(
            "CSV row:",
            bad_index + 2
        )

        print(
            "ISO3:",
            bad_row["iso3_code"]
        )

        print(
            "Bank:",
            bad_row["bank_name"]
        )

        print(
            "Fiscal year:",
            bad_row["fiscal_year"]
        )


        print()
        print(
            "COMPLETE RECORD:"
        )


        for column in INSERT_COLUMNS:

            print(
                f"{column}: "
                f"{bad_row[column]!r}"
            )


        print()
        print("=" * 70)
        print("POSTGRESQL ERROR")
        print("=" * 70)

        print(
            error
        )


        connection.rollback()

        cursor.close()
        connection.close()


        raise ValueError(
            "Exact failing financial record "
            "identified. No data committed."
        )


    connection.rollback()

    cursor.close()
    connection.close()


    raise ValueError(
        "Batch-level PostgreSQL failure detected. "
        "No data committed."
    )


# ============================================================
# REAL DATABASE INSERT
# ============================================================

print()
print("=" * 70)
print("LOADING FINANCIAL RECORDS")
print("=" * 70)


try:

    execute_values(
        cursor,
        INSERT_QUERY,
        records,
        page_size=500
    )

    connection.commit()


    print()
    print(
        "Database transaction committed."
    )


except Exception as error:

    connection.rollback()


    print()
    print("=" * 70)
    print("DATABASE LOAD FAILED")
    print("=" * 70)

    print(
        "Transaction rolled back."
    )

    print()
    print(
        "PostgreSQL error:"
    )

    print(
        error
    )


    cursor.close()
    connection.close()

    raise


# ============================================================
# FINAL DATABASE COUNT
# ============================================================

print()
print("=" * 70)
print("FINAL DATABASE CHECK")
print("=" * 70)


cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials
    """
)


after_count = cursor.fetchone()[0]


print(
    "Financial records before load:",
    before_count
)

print(
    "Financial records after load:",
    after_count
)


# ============================================================
# INVALID ISO3 CHECK
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials
    WHERE iso3_code IS NULL
       OR LENGTH(TRIM(iso3_code)) != 3
    """
)


invalid_database_iso3 = (
    cursor.fetchone()[0]
)


print(
    "Invalid ISO3 records in database:",
    invalid_database_iso3
)


# ============================================================
# DUPLICATE CHECK
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
    HAVING COUNT(*) > 1
    """
)


database_duplicates = (
    cursor.fetchall()
)


print(
    "Duplicate bank/year groups in database:",
    len(database_duplicates)
)


# ============================================================
# BANK REFERENCE CHECK
# ============================================================

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


orphan_financials = (
    cursor.fetchone()[0]
)


print(
    "Orphan financial records:",
    orphan_financials
)


# ============================================================
# COUNTRY REFERENCE CHECK
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM bank_financials f
    LEFT JOIN countries c
        ON f.iso3_code = c.iso3_code
    WHERE c.iso3_code IS NULL
    """
)


orphan_countries = (
    cursor.fetchone()[0]
)


print(
    "Financial records with missing countries:",
    orphan_countries
)


# ============================================================
# YEAR CHECK
# ============================================================

cursor.execute(
    """
    SELECT
        MIN(fiscal_year),
        MAX(fiscal_year),
        COUNT(DISTINCT fiscal_year)
    FROM bank_financials
    """
)


min_year, max_year, year_count = (
    cursor.fetchone()
)


print(
    "Database fiscal year range:",
    min_year,
    "to",
    max_year
)

print(
    "Distinct fiscal years:",
    year_count
)


# ============================================================
# FINAL VALIDATION
# ============================================================

if after_count < len(financials):

    raise ValueError(
        "Database contains fewer financial "
        "records than the source CSV."
    )


if invalid_database_iso3 != 0:

    raise ValueError(
        "Invalid ISO3 records found in database."
    )


if len(database_duplicates) != 0:

    raise ValueError(
        "Duplicate bank/year records found."
    )


if orphan_financials != 0:

    raise ValueError(
        "Orphan financial records found."
    )


if orphan_countries != 0:

    raise ValueError(
        "Orphan country references found."
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()


# ============================================================
# FINAL SUCCESS
# ============================================================

print()
print("=" * 70)
print("BANK FINANCIALS — LOAD COMPLETE")
print("=" * 70)

print(
    "CSV financial records:",
    len(financials)
)

print(
    "Database financial records:",
    after_count
)

print(
    "Invalid ISO3:",
    invalid_database_iso3
)

print(
    "Duplicate groups:",
    len(database_duplicates)
)

print(
    "Orphan financial records:",
    orphan_financials
)

print(
    "Orphan country references:",
    orphan_countries
)

print(
    "Database:",
    DB_NAME
)

print()
print("=" * 70)
print("STATUS: SUCCESS")
print("=" * 70)

print(
    "DONE"
)

print("=" * 70)
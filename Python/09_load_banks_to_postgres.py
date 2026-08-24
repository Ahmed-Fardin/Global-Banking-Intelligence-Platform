import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 09 — LOAD BANK MASTER TO POSTGRESQL
# ============================================================

load_dotenv()


# ============================================================
# FILE
# ============================================================

BANKS_FILE = "Data/Raw/Banks/Mains/Banks.csv"


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
# EXPECTED CSV COLUMNS
# ============================================================

EXPECTED_COLUMNS = [
    "country_name",
    "iso3_code",
    "bank_name",
    "bank_type",
    "bank_rank",
    "headquarters_city",
    "official_website",
    "founded_year",
    "swift_code",
    "is_active",
    "data_source",
]


# ============================================================
# NULL / PLACEHOLDER VALUES
# ============================================================

NULL_VALUES = {
    "",
    "nan",
    "none",
    "null",
    "n/a",
    "na",
    "pending public data",
    "pending_public_data",
}


# ============================================================
# LOAD CSV
# ============================================================

banks = pd.read_csv(
    BANKS_FILE,
    low_memory=False
)

banks.columns = (
    banks.columns
    .str.strip()
)


print("=" * 70)
print("BANKS DATA LOADED")
print("=" * 70)

print(
    "Rows:",
    len(banks)
)

print(
    "Columns:"
)

print(
    banks.columns.tolist()
)


# ============================================================
# COLUMN CHECK
# ============================================================

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in banks.columns
]

extra_columns = [
    column
    for column in banks.columns
    if column not in EXPECTED_COLUMNS
]


if missing_columns:

    raise ValueError(
        "Missing required columns: "
        + str(missing_columns)
    )


if extra_columns:

    print(
        "Extra columns:",
        extra_columns
    )


# Keep only the columns used by the database
banks = banks[EXPECTED_COLUMNS].copy()


# ============================================================
# TEXT CLEANING FUNCTION
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in NULL_VALUES:
        return None

    return value


# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

TEXT_COLUMNS = [
    "country_name",
    "iso3_code",
    "bank_name",
    "bank_type",
    "headquarters_city",
    "official_website",
    "swift_code",
    "data_source",
]


for column in TEXT_COLUMNS:

    banks[column] = (
        banks[column]
        .apply(clean_text)
    )


# ============================================================
# ISO3 NORMALIZATION
# ============================================================

banks["iso3_code"] = (
    banks["iso3_code"]
    .apply(
        lambda value:
        value.upper()
        if value is not None
        else None
    )
)


# ============================================================
# INTEGER CLEANING
# ============================================================

def clean_integer(value):

    # IMPORTANT:
    # pandas represents blank numeric cells as NaN.
    # NaN must become Python None.
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in NULL_VALUES:
        return None

    try:

        numeric_value = float(value)

    except (ValueError, TypeError):

        raise ValueError(
            f"Invalid integer value: {value}"
        )

    if not numeric_value.is_integer():

        raise ValueError(
            f"Non-integer value found: {value}"
        )

    integer_value = int(numeric_value)

    # PostgreSQL INTEGER range
    if integer_value < -2147483648:

        raise ValueError(
            f"Value below PostgreSQL INTEGER range: "
            f"{integer_value}"
        )

    if integer_value > 2147483647:

        raise ValueError(
            f"Value above PostgreSQL INTEGER range: "
            f"{integer_value}"
        )

    return integer_value


# ============================================================
# CLEAN INTEGER COLUMNS
# ============================================================

banks["bank_rank"] = (
    banks["bank_rank"]
    .apply(clean_integer)
)

banks["founded_year"] = (
    banks["founded_year"]
    .apply(clean_integer)
)


# ============================================================
# BOOLEAN CLEANING
# ============================================================

def clean_boolean(value):

    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    if value in {
        "true",
        "1",
        "yes",
        "y",
    }:

        return True

    if value in {
        "false",
        "0",
        "no",
        "n",
    }:

        return False

    if value in NULL_VALUES:

        return None

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


banks["is_active"] = (
    banks["is_active"]
    .apply(clean_boolean)
)


# ============================================================
# SOURCE VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("SOURCE VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# ISO3 CHECK
# ------------------------------------------------------------

invalid_iso3 = banks[
    banks["iso3_code"].isna()
    |
    (banks["iso3_code"].str.len() != 3)
]


print(
    "Invalid ISO3 records:",
    len(invalid_iso3)
)


if len(invalid_iso3) > 0:

    print(
        invalid_iso3[
            [
                "country_name",
                "iso3_code",
                "bank_name",
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "Invalid ISO3 records found."
    )


# ------------------------------------------------------------
# DUPLICATE CHECK
# ------------------------------------------------------------

duplicates = banks[
    banks.duplicated(
        subset=[
            "iso3_code",
            "bank_name",
        ],
        keep=False
    )
]


print(
    "Duplicate rows:",
    len(duplicates)
)


if len(duplicates) > 0:

    print(
        duplicates[
            [
                "country_name",
                "iso3_code",
                "bank_name",
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "Duplicate bank records found."
    )


# ============================================================
# POSTGRESQL CONNECTION
# ============================================================

print("\n" + "=" * 70)
print("POSTGRESQL CONNECTION")
print("=" * 70)

print(
    "Connecting to PostgreSQL..."
)


conn = psycopg2.connect(
    **DB_CONFIG
)

cursor = conn.cursor()


print(
    "Connected to database:",
    DB_CONFIG["database"]
)


# ============================================================
# DATABASE BANK TABLE STRUCTURE
# ============================================================

print("\n" + "=" * 70)
print("DATABASE BANK TABLE")
print("=" * 70)


cursor.execute(
    """
    SELECT
        column_name,
        data_type,
        character_maximum_length,
        is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'banks'
    ORDER BY ordinal_position;
    """
)


db_columns = cursor.fetchall()


for row in db_columns:

    print(
        f"{row[0]}: "
        f"{row[1]} | "
        f"max_length={row[2]} | "
        f"nullable={row[3]}"
    )


# ============================================================
# REQUIRED DATABASE COLUMNS
# ============================================================

database_column_names = {
    row[0]
    for row in db_columns
}


required_database_columns = {
    "bank_id",
    "iso3_code",
    "swift_code",
    "bank_name",
    "bank_type",
    "bank_rank",
    "headquarters_city",
    "official_website",
    "founded_year",
    "is_active",
    "data_source",
}


missing_database_columns = (
    required_database_columns
    -
    database_column_names
)


if missing_database_columns:

    raise ValueError(
        "Required database columns are missing: "
        + str(
            sorted(missing_database_columns)
        )
    )


# ============================================================
# DATABASE BANK MASTER
# ============================================================

cursor.execute(
    """
    SELECT
        iso3_code,
        bank_name
    FROM banks;
    """
)


database_banks = cursor.fetchall()


database_bank_keys = {
    (
        str(row[0]).strip().upper(),
        str(row[1]).strip()
    )
    for row in database_banks
}


print("\n" + "=" * 70)
print("CURRENT DATABASE BANK MASTER")
print("=" * 70)

print(
    "Banks currently in database:",
    len(database_banks)
)


# ============================================================
# FIND BANKS MISSING FROM DATABASE
# ============================================================

missing_bank_rows = []


for index, row in banks.iterrows():

    key = (
        row["iso3_code"],
        row["bank_name"]
    )

    if key not in database_bank_keys:

        missing_bank_rows.append(
            (
                index,
                row
            )
        )


print("\n" + "=" * 70)
print("BANK MASTER SYNC CHECK")
print("=" * 70)

print(
    "Banks in CSV:",
    len(banks)
)

print(
    "Banks in database:",
    len(database_banks)
)

print(
    "Missing from database:",
    len(missing_bank_rows)
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


missing_country_references = []


for index, row in missing_bank_rows:

    if row["iso3_code"] not in country_codes:

        missing_country_references.append(
            (
                index + 2,
                row["iso3_code"],
                row["bank_name"]
            )
        )


print("\n" + "=" * 70)
print("COUNTRY REFERENCE CHECK")
print("=" * 70)

print(
    "Bank countries missing from countries table:",
    len(missing_country_references)
)


if missing_country_references:

    for item in missing_country_references:

        print(
            f"CSV row {item[0]} | "
            f"{item[1]} | "
            f"{item[2]}"
        )

    raise ValueError(
        "Cannot load banks because some ISO3 codes "
        "do not exist in countries table."
    )


# ============================================================
# DATABASE LENGTH CHECK
# ============================================================

print("\n" + "=" * 70)
print("DATABASE LENGTH CHECK")
print("=" * 70)


database_lengths = {
    row[0]: row[2]
    for row in db_columns
}


length_errors = []


for index, row in banks.iterrows():

    csv_row = index + 2

    for column in [
        "iso3_code",
        "swift_code",
        "bank_name",
        "bank_type",
        "headquarters_city",
        "data_source",
    ]:

        value = row[column]

        if value is None:
            continue

        max_length = database_lengths.get(
            column
        )

        if max_length is None:
            continue

        value_length = len(
            str(value)
        )

        if value_length > max_length:

            length_errors.append(
                {
                    "row": csv_row,
                    "column": column,
                    "value": value,
                    "length": value_length,
                    "max": max_length,
                }
            )


print(
    "Length violations:",
    len(length_errors)
)


if length_errors:

    for error in length_errors:

        print(
            f"Row {error['row']} | "
            f"{error['column']} | "
            f"Length={error['length']} | "
            f"Max={error['max']} | "
            f"Value={error['value']}"
        )

    raise ValueError(
        "Database length validation failed."
    )


# ============================================================
# INSERT QUERY
# ============================================================

INSERT_QUERY = """
INSERT INTO banks (
    iso3_code,
    swift_code,
    bank_name,
    bank_type,
    bank_rank,
    headquarters_city,
    official_website,
    founded_year,
    is_active,
    data_source
)
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
);
"""


# ============================================================
# INSERT MISSING BANKS
# ============================================================

print("\n" + "=" * 70)
print("INSERTING MISSING BANKS")
print("=" * 70)


inserted = 0


for index, row in missing_bank_rows:

    csv_row = index + 2


    # ========================================================
    # CONVERT VALUES TO NATIVE PYTHON TYPES
    # ========================================================

    # --------------------------------------------------------
    # ISO3
    # --------------------------------------------------------

    if pd.notna(row["iso3_code"]):

        iso3_code = str(
            row["iso3_code"]
        ).strip().upper()

    else:

        iso3_code = None


    # --------------------------------------------------------
    # SWIFT
    # --------------------------------------------------------

    if pd.notna(row["swift_code"]):

        swift_code = str(
            row["swift_code"]
        ).strip()

    else:

        swift_code = None


    # --------------------------------------------------------
    # BANK NAME
    # --------------------------------------------------------

    if pd.notna(row["bank_name"]):

        bank_name = str(
            row["bank_name"]
        ).strip()

    else:

        bank_name = None


    # --------------------------------------------------------
    # BANK TYPE
    # --------------------------------------------------------

    if pd.notna(row["bank_type"]):

        bank_type = str(
            row["bank_type"]
        ).strip()

    else:

        bank_type = None


    # --------------------------------------------------------
    # BANK RANK
    #
    # FIX:
    # Never call int() directly on NaN.
    # --------------------------------------------------------

    bank_rank = None

    if pd.notna(row["bank_rank"]):

        bank_rank = int(
            row["bank_rank"]
        )


    # --------------------------------------------------------
    # HEADQUARTERS
    # --------------------------------------------------------

    if pd.notna(row["headquarters_city"]):

        headquarters_city = str(
            row["headquarters_city"]
        ).strip()

    else:

        headquarters_city = None


    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    if pd.notna(row["official_website"]):

        official_website = str(
            row["official_website"]
        ).strip()

    else:

        official_website = None


    # --------------------------------------------------------
    # FOUNDED YEAR
    #
    # FIX:
    # Never call int() directly on NaN.
    # --------------------------------------------------------

    founded_year = None

    if pd.notna(row["founded_year"]):

        founded_year = int(
            row["founded_year"]
        )


    # --------------------------------------------------------
    # ACTIVE
    # --------------------------------------------------------

    if pd.notna(row["is_active"]):

        is_active = bool(
            row["is_active"]
        )

    else:

        is_active = None


    # --------------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------------

    if pd.notna(row["data_source"]):

        data_source = str(
            row["data_source"]
        ).strip()

    else:

        data_source = None


    # ========================================================
    # FINAL INTEGER RANGE CHECK
    # ========================================================

    if bank_rank is not None:

        if not (
            -2147483648
            <= bank_rank
            <= 2147483647
        ):

            raise ValueError(
                f"bank_rank outside PostgreSQL "
                f"INTEGER range at CSV row "
                f"{csv_row}: {bank_rank}"
            )


    if founded_year is not None:

        if not (
            -2147483648
            <= founded_year
            <= 2147483647
        ):

            raise ValueError(
                f"founded_year outside PostgreSQL "
                f"INTEGER range at CSV row "
                f"{csv_row}: {founded_year}"
            )


    # ========================================================
    # INSERT
    # ========================================================

    try:

        cursor.execute(
            INSERT_QUERY,
            (
                iso3_code,
                swift_code,
                bank_name,
                bank_type,
                bank_rank,
                headquarters_city,
                official_website,
                founded_year,
                is_active,
                data_source,
            )
        )


        inserted += 1


    except Exception as error:

        print("\n" + "=" * 70)
        print("BANK INSERT FAILED")
        print("=" * 70)

        print(
            "CSV row:",
            csv_row
        )

        print(
            "ISO3:",
            repr(iso3_code)
        )

        print(
            "Bank:",
            repr(bank_name)
        )

        print(
            "Bank type:",
            repr(bank_type)
        )

        print(
            "Bank rank:",
            repr(bank_rank)
        )

        print(
            "Founded year:",
            repr(founded_year)
        )

        print(
            "Headquarters:",
            repr(headquarters_city)
        )

        print(
            "Website:",
            repr(official_website)
        )

        print(
            "SWIFT:",
            repr(swift_code)
        )

        print(
            "Active:",
            repr(is_active)
        )

        print(
            "Data source:",
            repr(data_source)
        )

        print(
            "PostgreSQL error:",
            error
        )

        print(
            "SQLSTATE:",
            getattr(
                error,
                "pgcode",
                None
            )
        )


        diagnostics = getattr(
            error,
            "diag",
            None
        )


        if diagnostics:

            print(
                "Message:",
                diagnostics.message_primary
            )

            print(
                "Detail:",
                diagnostics.message_detail
            )

            print(
                "Hint:",
                diagnostics.message_hint
            )

            print(
                "Column:",
                diagnostics.column_name
            )

            print(
                "Constraint:",
                diagnostics.constraint_name
            )

            print(
                "Datatype:",
                diagnostics.datatype_name
            )


        # Roll back failed transaction
        conn.rollback()

        raise


# ============================================================
# COMMIT
# ============================================================

conn.commit()


# ============================================================
# FINAL DATABASE COUNT
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM banks;
    """
)


final_count = cursor.fetchone()[0]


# ============================================================
# FINAL NULL KEY CHECK
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM banks
    WHERE iso3_code IS NULL
       OR bank_name IS NULL;
    """
)


null_key_rows = cursor.fetchone()[0]


# ============================================================
# FINAL ISO3 CHECK
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM banks
    WHERE LENGTH(iso3_code) != 3;
    """
)


invalid_iso3_database = (
    cursor.fetchone()[0]
)


# ============================================================
# FINAL SWIFT COUNT
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM banks
    WHERE swift_code IS NOT NULL;
    """
)


swift_count = cursor.fetchone()[0]


# ============================================================
# FINAL BANK MASTER MATCH
# ============================================================

cursor.execute(
    """
    SELECT
        iso3_code,
        bank_name
    FROM banks;
    """
)


final_database_banks = {
    (
        str(row[0]).strip().upper(),
        str(row[1]).strip()
    )
    for row in cursor.fetchall()
}


csv_bank_keys = {
    (
        str(row["iso3_code"]).strip().upper(),
        str(row["bank_name"]).strip()
    )
    for _, row in banks.iterrows()
}


remaining_missing = (
    csv_bank_keys
    -
    final_database_banks
)


# ============================================================
# CLOSE DATABASE
# ============================================================

cursor.close()

conn.close()


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("BANK MASTER LOAD COMPLETE")
print("=" * 70)

print(
    "CSV rows:",
    len(banks)
)

print(
    "Banks originally in database:",
    len(database_banks)
)

print(
    "Missing banks before load:",
    len(missing_bank_rows)
)

print(
    "Banks inserted:",
    inserted
)

print(
    "Banks currently in database:",
    final_count
)

print(
    "Invalid ISO3 codes in database:",
    invalid_iso3_database
)

print(
    "NULL key rows:",
    null_key_rows
)

print(
    "Banks with SWIFT codes:",
    swift_count
)

print(
    "Banks still missing:",
    len(remaining_missing)
)

print(
    "Database:",
    DB_CONFIG["database"]
)


# ============================================================
# FINAL SAFETY CHECKS
# ============================================================

if remaining_missing:

    print(
        "\nRemaining missing banks:"
    )

    for bank in sorted(
        remaining_missing
    ):

        print(
            bank
        )

    raise ValueError(
        "Some CSV banks are still missing "
        "from the database."
    )


if null_key_rows != 0:

    raise ValueError(
        "NULL key values exist in banks table."
    )


if invalid_iso3_database != 0:

    raise ValueError(
        "Invalid ISO3 codes exist in banks table."
    )


# ============================================================
# SUCCESS
# ============================================================

print("\n" + "=" * 70)
print("FINAL STATUS: SUCCESS")
print("=" * 70)

print(
    "Banks.csv and PostgreSQL banks table "
    "are synchronized."
)

print(
    "Total bank records:",
    final_count
)

print(
    "New banks inserted:",
    inserted
)

print(
    "Banks still missing:",
    len(remaining_missing)
)

print("=" * 70)
print("DONE")
print("=" * 70)
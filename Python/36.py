import pandas as pd
from pathlib import Path
import shutil


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 36 — FINALIZE USD FINANCIAL DATASET
# ============================================================

INPUT_FILE = Path(
    "Data/Raw/Banks/Mains/bank_financials_synthetic_usd.csv"
)

BACKUP_FILE = Path(
    "Data/Raw/Banks/Mains/bank_financials_synthetic_usd_before_metadata_fix.csv"
)


# ============================================================
# STANDARD COLUMN STRUCTURE
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


# ============================================================
# POSSIBLE USD COLUMN NAMES
# ============================================================

USD_COLUMN_RENAME_MAP = {
    "total_assets_usd": "total_assets",
    "total_deposits_usd": "total_deposits",
    "total_loans_usd": "total_loans",
    "shareholders_equity_usd": "shareholders_equity",
    "operating_income_usd": "operating_income",
    "net_income_usd": "net_income",
}


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("GLOBAL BANKING INTELLIGENCE")
print("36 — FINALIZE USD FINANCIAL DATASET")
print("=" * 70)

print()
print("Input file:")
print(INPUT_FILE)


# ============================================================
# FILE CHECK
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    keep_default_na=True,
)

original_row_count = len(df)

print()
print("=" * 70)
print("SOURCE FILE")
print("=" * 70)

print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# BACKUP
# ============================================================

print()
print("=" * 70)
print("BACKUP")
print("=" * 70)

if not BACKUP_FILE.exists():

    shutil.copy2(
        INPUT_FILE,
        BACKUP_FILE,
    )

    print("Backup created:")
    print(BACKUP_FILE)

else:

    print("Backup already exists:")
    print(BACKUP_FILE)


# ============================================================
# RENAME USD MONETARY COLUMNS IF NECESSARY
# ============================================================

print()
print("=" * 70)
print("USD COLUMN NORMALIZATION")
print("=" * 70)

for old_name, new_name in USD_COLUMN_RENAME_MAP.items():

    if old_name in df.columns:

        if new_name in df.columns:

            raise ValueError(
                f"Column collision detected: "
                f"'{old_name}' and '{new_name}' both exist."
            )

        df.rename(
            columns={
                old_name: new_name
            },
            inplace=True,
        )

        print(
            f"{old_name} -> {new_name}"
        )


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
print("=" * 70)
print("COLUMN CHECK")
print("=" * 70)

print(
    "Expected columns:",
    len(EXPECTED_COLUMNS)
)

print(
    "Actual columns:",
    len(df.columns)
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

    print()
    print("Missing columns:")

    for column in missing_columns:
        print(" ", column)

    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

if extra_columns:

    print()
    print("Extra columns:")

    for column in extra_columns:
        print(" ", column)

    raise ValueError(
        f"Unexpected columns: {extra_columns}"
    )


# ============================================================
# STANDARD COLUMN ORDER
# ============================================================

df = df[EXPECTED_COLUMNS].copy()


# ============================================================
# KEY CHECKS
# ============================================================

print()
print("=" * 70)
print("KEY CHECK")
print("=" * 70)

blank_iso3 = (
    df["iso3_code"].isna()
    |
    (
        df["iso3_code"]
        .astype(str)
        .str.strip()
        == ""
    )
).sum()

blank_bank_names = (
    df["bank_name"].isna()
    |
    (
        df["bank_name"]
        .astype(str)
        .str.strip()
        == ""
    )
).sum()

invalid_iso3 = (
    df["iso3_code"].notna()
    &
    (
        df["iso3_code"]
        .astype(str)
        .str.strip()
        .str.len()
        != 3
    )
).sum()

print("Blank ISO3:", blank_iso3)
print("Invalid ISO3 length:", invalid_iso3)
print("Blank bank names:", blank_bank_names)

if blank_iso3 > 0:
    raise ValueError(
        "Blank ISO3 values detected."
    )

if invalid_iso3 > 0:
    raise ValueError(
        "Invalid ISO3 values detected."
    )

if blank_bank_names > 0:
    raise ValueError(
        "Blank bank names detected."
    )


# ============================================================
# FISCAL YEAR CHECK
# ============================================================

print()
print("=" * 70)
print("FISCAL YEAR CHECK")
print("=" * 70)

years = pd.to_numeric(
    df["fiscal_year"],
    errors="coerce",
)

invalid_years = (
    years.isna()
    |
    ~years.between(2020, 2025)
).sum()

print(
    "Invalid fiscal years:",
    invalid_years
)

if invalid_years > 0:

    raise ValueError(
        "Invalid fiscal years detected."
    )


# ============================================================
# DUPLICATE CHECK
# ============================================================

print()
print("=" * 70)
print("BANK / YEAR DUPLICATE CHECK")
print("=" * 70)

duplicates = df.duplicated(
    subset=[
        "iso3_code",
        "bank_name",
        "fiscal_year",
    ],
    keep=False,
)

duplicate_rows = duplicates.sum()

print(
    "Duplicate rows:",
    duplicate_rows
)

if duplicate_rows > 0:

    raise ValueError(
        "Duplicate bank/year records detected."
    )


# ============================================================
# FINALIZE USD CURRENCY
# ============================================================

print()
print("=" * 70)
print("USD DATASET CURRENCY")
print("=" * 70)

print(
    "Original reporting_currency values detected:",
    df["reporting_currency"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
    .nunique()
)

print(
    "Setting reporting_currency = USD"
)

df["reporting_currency"] = "USD"


# ============================================================
# VERIFY USD CURRENCY
# ============================================================

currency_values = (
    df["reporting_currency"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
    .unique()
)

print(
    "Final reporting currency:",
    list(currency_values)
)

if len(currency_values) != 1:
    raise ValueError(
        "USD currency normalization failed."
    )

if currency_values[0] != "USD":
    raise ValueError(
        "Final reporting currency is not USD."
    )


# ============================================================
# ROW COUNT CHECK
# ============================================================

if len(df) != original_row_count:

    raise ValueError(
        "Row count changed unexpectedly."
    )


# ============================================================
# FINAL NULL / NAN CHECK
# ============================================================

print()
print("=" * 70)
print("FINAL DATA CHECK")
print("=" * 70)

nan_count = int(
    df.isna().sum().sum()
)

print(
    "Remaining pandas NaN values:",
    nan_count
)

# NaN is allowed in non-key financial fields.
# We only ensure no NaN exists in key fields.

key_nan_count = int(
    df[
        [
            "iso3_code",
            "bank_name",
            "fiscal_year",
        ]
    ]
    .isna()
    .sum()
    .sum()
)

print(
    "Key-field NaN values:",
    key_nan_count
)

if key_nan_count > 0:

    raise ValueError(
        "Key fields contain missing values."
    )


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    INPUT_FILE,
    index=False,
)

print()
print("=" * 70)
print("FILE SAVED")
print("=" * 70)

print(
    "Saved:",
    INPUT_FILE
)

print(
    "Rows:",
    len(df)
)

print(
    "Columns:",
    len(df.columns)
)


# ============================================================
# FINAL COLUMN LIST
# ============================================================

print()
print("=" * 70)
print("FINAL COLUMNS")
print("=" * 70)

for number, column in enumerate(
    df.columns,
    start=1,
):

    print(
        f"{number:02d}. {column}"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print()
print("=" * 70)
print("STATUS: PASS")
print("=" * 70)

print()
print(
    "USD-normalized monetary values are preserved."
)

print(
    "Standard financial column names are in place."
)

print(
    "reporting_currency is now USD for every record."
)

print()
print("# DONE")
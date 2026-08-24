import pandas as pd
import random

# ============================================================
# FILE PATHS
# ============================================================

INPUT = "Data/Raw/Banks/world_bank_data_2020_2025_cleaned.csv"
OUTPUT = "Data/Raw/Banks/world_bank_data_2020_2025_synthetic.csv"

PENDING = "Pending Public Data"


# ============================================================
# LOAD CSV
# ============================================================

def load_csv(path):

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1"
    ]:

        try:

            df = pd.read_csv(
                path,
                encoding=encoding,
                dtype=str,
                low_memory=False,
                keep_default_na=False
            )

            df.columns = df.columns.str.strip()

            print(f"Loaded: {path}")
            print(f"Encoding: {encoding}")

            return df

        except Exception:
            pass

    raise Exception(f"Could not load CSV: {path}")


df = load_csv(INPUT)


# ============================================================
# WORLD BANK NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Inflation (CPI %)",
    "GDP (Current USD)",
    "GDP per Capita (Current USD)",
    "Unemployment Rate (%)",
    "Interest Rate (Real, %)",
    "Inflation (GDP Deflator, %)",
    "GDP Growth (% Annual)",
    "Current Account Balance (% GDP)",
    "Government Expense (% of GDP)",
    "Government Revenue (% of GDP)",
    "Tax Revenue (% of GDP)",
    "Gross National Income (USD)"
]


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "iso3_code",
    "country_name",
    "year"
] + numeric_columns

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:

    raise Exception(
        "Missing columns:\n"
        + "\n".join(missing_columns)
    )


# ============================================================
# CLEAN ISO3
# ============================================================

df["iso3_code"] = (
    df["iso3_code"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# CLEAN YEAR
# ============================================================

df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce"
)


# ============================================================
# CONVERT ALL MISSING MARKERS TO NaN
# ============================================================

missing_markers = [
    "",
    "pending public data",
    "Pending Public Data",
    "PENDING PUBLIC DATA",
    "NA",
    "N/A",
    "NULL",
    "null",
    "NaN",
    "nan"
]

pending_found = 0

for col in numeric_columns:

    values = (
        df[col]
        .astype(str)
        .str.strip()
    )

    pending_found += (
        values.str.lower()
        .eq("pending public data")
        .sum()
    )

    df[col] = values.replace(
        missing_markers,
        pd.NA
    )


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# ============================================================
# COUNT MISSING BEFORE
# ============================================================

missing_before = df[
    numeric_columns
].isna().sum()


# ============================================================
# SYNTHETIC GENERATION
# ============================================================

filled = 0

filled_by_column = {
    col: 0
    for col in numeric_columns
}


# ============================================================
# PASS 1
# COUNTRY-SPECIFIC GENERATION
# ============================================================

for iso3 in df["iso3_code"].unique():

    country_mask = (
        df["iso3_code"] == iso3
    )

    for col in numeric_columns:

        known = df.loc[
            country_mask,
            col
        ].dropna()

        # ----------------------------------------------------
        # COUNTRY HAS KNOWN VALUES
        # ----------------------------------------------------

        if len(known) > 0:

            low = known.min()
            high = known.max()

            missing_indexes = df.loc[
                country_mask &
                df[col].isna()
            ].index

            for idx in missing_indexes:

                if low == high:

                    synthetic = low

                else:

                    synthetic = random.uniform(
                        low,
                        high
                    )

                df.at[idx, col] = round(
                    synthetic,
                    2
                )

                filled += 1
                filled_by_column[col] += 1


# ============================================================
# PASS 2
# GLOBAL FALLBACK
#
# If an entire country has NO value for an indicator,
# use the overall dataset range for that indicator.
# ============================================================

global_fallback_filled = 0

for col in numeric_columns:

    global_known = df[col].dropna()

    # No values anywhere in the dataset
    if len(global_known) == 0:
        continue

    global_low = global_known.min()
    global_high = global_known.max()

    missing_indexes = df.index[
        df[col].isna()
    ]

    for idx in missing_indexes:

        if global_low == global_high:

            synthetic = global_low

        else:

            synthetic = random.uniform(
                global_low,
                global_high
            )

        df.at[idx, col] = round(
            synthetic,
            2
        )

        filled += 1
        filled_by_column[col] += 1
        global_fallback_filled += 1


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# REMAINING MISSING VALUES
# ============================================================

remaining_missing = df[
    numeric_columns
].isna().sum()


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("WORLD BANK SYNTHETIC DATA GENERATION COMPLETE")
print("=" * 70)

print("Rows:", len(df))

print(
    "Pending Public Data markers found:",
    pending_found
)

print(
    "Missing values before:",
    int(missing_before.sum())
)

print(
    "Synthetic values generated:",
    filled
)

print(
    "Country-specific values generated:",
    filled - global_fallback_filled
)

print(
    "Global fallback values generated:",
    global_fallback_filled
)


# ============================================================
# COLUMN SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SYNTHETIC VALUES GENERATED BY COLUMN")
print("=" * 70)

for col in numeric_columns:

    print(
        f"{col}: {filled_by_column[col]}"
    )


# ============================================================
# REMAINING MISSING
# ============================================================

print("\n" + "=" * 70)
print("REMAINING MISSING VALUES")
print("=" * 70)

print(
    remaining_missing.to_string()
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("SAVED")
print("=" * 70)

print(OUTPUT)
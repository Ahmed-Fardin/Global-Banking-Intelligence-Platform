import pandas as pd

input_file = "Data/Raw/Banks/bank_financials.csv"
output_file = "Data/Raw/Banks/bank_financials.csv"

df = pd.read_csv(
    input_file,
    encoding="utf-8-sig",
    dtype=str,
    low_memory=False
)

df.columns = df.columns.str.strip()

# ============================================================
# FIX INCORRECT ISO3 CODES
# ============================================================

code_fixes = {
    "GERMANY": "DEU",
    "GRENADA": "GRD",
    "GUYANA": "GUY",
    "ICELAND": "ISL",
    "LIE": "LIE"
}

df["iso3_code"] = df["iso3_code"].replace(code_fixes)

# ============================================================
# REMOVE REGIONAL BANK RECORDS
# ============================================================

before = len(df)

df = df[
    df["iso3_code"] != "XAF"
].copy()

removed = before - len(df)

# ============================================================
# SAVE
# ============================================================

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("BANK FINANCIALS ISO3 FIX COMPLETE")
print("=" * 60)

print("XAF records removed:", removed)

print("\nRemaining problematic codes:")
print(
    df[
        df["iso3_code"].isin([
            "GERMANY",
            "GRENADA",
            "GUYANA",
            "ICELAND",
            "LIE",
            "XAF"
        ])
    ][["iso3_code", "bank_name"]]
)

print("\nSaved:", output_file)
import pandas as pd

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv("Data/Raw/Banks/bank_financials.csv")

print("=" * 70)
print("BANK-YEAR DUPLICATE ANALYSIS")
print("=" * 70)

# ------------------------------------------
# Find duplicate bank + year combinations
# ------------------------------------------

duplicates = df[
    df.duplicated(
        subset=["iso3_code", "bank_name", "fiscal_year"],
        keep=False
    )
].copy()

print(f"\nRows involved: {len(duplicates):,}")

# ------------------------------------------
# Group by bank/year
# ------------------------------------------

groups = duplicates.groupby(
    ["iso3_code", "bank_name", "fiscal_year"]
)

summary = []

for (iso, bank, year), group in groups:

    rows = len(group)

    unique_rows = len(group.drop_duplicates())

    summary.append({
        "iso3_code": iso,
        "bank_name": bank,
        "fiscal_year": year,
        "rows": rows,
        "unique_rows": unique_rows
    })

summary = pd.DataFrame(summary)

summary = summary.sort_values(
    ["rows", "bank_name"],
    ascending=[False, True]
)

summary.to_csv(
    "BankYear_Duplicate_Summary.csv",
    index=False
)

print("\nSaved: BankYear_Duplicate_Summary.csv")

# ------------------------------------------
# Statistics
# ------------------------------------------

print("\nSUMMARY")

print("-" * 70)

print(f"Duplicate bank-years : {len(summary):,}")

print()

print(summary["rows"].value_counts().sort_index())

print()

print("=" * 70)
print("DONE")
print("=" * 70)
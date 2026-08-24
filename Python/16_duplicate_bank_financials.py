import pandas as pd

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv("Data/Raw/Banks/bank_financials.csv")

print("=" * 60)
print("BANK FINANCIALS DUPLICATE ANALYSIS")
print("=" * 60)

print(f"\nTotal rows: {len(df):,}")

# ==========================================
# EXACT DUPLICATES
# ==========================================

exact_duplicates = df[df.duplicated(keep=False)]

print(f"\nExact duplicate rows: {len(exact_duplicates):,}")

exact_duplicates.sort_values(
    by=["bank_name", "fiscal_year"],
    inplace=True
)

exact_duplicates.to_csv(
    "Exact_Duplicates.csv",
    index=False
)

print("Saved: Exact_Duplicates.csv")

# ==========================================
# BANK + YEAR DUPLICATES
# ==========================================

bank_year_duplicates = df[
    df.duplicated(
        subset=["iso3_code", "bank_name", "fiscal_year"],
        keep=False
    )
]

bank_year_duplicates = bank_year_duplicates.sort_values(
    by=["iso3_code", "bank_name", "fiscal_year"]
)

bank_year_duplicates.to_csv(
    "BankYear_Duplicates.csv",
    index=False
)

print(f"Bank-Year duplicate rows: {len(bank_year_duplicates):,}")

print("Saved: BankYear_Duplicates.csv")

# ==========================================
# CLEAN DATASET
# ==========================================

clean_df = df.drop_duplicates()

removed = len(df) - len(clean_df)

print(f"\nRows that would be removed: {removed:,}")

clean_df.to_csv(
    "Data/Raw/Banks/Clean_bank_financials.csv",
    index=False
)

print("Saved: Clean_bank_financials.csv")

print("\nDONE")
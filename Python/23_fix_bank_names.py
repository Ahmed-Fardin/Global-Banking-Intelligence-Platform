import pandas as pd

# =====================================================
# SAFE CSV LOADER
# =====================================================

def load_csv(path):
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    for enc in encodings:
        try:
            print(f"Trying {enc}...")
            df = pd.read_csv(path, encoding=enc)
            print(f"Loaded using {enc}\n")
            return df
        except:
            continue

    raise Exception(f"Could not load {path}")

# =====================================================
# LOAD DATA
# =====================================================

df = load_csv("Data/Processed/bank_financials_names_fixed.csv")
df.columns = df.columns.str.strip()

# =====================================================
# FINANCIAL COLUMNS
# =====================================================

financial_columns = [
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income"
]

# =====================================================
# CLEAN NUMBERS
# =====================================================

for col in financial_columns:

    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df[col] = pd.to_numeric(df[col], errors="coerce")

# =====================================================
# AUDIT
# =====================================================

issues = []

for _, row in df.iterrows():

    bank = row["bank_name"]
    year = row["fiscal_year"]

    assets = row["total_assets"]
    deposits = row["total_deposits"]
    loans = row["total_loans"]
    equity = row["shareholders_equity"]
    income = row["operating_income"]
    profit = row["net_income"]

    if pd.notna(assets) and pd.notna(loans):

        if loans > assets:
            issues.append({
                "bank": bank,
                "year": year,
                "issue": "Loans > Assets",
                "assets": assets,
                "loans": loans
            })

    if pd.notna(assets) and pd.notna(deposits):

        if deposits > assets:
            issues.append({
                "bank": bank,
                "year": year,
                "issue": "Deposits > Assets",
                "assets": assets,
                "deposits": deposits
            })

    if pd.notna(assets) and pd.notna(equity):

        if equity > assets:
            issues.append({
                "bank": bank,
                "year": year,
                "issue": "Equity > Assets",
                "assets": assets,
                "equity": equity
            })

    if pd.notna(income) and pd.notna(profit):

        if profit > income:
            issues.append({
                "bank": bank,
                "year": year,
                "issue": "Net Income > Operating Income",
                "operating_income": income,
                "net_income": profit
            })

# =====================================================
# SAVE
# =====================================================

issues = pd.DataFrame(issues)

issues.to_csv(
    "Data/Processed/Financial_Logic_Audit_Report.csv",
    index=False,
    encoding="utf-8-sig"
)

print("="*60)
print("FINANCIAL LOGIC AUDIT COMPLETE")
print("="*60)

if len(issues) == 0:
    print("✅ No financial logic issues found.")
else:
    print(issues)

    issues.to_csv(
        "Data/Processed/Financial_Logic_Audit_Report.csv",
        index=False,
        encoding="utf-8-sig"
    )
    print()
    print("Total Issues:", len(issues))
import pandas as pd
import random

# =====================================================
# LOAD
# =====================================================

def load_csv(path):
    for enc in ["utf-8-sig", "utf-8", "cp1252", "latin1"]:
        try:
            df = pd.read_csv(
                path,
                encoding=enc,
                low_memory=False,
                keep_default_na=False,
                dtype=str
            )
            print(f"Loaded with {enc}")
            return df
        except:
            pass

    raise Exception("Could not load CSV")

df = load_csv("Data/Raw/Banks/bank_financials.csv")

df.columns = df.columns.str.strip()

financial_columns = [
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
    "branches"
]

filled = 0

# =====================================================
# FILL SYNTHETIC VALUES
# =====================================================

for bank in df["bank_name"].unique():

    bank_mask = df["bank_name"] == bank

    for col in financial_columns:

        numeric = pd.to_numeric(df.loc[bank_mask, col], errors="coerce")

        known = numeric.dropna()

        if len(known) == 0:
            continue

        low = known.min()
        high = known.max()

        for idx in df.loc[bank_mask].index:

            current = str(df.at[idx, col]).strip()

            if current.lower() == "pending public data":

                if low == high:
                    synthetic = low
                else:
                    synthetic = random.uniform(low, high)

                if col in [
                    "roe_percent",
                    "roa_percent",
                    "capital_adequacy_percent",
                    "cost_income_ratio",
                    "loan_to_deposit_ratio",
                    "npl_ratio"
                ]:
                    value = f"{synthetic:.2f}"
                else:
                    value = str(int(round(synthetic)))

                df.at[idx, col] = value
                filled += 1

# =====================================================
# SAVE
# =====================================================

output = "Data/Raw/Banks/bank_financials_synthetic.csv"

df.to_csv(
    output,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("DONE")
print("=" * 60)
print("Synthetic values generated:", filled)
print("Saved as:", output)
import pandas as pd
import re

# ===========================
# LOAD DATA
# ===========================

df = pd.read_csv(
    "Data/Raw/Banks/bank_financials.csv",
    encoding="cp1252"
)

financial_columns = [
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income"
]

results = []

for col in financial_columns:

    for idx, value in df[col].items():

        value = str(value).strip()

        issue = None

        if value.lower() in ["nan", "", "n/a", "null"]:
            issue = "Blank"

        elif value.endswith(("B","b")):
            issue = "Billion"

        elif value.endswith(("M","m")):
            issue = "Million"

        elif value.endswith(("T","t")):
            issue = "Trillion"

        elif value.endswith(("K","k")):
            issue = "Thousand"

        elif "," in value:
            issue = "Comma"

        else:

            try:

                num = float(value)

                # ONLY financial amounts
                if 0 < abs(num) < 100000:
                  issue = "Suspicious Small Number"

            except:
                issue = "Text"

        if issue:

            results.append({
                "bank": df.loc[idx,"bank_name"],
                "year": df.loc[idx,"fiscal_year"],
                "column": col,
                "value": value,
                "issue": issue
            })




audit = pd.DataFrame(results)

audit.to_csv(
    "Data/Raw/Banks/Financials_Audit.csv",
    index=False
)


small = audit[audit["issue"] == "Suspicious Small Number"]

print(small.head(100))

small.to_csv(
    "Data/Raw/Banks/Suspicious_Small_Numbers.csv",
    index=False
)            

print(audit["issue"].value_counts())
print()
print("Total:",len(audit))
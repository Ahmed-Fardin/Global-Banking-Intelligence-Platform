import pandas as pd

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

report = []

for bank in sorted(df["bank_name"].unique()):

    bank_df = df[df["bank_name"] == bank]

    values = []

    for col in financial_columns:

        for v in bank_df[col]:

            try:
                values.append(float(str(v).replace(",", "").replace("B","").replace("M","").replace("T","")))
            except:
                pass

    if len(values) == 0:
        continue

    report.append({
        "bank_name": bank,
        "minimum_value": min(values),
        "maximum_value": max(values)
    })

report = pd.DataFrame(report)

report.to_csv(
    "Data/Raw/Banks/Reporting_Scale_Report.csv",
    index=False
)

print("Done!")
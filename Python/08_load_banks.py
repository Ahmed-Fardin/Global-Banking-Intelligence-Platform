import pandas as pd

# Load Bangladesh banks CSV
df = pd.read_csv("Data/raw/banks/banks.csv")

print("=" * 50)
print("BANGLADESH BANKS")
print("=" * 50)

print(df)

print("\nTotal Banks:", len(df))

print("\nColumns:")
print(df.columns.tolist())
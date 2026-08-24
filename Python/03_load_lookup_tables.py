import pandas as pd
from config import get_connection

# ==========================================
# CONNECT TO DATABASE
# ==========================================

conn = get_connection()
cursor = conn.cursor()

# ==========================================
# LOAD REGIONS
# ==========================================

regions_df = pd.read_csv("Data/reference/regions.csv")

for _, row in regions_df.iterrows():

    cursor.execute(
        """
        INSERT INTO regions (region_name)
        VALUES (%s)
        ON CONFLICT (region_name) DO NOTHING;
        """,
        (row["region"],)
    )

conn.commit()

print("Regions loaded successfully.")

# ==========================================
# LOAD CURRENCIES
# ==========================================

currencies_df = pd.read_csv("Data/reference/currencies.csv")

for _, row in currencies_df.iterrows():

    cursor.execute(
        """
        INSERT INTO currencies
        (currency_name, currency_code, currency_symbol)

        VALUES (%s, %s, %s)

        ON CONFLICT (currency_code) DO NOTHING;
        """,
        (
            row["currency_name"],
            row["currency_code"],
            row["currency_symbol"]
        )
    )

conn.commit()

print("Currencies loaded successfully.")

cursor.close()
conn.close()
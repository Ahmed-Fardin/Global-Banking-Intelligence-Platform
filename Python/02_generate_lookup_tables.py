import pandas as pd

# ==========================================
# LOAD COUNTRIES DATA
# ==========================================

countries_df = pd.read_csv("Data/processed/countries.csv")

# ==========================================
# GENERATE REGIONS
# ==========================================

regions_df = (
    countries_df[["region"]]
    .drop_duplicates()
    .sort_values("region")
    .reset_index(drop=True)
)

regions_df.to_csv("Data/reference/regions.csv", index=False)

print("regions.csv created successfully.")

# ==========================================
# GENERATE CURRENCIES
# ==========================================

currencies_df = (
    countries_df[
        [
            "currency_name",
            "currency_code",
            "currency_symbol"
        ]
    ]
    .drop_duplicates()
    .sort_values("currency_code")
    .reset_index(drop=True)
)

currencies_df.to_csv("Data/reference/currencies.csv", index=False)



# ==========================================
# CREATE COUNTRIES DIMENSION
# ==========================================

countries_df = pd.read_csv("Data/processed/countries.csv")

regions_df = pd.read_csv("Data/reference/regions.csv")
currencies_df = pd.read_csv("Data/reference/currencies.csv")

# ==========================================
# CREATE REGION LOOKUP DICTIONARY
# ==========================================

region_lookup = dict(
    zip(
        regions_df["region"],
        regions_df.index + 1
    )
)

print(region_lookup)


print(countries_df.head())

print(regions_df.head())

print(currencies_df.head())


print("currencies.csv created successfully.")
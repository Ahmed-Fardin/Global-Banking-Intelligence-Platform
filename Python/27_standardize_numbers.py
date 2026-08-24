import pandas as pd
import numpy as np

# 1. Load your existing CSV file
input_file = 'data/Raw/Banks/world_bank_data_2020_2025_final.csv'
output_file = 'data/Raw/Banks/world_bank_data_2020_2025_completed.csv'

df = pd.read_csv(input_file)
print(f"Loaded {input_file} with {len(df)} rows.")

# 2. Clean population: convert valid numbers to float, leave "Pending Public Data" as NaN
df['pop_clean'] = pd.to_numeric(df['population'], errors='coerce')

# Fill missing values using GDP / GDP per capita relationship
calc_pop = df['GDP (Current USD)'] / df['GDP per Capita (Current USD)']
df['pop_clean'] = df['pop_clean'].fillna(calc_pop)

# Interpolate and fill any remaining gaps per country
df['pop_clean'] = df.groupby('country_name')['pop_clean'].transform(
    lambda group: group.interpolate(method='linear').bfill().ffill()
)

# Update the population column and format as integers
df['population'] = df['pop_clean'].round().astype('Int64')
df = df.drop(columns=['pop_clean'])

# 3. Save the completed dataset
df.to_csv(output_file, index=False)
print(f"Completed dataset successfully saved to {output_file}")
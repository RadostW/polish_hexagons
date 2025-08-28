import pandas as pd

# Load the CSV file
file_path = 'election_data.csv'  # Update this with your actual file path
df = pd.read_csv(file_path, sep=';', encoding='utf-8')

# Convert numeric columns to actual numbers (errors='coerce' will turn bad data into NaN)
numeric_cols = df.columns[7:]  # all columns after the first 7 are numeric in your sample
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Group by "Teryt Powiatu" and aggregate numeric data by summing
aggregated = df.groupby("Teryt Powiatu")[numeric_cols].sum().reset_index()

# Optionally, save to a new file
aggregated.to_csv('aggregated_by_teryt_powiatu.csv', sep=';', index=False)

# Display the aggregated DataFrame
print(aggregated)


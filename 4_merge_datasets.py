import pandas as pd

# Load first CSV (powiaty data)
powiaty_df = pd.read_csv("powiaty_tiles_assigned.csv")

# Load second CSV (midpoints data), rename the column to match for merging
midpoints_df = pd.read_csv("powiaty_midpoints.csv")

# Merge data on the "name" column (left join to keep all powiaty entries)
merged_df = powiaty_df.merge(midpoints_df, on="teryt", how="left")

dups = merged_df[merged_df["teryt"].duplicated(keep=False)]
suspicious = ((dups["JPT_POWIER"]/100 - dups["area"])**2 > (50*50))
suspicious_df = dups[suspicious]

# Drop the suspicious rows using their index
merged_df = merged_df.drop(suspicious_df.index)

# Save the result to a new CSV file
merged_df.to_csv("powiaty_tiles_and_midpoints.csv", index=False)

print("CSV files merged successfully and saved as merged_powiaty.csv")

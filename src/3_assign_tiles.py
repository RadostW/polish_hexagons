import pandas as pd
import numpy as np

# Load the CSV file
filename = "powiaty_population.csv"
df = pd.read_csv(filename)

# Compute the tile_fraction
DF_TILE_SIZE = 50_000
df["tile_fraction"] = df["population"] / DF_TILE_SIZE

# Compute initial tile allocation (integer part)
df["tiles"] = df["tile_fraction"].astype(int)

# Compute the remainder
remainders = df["tile_fraction"] - df["tiles"]

# Determine the number of extra tiles to allocate
total_tiles = df["tiles"].sum()
extra_tiles_needed = int(round(df["tile_fraction"].sum() - total_tiles))

# Assign extra tiles based on the largest remainders
df["remainder"] = remainders
sorted_df = df.sort_values(by="remainder", ascending=False)
for i in range(extra_tiles_needed):
    sorted_df.iloc[i, sorted_df.columns.get_loc("tiles")] += 1

df = sorted_df.drop(columns=["remainder"]).sort_index()

# Convert tiles column to a list
df["tiles"] = df["tiles"].astype(int).tolist()
df["tiles"] = df["tiles"].clip(lower=1)

# Save the result to a CSV file
df.to_csv("powiaty_tiles_assigned.csv", index=False)

print(df)

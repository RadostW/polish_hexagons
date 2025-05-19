import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations

# Load the CSV files
hexagon_df = pd.read_csv("optimized_assigned_hexagons.csv")
election_df = pd.read_csv("presidential_election/election.csv", sep=";")

# Load the shapefile for powiaty
powiaty = gpd.read_file("powiaty/powiaty.shp")

# Normalize TERYT codes for matching
election_df["Kod TERYT"] = election_df["Kod TERYT"].astype(str).str.zfill(6).str[:4]
hexagon_df["teryt"] = hexagon_df["teryt"].astype(str).str.zfill(4)

# Merge datasets on TERYT codes
merged_df = election_df.merge(hexagon_df, left_on="Kod TERYT", right_on="teryt", how="inner")

# Create the plot with 2 subplots (side by side)
fig, axs = plt.subplots(1, 2, figsize=(20, 10), sharey=True)

#
# LEFT PLOT
#

# Define hexagon parameters
hex_size = 11000
hex_width = np.sqrt(3) * hex_size
hex_height = 2 * hex_size


# Function to draw hexagon
def draw_hexagon(x, y, color):
    angles = np.linspace(0, 2 * np.pi, 7)
    x_hex = x + hex_size * np.cos(angles)
    y_hex = y + hex_size * np.sin(angles)
    axs[0].fill(
        x_hex,
        y_hex,
        color,  
        # edgecolor="black",
        zorder=50,
    )


TRZASKOWSKI_color = "#F28E2B"
DUDA_color = "#4E79A7"

# Group data by powiat
for _, row in merged_df.iterrows():
    winner = (
        TRZASKOWSKI_color
        if row["Rafał Kazimierz TRZASKOWSKI"] > row["Andrzej Sebastian DUDA"]
        else DUDA_color
    )
    draw_hexagon(row["hexagon_easting"], row["hexagon_northing"], winner)

# Connect close hexagons only within the same TERYT code
for teryt_code, group in merged_df.groupby("Kod TERYT"):
    # Determine winner for each TERYT group
    winner = (
        TRZASKOWSKI_color
        if group["Rafał Kazimierz TRZASKOWSKI"].sum()
        > group["Andrzej Sebastian DUDA"].sum()
        else DUDA_color
    )

    hex_coords = group[["hexagon_easting", "hexagon_northing"]].values

    # Check distances between hexagons and connect if close enough
    for (x1, y1), (x2, y2) in combinations(hex_coords, 2):
        if np.linalg.norm([x2 - x1, y2 - y1]) < 30000:
            axs[0].plot([x1, x2], [y1, y2], winner, linewidth=5, zorder=10)


axs[0].axis("equal")

#
# RIGHT PLOT
#

# Plot powiaty on the second subplot (right side)
powiaty["winner"] = powiaty["JPT_KOD_JE"].apply(
    lambda x: TRZASKOWSKI_color if election_df[election_df["Kod TERYT"] == str(x).zfill(4)]["Rafał Kazimierz TRZASKOWSKI"].sum() >
              election_df[election_df["Kod TERYT"] == str(x).zfill(4)]["Andrzej Sebastian DUDA"].sum() else DUDA_color
)

# Plot the powiaty geometries with color coding
powiaty.plot(ax=axs[1], color=powiaty["winner"], edgecolor="white", linewidth=1)

axs[1].axis("equal")

axs[0].axis('off')
axs[1].axis('off')

plt.tight_layout()
plt.show()


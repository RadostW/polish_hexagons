import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations

# Constants for hexagon geometry
HEX_SIZE = 11000
HEX_WIDTH = np.sqrt(3) * HEX_SIZE
HEX_HEIGHT = 2 * HEX_SIZE

# Function to draw a single hexagon
def draw_hexagon(ax, x, y, color):
    angles = np.linspace(0, 2 * np.pi, 7)
    x_hex = x + HEX_SIZE * np.cos(angles)
    y_hex = y + HEX_SIZE * np.sin(angles)
    ax.fill(x_hex, y_hex, color, zorder=50)

def make_graph(teryt_color_df):
    # Load input data
    hexagon_df = pd.read_csv("optimized_assigned_hexagons.csv")
    # election_df = pd.read_csv("presidential_election/election.csv", sep=";")
    powiaty = gpd.read_file("powiaty/powiaty.shp")

    # Normalize TERYT codes
    # election_df["Kod TERYT"] = election_df["Kod TERYT"].astype(str).str.zfill(6).str[:4]
    hexagon_df["teryt"] = hexagon_df["teryt"].astype(str).str.zfill(4)

    # Merge with color mapping
    hexagon_colored = hexagon_df.merge(teryt_color_df, on="teryt", how="left")    
    # merged_df = election_df.merge(hexagon_colored, left_on="Kod TERYT", right_on="teryt", how="inner")
    merged_df = hexagon_colored

    # Set up figure
    fig, axs = plt.subplots(1, 2, figsize=(20, 10), sharey=True)

    # --- LEFT PLOT: Hexagons ---
    for _, row in merged_df.iterrows():
        if not pd.isna(row["color"]):
            draw_hexagon(axs[0], row["hexagon_easting"], row["hexagon_northing"], row["color"])

    # Draw connecting lines between close hexagons of same TERYT
    for teryt_code, group in merged_df.groupby("teryt"):
        color = group["color"].iloc[0]
        coords = group[["hexagon_easting", "hexagon_northing"]].values
        for (x1, y1), (x2, y2) in combinations(coords, 2):
            if np.linalg.norm([x2 - x1, y2 - y1]) < 30000:                
                if not pd.isna(color):
                    axs[0].plot([x1, x2], [y1, y2], color=color, linewidth=5, zorder=10)

    axs[0].axis("equal")
    axs[0].axis("off")

    # --- RIGHT PLOT: Powiaty map ---
    powiaty["JPT_KOD_JE"] = powiaty["JPT_KOD_JE"].astype(str).str.zfill(4)
    powiaty = powiaty.merge(teryt_color_df, left_on="JPT_KOD_JE", right_on="teryt", how="left")

    powiaty_clean = powiaty[~powiaty["color"].isna()]
    choropleth = powiaty_clean.plot(ax=axs[1], color=powiaty_clean["color"], edgecolor="white", linewidth=1)

    axs[1].axis("equal")
    axs[1].axis("off")

    cax = axs[1].inset_axes((1.05, 0, 0.03, 1.0))
    sm = choropleth.collections[0]
    plt.colorbar(sm, cax=cax)

    plt.tight_layout()
    plt.show()


import pandas as pd

# Load data
election_df = pd.read_csv("presidential_election_2025/aggregated_by_teryt_powiatu.csv", sep=";")

# Rename column
election_df = election_df.rename(columns={"Teryt Powiatu": "teryt"})

# Define color scale
trzaskowski_colors = [
    "#f7fbff",  # <1%
    "#deebf7",  # <2%
    "#c6dbef",  # <4%
    "#9ecae1",  # <8%
    "#6baed6",  # <16%
    "#3182bd",  # <32%
    "#08519c"   # >32%
]

# Compute ratio
election_df["trzaskowski_ratio"] = (
    election_df["TRZASKOWSKI Rafał Kazimierz"] / 
    election_df["Liczba głosów ważnych oddanych łącznie na wszystkich kandydatów (z kart ważnych)"]
)

# Assign colors based on ratio
def assign_color(ratio):
    if ratio < 0.01:
        return trzaskowski_colors[0]
    elif ratio < 0.02:
        return trzaskowski_colors[1]
    elif ratio < 0.04:
        return trzaskowski_colors[2]
    elif ratio < 0.08:
        return trzaskowski_colors[3]
    elif ratio < 0.16:
        return trzaskowski_colors[4]
    elif ratio < 0.32:
        return trzaskowski_colors[5]
    else:
        return trzaskowski_colors[6]

election_df["color"] = election_df["trzaskowski_ratio"].apply(assign_color)
election_df["teryt"] = election_df["teryt"].astype(int).astype(str).str.zfill(6).str[:4]

make_graph(election_df)

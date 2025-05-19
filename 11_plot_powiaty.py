import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
import matplotlib.colors as mcolors

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

def generate_color_scale(base_color, levels,coloring_strategy):    
    assert levels >= 2, "Need at least 2 color levels"

    base_rgb = np.array(mcolors.to_rgb(base_color))
    gray = np.array([0.5, 0.5, 0.5])
    white = np.array([1.0, 1.0, 1.0])

    # Number of steps in each part
    split = coloring_strategy  # first N colors from base to gray
    remaining = levels - split

    # Interpolate: base → gray (first 3)
    colors1 = [mcolors.to_hex(base_rgb * (1 - frac) + gray * frac)
               for frac in np.linspace(0, 1, split)]

    # Interpolate: gray → white (remaining)
    colors2 = [mcolors.to_hex(gray * (1 - frac) + white * frac)
               for frac in np.linspace(1 / (remaining or 1), 1, remaining)]

    return list(reversed(colors1 + colors2))

# Main plotting function
def make_graph(election_df, candidate_col, max_color, title, coloring_strategy):
    thresholds = [0.00, 0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 1.01]  # Upper bounds
    # color_labels = [0, 1, 2, 4, 8, 16, 32]  # For ticks in percent

    # Generate colors
    colors = generate_color_scale(max_color, len(thresholds)-1,coloring_strategy)

    # Calculate ratio
    election_df["ratio"] = (
        election_df[candidate_col] /
        election_df["Liczba głosów ważnych oddanych łącznie na wszystkich kandydatów (z kart ważnych)"]
    )

    # Assign colors
    def assign_color(ratio):
        for i, threshold in enumerate(thresholds):
            if ratio < threshold:
                return colors[i-1]
        return colors[-1]

    election_df["color"] = election_df["ratio"].apply(assign_color)
    #election_df["teryt"] = election_df["teryt"].astype(str).str.zfill(6).str[:4]

    # Load hexagon and powiat data
    hexagon_df = pd.read_csv("optimized_assigned_hexagons.csv")
    hexagon_df["teryt"] = hexagon_df["teryt"].astype(str).str.zfill(4)
    merged_df = hexagon_df.merge(election_df[["teryt", "color"]], on="teryt", how="left")

    powiaty = gpd.read_file("powiaty/powiaty.shp")
    powiaty["JPT_KOD_JE"] = powiaty["JPT_KOD_JE"].astype(str).str.zfill(4)
    powiaty = powiaty.merge(election_df[["teryt", "color"]], left_on="JPT_KOD_JE", right_on="teryt", how="left")

    # Create plots
    #fig, axs = plt.subplots(1, 2, figsize=(20, 10), sharey=True)
    fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharey=True, constrained_layout=True)
    #fig.suptitle(title, fontname="Atkinson Hyperlegible")
    fig.text(0.5, 0.98, title, ha='center', va='top', fontsize=20, fontname="Atkinson Hyperlegible")
    fig.text(0.1, 0.1, "Radost Waszkiewicz (2025)", ha='center', va='top', fontsize=6, fontname="Atkinson Hyperlegible")

    # --- LEFT: Hexagons ---
    for _, row in merged_df.iterrows():
        if pd.notna(row["color"]):
            draw_hexagon(axs[0], row["hexagon_easting"], row["hexagon_northing"], row["color"])

    for teryt_code, group in merged_df.groupby("teryt"):
        color = group["color"].iloc[0]
        coords = group[["hexagon_easting", "hexagon_northing"]].values
        for (x1, y1), (x2, y2) in combinations(coords, 2):
            if np.linalg.norm([x2 - x1, y2 - y1]) < 30000:
                if pd.notna(color):
                    axs[0].plot([x1, x2], [y1, y2], color=color, linewidth=5, zorder=10)

    data_bounds = axs[0].dataLim
    min_x, min_y = data_bounds.min
    max_x, max_y = data_bounds.max

    axs[0].set_xlim(min_x, max_x)
    axs[0].set_ylim(min_y, max_y)
    axs[0].set_aspect('equal')
    axs[0].axis('off')

    # --- RIGHT: Powiaty map ---
    powiaty_clean = powiaty[~powiaty["color"].isna()]
    choropleth = powiaty_clean.plot(ax=axs[1], color=powiaty_clean["color"], edgecolor="white", linewidth=1)

    axs[1].axis("equal")
    axs[1].axis("off")

    # --- Colorbar (with boundaries as ticks) ----------------------------
    from matplotlib.colors import ListedColormap, BoundaryNorm

    boundaries = [0, 0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 1]            
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(boundaries, len(colors))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cax = axs[1].inset_axes((1.05, 0, 0.03, 1.0))
    cbar = plt.colorbar(sm, cax=cax, ticks=boundaries)

    cbar.ax.set_yticklabels([
        "", "1%", "2%", "4%", "8%", "16%", "32%", ""
    ])

    #plt.tight_layout(pad=1,rect=(0, 0, .9, .9))
    #plt.savefig(title+".png",dpi=300)

    plt.tight_layout()    

    plt.savefig(title+".png", bbox_inches = 'tight',dpi=300)
    #plt.show()


# Load and prepare data
election_df = pd.read_csv("presidential_election_2025/aggregated_by_teryt_powiatu.csv", sep=";")
election_df = election_df.rename(columns={"Teryt Powiatu": "teryt"})
election_df["teryt"] = election_df["teryt"].astype(int).astype(str).str.zfill(6).str[:4]

# election_df["duopol"] = 0.5*(election_df["TRZASKOWSKI Rafał Kazimierz"] + election_df["NAWROCKI Karol Tadeusz"])
# make_graph(
#     election_df,
#     candidate_col="duopol",
#     max_color="#00ff00",
#     title="Średnia Trzaskowski-Nawrocki",
#     coloring_strategy=3,
# )
# exit()


# TRZASKOWSKI Rafał Kazimierz;
# NAWROCKI Karol Tadeusz;

# MENTZEN Sławomir Jerzy;
# BRAUN Grzegorz Michał;

# HOŁOWNIA Szymon Franciszek
# ZANDBERG Adrian Tadeusz
# BIEJAT Magdalena Agnieszka


# Call the function
make_graph(
    election_df,
    candidate_col="TRZASKOWSKI Rafał Kazimierz",
    max_color="#ff5c00",
    title="Rafał Trzaskowski",
    coloring_strategy=3,
)

make_graph(
    election_df,
    candidate_col="NAWROCKI Karol Tadeusz",
    max_color="#0141ff",
    title="Karol Nawrocki",
    coloring_strategy=3,
)

make_graph(
    election_df,
    candidate_col="MENTZEN Sławomir Jerzy",
    max_color="#954600",
    title="Sławomir Mentzen",
    coloring_strategy=4,
)

make_graph(
    election_df,
    candidate_col="BRAUN Grzegorz Michał",
    max_color="#00327c",
    title="Grzegorz Braun",
    coloring_strategy=4,
)

make_graph(
    election_df,
    candidate_col="HOŁOWNIA Szymon Franciszek",
    max_color="#ffe200",
    title="Szymon Hołownia",
    coloring_strategy=5,
)

make_graph(
    election_df,
    candidate_col="ZANDBERG Adrian Tadeusz",
    max_color="#4600fd",
    title="Adrian Zandberg",
    coloring_strategy=5,
)

make_graph(
    election_df,
    candidate_col="BIEJAT Magdalena Agnieszka",
    max_color="#fc0000",
    title="Magdalena Biejat",
    coloring_strategy=5,
)
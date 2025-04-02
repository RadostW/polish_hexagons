import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
from tqdm import tqdm  # Progress bar

# Load data
powiaty_df = pd.read_csv("powiaty_tiles_and_midpoints.csv")
hexagons_df = pd.read_csv("hexes_midpoints.csv")

# Sort powiaty by the number of tiles they should get in descending order
powiaty_df = powiaty_df.sort_values(by="tiles", ascending=False)

# Convert hexagon and powiat centers to numpy arrays
hexagon_centers = hexagons_df[['easting', 'northing']].to_numpy()
powiat_centers = powiaty_df[['easting', 'northing']].to_numpy()

plt.scatter(hexagon_centers[:,0], hexagon_centers[:,1], color='red', s=10)  # Red dots for hexagon centers
plt.scatter(powiat_centers[:,0],powiat_centers[:,1], color='green', s=50)  # Green dots for powiat centers
plt.show()

# Prepare an assignment list
assigned_hexagons = []

# Iterate over unique tile counts in descending order
remaining_hexagons = hexagon_centers.tolist()
    
for tile_count in sorted(powiaty_df['tiles'].unique(), reverse=True):
    group = powiaty_df[powiaty_df['tiles'] == tile_count]
    
    print(f"Processing powiaty with {tile_count} tiles each ({len(group)} powiaty)...")

    with tqdm(total=len(group)) as pbar:  # Progress bar for the while loop
        while not group.empty:
            # Compute distances from powiat centers to hexagon centers
            distances = {powiat: distance.cdist([center], remaining_hexagons) for powiat, center in zip(group['name'], group[['easting', 'northing']].to_numpy())}
            
            # Find the powiat for which the closest hexagon is the farthest in the group
            farthest_closest = max(distances, key=lambda p: min(distances[p][0]))

            # Assign the required number of hexagons to this powiat
            required_tiles = tile_count
            sorted_hexes = sorted(remaining_hexagons, key=lambda h: distance.euclidean(h, group.loc[group['name'] == farthest_closest, ['easting', 'northing']].values[0]))
            assign_to_powiat = sorted_hexes[:required_tiles]
            
            # Append assignments to the list
            for hexagon in assign_to_powiat:
                assigned_hexagons.append({
                    "name": farthest_closest,
                    "teryt": group.loc[group['name'] == farthest_closest, 'teryt'].values[0],
                    "powiat_easting": group.loc[group['name'] == farthest_closest, 'easting'].values[0],
                    "powiat_northing": group.loc[group['name'] == farthest_closest, 'northing'].values[0],
                    "hexagon_easting": hexagon[0],
                    "hexagon_northing": hexagon[1]
                })

            # Remove assigned hexagons from the available list
            remaining_hexagons = [h for h in remaining_hexagons if h not in assign_to_powiat]

            # Remove powiat from the group
            group = group[group['name'] != farthest_closest]
            
            pbar.update(1)  # Update progress bar

# Save the output as a CSV file
output_df = pd.DataFrame(assigned_hexagons)
output_df.to_csv("assigned_hexagons.csv", index=False)

print("Assignment complete. Output saved to 'assigned_hexagons.csv'.")

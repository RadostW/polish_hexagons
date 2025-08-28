import geopandas as gpd
import matplotlib.pyplot as plt

# Load the shapefile
powiaty = gpd.read_file("powiaty/powiaty.shp")

# Compute the centroids
powiaty["midpoint"] = powiaty.geometry.centroid

# Export midpoints to CSV
midpoints_df = powiaty[["JPT_NAZWA_","JPT_POWIER","JPT_KOD_JE", "midpoint"]].copy()

midpoints_df = midpoints_df.rename(columns={"JPT_NAZWA_": "nazwa"})
midpoints_df = midpoints_df.rename(columns={"JPT_KOD_JE": "teryt"})

midpoints_df["easting"] = midpoints_df["midpoint"].x
midpoints_df["northing"] = midpoints_df["midpoint"].y
midpoints_df.drop(columns=["midpoint"], inplace=True)
midpoints_df.to_csv("powiaty_midpoints.csv", index=False)

# Display the first few midpoints
print(midpoints_df.head())

# Plot the powiaty with midpoints
ax = powiaty.plot(figsize=(10, 10), edgecolor="black")
powiaty["midpoint"].plot(ax=ax, color="red", markersize=5)

# Show the plot
plt.show()

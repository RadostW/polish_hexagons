import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import pandas as pd

# Load the powiaty shapefile
powiaty = gpd.read_file("powiaty/powiaty.shp")

# Ensure it's in a projected CRS (for meters)
if powiaty.crs is None or powiaty.crs.to_epsg() != 2180:
    powiaty = powiaty.to_crs(epsg=2180)  # Poland's metric CRS

# Get the bounding box of Poland
minx, miny, maxx, maxy = powiaty.total_bounds

# Estimate hexagon size
num_hexagons = 976
area = (maxx - minx) * (maxy - miny)
hex_area = area / num_hexagons  # Area per hexagon
hex_radius = np.sqrt(hex_area / (3 * np.sqrt(3) / 2))  # Hexagon radius

# Function to generate a hexagonal grid that fully covers the bounding box
def create_hex_grid(minx, miny, maxx, maxy, radius):
    """Generate a hexagonal grid covering the bounding box with enough columns."""
    hex_width = 2 * radius
    hex_height = np.sqrt(3) * radius

    # Extend the number of columns slightly to ensure full coverage
    cols = int((maxx - minx) / (hex_width * 0.75)) + 3
    rows = int((maxy - miny) / hex_height) + 3

    hexagons = []
    centroids = []
    
    for row in range(rows):
        for col in range(cols):
            x = minx + col * hex_width * 0.75  # 0.75 accounts for the staggered pattern
            y = miny + row * hex_height
            if col % 2 == 1:
                y += hex_height / 2  # Offset for staggered columns
            
            # Create hexagon
            hexagon = Polygon([
                (x + radius * np.cos(theta), y + radius * np.sin(theta))
                for theta in np.linspace(0, 2 * np.pi, 7)
            ])
            hexagons.append(hexagon)
            centroids.append(Point(x, y))

    return gpd.GeoDataFrame(geometry=hexagons, crs=powiaty.crs), centroids

# Create the hexagonal grid
hex_grid, centroids = create_hex_grid(minx, miny, maxx, maxy, hex_radius)

# Clip hexagons to the shape of Poland
poland_shape = unary_union(powiaty.geometry)  # Merge all powiats into one shape
hex_grid = hex_grid[hex_grid.intersects(poland_shape)]

# Plot everything
fig, ax = plt.subplots(figsize=(10, 10))

# Plot powiaty (Polish counties)
powiaty.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.5)

# Plot hex grid
hex_grid.plot(ax=ax, facecolor="none", edgecolor="blue", alpha=0.8)

# Show plot
print(f"Final number of hexagons: {len(hex_grid)}")
plt.title("Hexagonal Grid Over Poland with Midpoints")
plt.show()

# Export the hexagonal grid as a shapefile
hex_grid.to_file("hexes/hexagonal_grid.shp", driver="ESRI Shapefile")

hex_grid["midpoint"] = hex_grid.geometry.centroid
midpoints_df = hex_grid[["midpoint"]].copy()
midpoints_df["easting"] = midpoints_df["midpoint"].x
midpoints_df["northing"] = midpoints_df["midpoint"].y
midpoints_df.drop(columns=["midpoint"], inplace=True)
midpoints_df.to_csv("hexes_midpoints.csv", index=False)


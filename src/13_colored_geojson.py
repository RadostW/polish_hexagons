import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

# Load GeoJSON
gdf = gpd.read_file("poland_hexagons_wide_bridge.geojson")

# Function to count total points in a geometry
def count_points(geom):
    if geom.geom_type == "Polygon":
        return len(geom.exterior.coords)
    elif geom.geom_type == "MultiPolygon":
        return sum(len(p.exterior.coords) for p in geom.geoms)
    else:
        return 0

# Assign color based on number of points
def assign_color_by_points(geom):
    if count_points(geom) > 10:
        return "orange"
    else:
        return "blue"

gdf["fill"] = gdf["geometry"].apply(assign_color_by_points)
gdf["fill-opacity"] = 0.6   # optional for geojson.io
gdf["stroke"] = "#000000"
gdf["stroke-width"] = 1

# Save colored GeoJSON
gdf.to_file("poland_hexagons_wide_bridge_colored.geojson", driver="GeoJSON")

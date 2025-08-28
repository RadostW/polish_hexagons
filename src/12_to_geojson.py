import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from itertools import combinations

# --- Hexagon geometry constants ---
HEX_SIZE = 11000
HEX_WIDTH = np.sqrt(3) * HEX_SIZE
HEX_HEIGHT = 0.5 * HEX_SIZE

BRIDGE_WIDTH = 0.25*HEX_SIZE

def hexagon_polygon(x, y):
    """Return shapely Polygon of hexagon centered at (x,y)."""
    angles = np.linspace(0, 2 * np.pi, 7)  # 6 points + repeat
    x_hex = x + HEX_SIZE * np.cos(angles)
    y_hex = y + HEX_SIZE * np.sin(angles)
    return Polygon(zip(x_hex, y_hex))

def bridge_rectangle(x1, y1, x2, y2, width=BRIDGE_WIDTH):
    """
    Create a small rectangle (bridge) connecting two hexagon centers.
    width = thickness of the bridge in map units.
    """
    # Vector between centers
    dx, dy = x2 - x1, y2 - y1
    dist = np.hypot(dx, dy)
    if dist == 0:
        return None

    # Midpoint
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2

    # Unit vector along the line
    ux, uy = dx / dist, dy / dist
    # Perpendicular unit vector
    px, py = -uy, ux

    # Half-length is half the distance
    hl = dist / 2
    hw = width / 2

    # Four corners of rectangle
    coords = [
        (mx - hl * ux - hw * px, my - hl * uy - hw * py),
        (mx + hl * ux - hw * px, my + hl * uy - hw * py),
        (mx + hl * ux + hw * px, my + hl * uy + hw * py),
        (mx - hl * ux + hw * px, my - hl * uy + hw * py),
    ]
    return Polygon(coords)

def make_geojson(hexagon_file="optimized_assigned_hexagons.csv", crs="EPSG:2180", outfile="poland_hexagons.geojson"):
    # Load hexagon centers
    hexagon_df = pd.read_csv(hexagon_file)
    hexagon_df["teryt"] = hexagon_df["teryt"].astype(str).str.zfill(4)

    features = []

    for teryt_code, group in hexagon_df.groupby("teryt"):
        # --- Preserve 'name' values ---
        if "name" in group:
            names = group["name"].dropna().unique().tolist()
            name_value = names[0] if len(names) == 1 else names
        else:
            name_value = None

        # --- Build hexagon polygons ---
        hex_polys = [
            hexagon_polygon(x, y)
            for x, y in zip(group["hexagon_easting"], group["hexagon_northing"])
        ]

        # --- Build rectangular bridges ---
        coords = group[["hexagon_easting", "hexagon_northing"]].values
        bridges = []
        for (x1, y1), (x2, y2) in combinations(coords, 2):
            if np.linalg.norm([x2 - x1, y2 - y1]) < 30000:  # threshold
                bridge = bridge_rectangle(x1, y1, x2, y2)
                if bridge:
                    bridges.append(bridge)

        # Combine hexagons + bridges
        all_geoms = hex_polys + bridges
        multipoly = gpd.GeoSeries(all_geoms).union_all()

        features.append({
            "teryt": teryt_code,
            "name": name_value,
            "geometry": multipoly
        })

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(features, crs=crs)

    # Reproject to WGS84 for GeoJSON compatibility
    gdf = gdf.to_crs(epsg=4326)

    # Save
    gdf.to_file(outfile, driver="GeoJSON")

    return gdf

# Example usage
if __name__ == "__main__":
    gdf_result = make_geojson()
    print(gdf_result.head())

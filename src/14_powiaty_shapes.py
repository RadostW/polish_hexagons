import geopandas as gpd
import topojson as tp

# Load shapefile
powiaty = gpd.read_file("powiaty/powiaty.shp")

# Keep only relevant columns and rename
powiaty = powiaty[["JPT_KOD_JE", "JPT_NAZWA_", "geometry"]].rename(
    columns={"JPT_KOD_JE": "teryt", "JPT_NAZWA_": "name"}
)
powiaty["teryt"] = powiaty["teryt"].astype(str).str.zfill(4)

# Ensure original CRS (CRS84 / EPSG:4326)
if powiaty.crs is None:
    powiaty.set_crs("EPSG:4326", inplace=True)
elif powiaty.crs.to_epsg() != 4326:
    powiaty = powiaty.to_crs(epsg=4326)

# Create TopoJSON topology
topo = tp.Topology(powiaty, prequantize=False)

# Topology-preserving simplification with a small tolerance
powiaty_simplified = topo.toposimplify(epsilon=0.005).to_gdf()

# Export simplified GeoJSON with CRS84
powiaty_simplified.to_file(
    "powiaty.geojson", 
    driver="GeoJSON",
    # crs="EPSG:4326"  # ensures CRS84 in the output
)

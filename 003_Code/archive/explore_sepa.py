import geopandas as gpd

# Load PVA data
pva = gpd.read_file("/Users/riteshghorpade/Documents/010_Project/002_Dataset/PotentiallyVulnerableAreas_v2_GPKG")

# Check what we have
print("Shape:", pva.shape)
print("CRS:", pva.crs)
print("Columns:", pva.columns.tolist())
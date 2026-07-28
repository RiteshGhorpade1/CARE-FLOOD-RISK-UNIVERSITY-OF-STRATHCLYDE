import geopandas as gpd
import os

# File paths
files = {
    "SEPA PVA Flood Zones": "/Users/riteshghorpade/Documents/010_Project/002_Dataset/GeoPackage/Data/PVAv2.gpkg",
    "OSM Buildings": "/Users/riteshghorpade/Documents/010_Project/002_Dataset/osm_buildings_glasgow.gpkg",
    "OSM Roads": "/Users/riteshghorpade/Documents/010_Project/002_Dataset/osm_roads_glasgow.gpkg",
    "OSM Water Bodies": "/Users/riteshghorpade/Documents/010_Project/002_Dataset/osm_water_glasgow.gpkg",
    "Elevation Data": "/Users/riteshghorpade/Documents/010_Project/002_Dataset/glasgow_elevation.gpkg"
}

print("=" * 50)
print("CARE Project — Dataset Summary")
print("=" * 50)

total_size = 0
for name, path in files.items():
    # File size
    size_mb = os.path.getsize(path) / (1024 * 1024)
    total_size += size_mb
    
    # Row count
    data = gpd.read_file(path)
    
    print(f"\n{name}")
    print(f"  Rows: {len(data):,}")
    print(f"  Columns: {len(data.columns)}")
    print(f"  File size: {size_mb:.2f} MB")

print("\n" + "=" * 50)
print(f"Total dataset size: {total_size:.2f} MB")
print("=" * 50)
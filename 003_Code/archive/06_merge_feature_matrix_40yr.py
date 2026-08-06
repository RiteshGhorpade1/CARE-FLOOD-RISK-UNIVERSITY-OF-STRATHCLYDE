"""
Build feature_matrix_40yr.csv: the original feature_matrix.csv with its
3-year (2023-2025) rainfall columns replaced by the 39-year (1987-2025)
climatology from rainfall_features_40yr.csv, plus easting/northing carried
over from feature_matrix_with_coords.csv for dashboard mapping.

Row order across feature_matrix.csv, feature_matrix_with_coords.csv, and
rainfall_features_40yr.csv's grid_id is identical (same grid-generation
code, verified by coordinate spot-check and by the shared-column equality
check below), so a straight row-order merge is safe.
"""

import pandas as pd

BASE = "/Users/riteshghorpade/Documents/010_Project/002_Dataset"

FEATURE_COLS = ['elevation', 'dist_to_water', 'dist_to_clyde',
                'building_count', 'road_count', 'mean_annual_mm_day',
                'mean_winter_mm_day', 'wet_days_per_year', 'max_daily_mm']

OLD_RAIN_COLS = ['mean_annual_mm_day', 'mean_winter_mm_day',
                  'wet_days_per_year', 'max_daily_mm']

SHARED_NON_RAIN_COLS = ['elevation', 'dist_to_water', 'dist_to_clyde',
                          'building_count', 'road_count', 'flood_risk']

df = pd.read_csv(f"{BASE}/feature_matrix.csv")
df["grid_id"] = df.index

new_rain = pd.read_csv(f"{BASE}/rainfall_features_40yr.csv")
coords = pd.read_csv(f"{BASE}/feature_matrix_with_coords.csv")

assert len(df) == len(coords), "row count mismatch vs feature_matrix_with_coords.csv"
mismatches = (df[SHARED_NON_RAIN_COLS] != coords[SHARED_NON_RAIN_COLS]).any(axis=1).sum()
assert mismatches == 0, f"{mismatches} rows misaligned vs feature_matrix_with_coords.csv"

merged = df.drop(columns=OLD_RAIN_COLS).merge(new_rain, on="grid_id", how="left")
assert merged["mean_annual_mm_day"].isnull().sum() == 0, "unmatched grid_id after merge"

merged["easting"] = coords["easting"]
merged["northing"] = coords["northing"]

merged = merged[FEATURE_COLS + ["flood_risk", "easting", "northing"]]
merged.to_csv(f"{BASE}/feature_matrix_40yr.csv", index=False)

print("Shape:", merged.shape)
print("Nulls:", merged.isnull().sum().sum())
print(merged.head(3))
print(f"\nSaved to {BASE}/feature_matrix_40yr.csv")

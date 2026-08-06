"""
Compute 4 rainfall climatology features per grid point from the 1987-2025
daily rainfall parquet, aggregated across the full 39-year period.

Wet-day threshold (>=1.0mm) and mean_annual/mean_winter methodology match
the original 2023-2025 feature_matrix.csv derivation (verified against
hadukgrid_daily_glasgow_clean.csv). max_daily_mm intentionally uses the
average of each year's maximum, not a single all-time max, so one extreme
year doesn't dominate a 39-year climatology feature.
"""

import pandas as pd

BASE = "/Users/riteshghorpade/Documents/010_Project/002_Dataset"
IN_PATH = f"{BASE}/rainfall_daily_1987_2025.parquet"
OUT_PATH = f"{BASE}/rainfall_features_40yr.csv"

WET_THRESHOLD_MM = 1.0

df = pd.read_parquet(IN_PATH, columns=["grid_id", "date", "rainfall_mm"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

mean_annual = df.groupby("grid_id")["rainfall_mm"].mean().rename("mean_annual_mm_day")

winter = df[df["month"].isin([12, 1, 2])]
mean_winter = winter.groupby("grid_id")["rainfall_mm"].mean().rename("mean_winter_mm_day")

df["wet"] = df["rainfall_mm"] >= WET_THRESHOLD_MM
wet_per_year = df.groupby(["grid_id", "year"])["wet"].sum()
wet_days_per_year = wet_per_year.groupby("grid_id").mean().rename("wet_days_per_year")

yearly_max = df.groupby(["grid_id", "year"])["rainfall_mm"].max()
max_daily_mm = yearly_max.groupby("grid_id").mean().rename("max_daily_mm")

result = pd.concat([mean_annual, mean_winter, wet_days_per_year, max_daily_mm], axis=1)
result = result.reset_index().sort_values("grid_id").reset_index(drop=True)

print("Shape:", result.shape)
print(result.head())

result.to_csv(OUT_PATH, index=False)
print(f"\nSaved to {OUT_PATH}")

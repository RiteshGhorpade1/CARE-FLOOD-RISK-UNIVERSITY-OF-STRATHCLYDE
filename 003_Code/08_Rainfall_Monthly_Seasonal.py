

from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent / "002_Dataset"
RAIN_DAILY_PARQUET = BASE / "processed" / "rainfall_daily_1987_2025.parquet"
OUT_MONTHLY = BASE / "processed" / "rainfall_monthly_40yr.csv"
OUT_ANNUAL = BASE / "processed" / "rainfall_annual_40yr.csv"

WET_THRESHOLD_MM = 1.0  # matches 02_EDA.ipynb / 03_Feature_Engineering.ipynb

print(f"Loading {RAIN_DAILY_PARQUET} ...")
rainfall_daily = pd.read_parquet(RAIN_DAILY_PARQUET)
print(f"Loaded {len(rainfall_daily):,} rows, {rainfall_daily['grid_id'].nunique():,} grid points")

rainfall_daily["year"] = rainfall_daily["date"].dt.year
rainfall_daily["month"] = rainfall_daily["date"].dt.month
rainfall_daily["wet"] = rainfall_daily["rainfall_mm"] >= WET_THRESHOLD_MM

# --- Per grid_id x month climatology (Step 7b's logic, month-resolved) ---
mean_mm_day = (
    rainfall_daily.groupby(["grid_id", "month"])["rainfall_mm"]
    .mean()
    .rename("mean_mm_day")
)

wet_per_year_month = (
    rainfall_daily.groupby(["grid_id", "year", "month"])["wet"].sum()
)
wet_days = wet_per_year_month.groupby(["grid_id", "month"]).mean().rename("wet_days")

max_per_year_month = (
    rainfall_daily.groupby(["grid_id", "year", "month"])["rainfall_mm"].max()
)
max_daily_mm = max_per_year_month.groupby(["grid_id", "month"]).mean().rename("max_daily_mm")

monthly = pd.concat([mean_mm_day, wet_days, max_daily_mm], axis=1).reset_index()
monthly = monthly.sort_values(["grid_id", "month"]).reset_index(drop=True)

# --- Validation ---
n_grid = rainfall_daily["grid_id"].nunique()
expected_rows = n_grid * 12
assert len(monthly) == expected_rows, (
    f"Expected {expected_rows} rows ({n_grid} grid points x 12 months), got {len(monthly)}"
)
assert monthly.isnull().sum().sum() == 0, "Unexpected nulls in monthly aggregate"
assert sorted(monthly["month"].unique().tolist()) == list(range(1, 13)), "Missing calendar months"
print(f"Validation passed: {len(monthly):,} rows, {n_grid:,} grid points x 12 months, no nulls")

monthly.to_csv(OUT_MONTHLY, index=False)
print(f"Saved {OUT_MONTHLY}")


annual_totals_by_point = rainfall_daily.groupby(["grid_id", "year"])["rainfall_mm"].sum()
area_avg_annual_totals = annual_totals_by_point.groupby("year").mean()  # mean across 7,843 points per year

annual_df = area_avg_annual_totals.rename("total_mm").reset_index()
annual_df.to_csv(OUT_ANNUAL, index=False)
print(f"Saved {OUT_ANNUAL}")

wettest_year = area_avg_annual_totals.idxmax()
driest_year = area_avg_annual_totals.idxmin()
print("\n--- Area-averaged annual rainfall totals (mean across all grid points) ---")
print(area_avg_annual_totals.round(1))
print(f"\nWettest year: {wettest_year} ({area_avg_annual_totals[wettest_year]:.1f}mm)")
print(f"Driest year:  {driest_year} ({area_avg_annual_totals[driest_year]:.1f}mm)")
print(
    "Note: 2020 is missing all of July in the source archive (a pre-existing "
    "gap, see care_dashboard_versionB.py's RAINFALL_YTD_2026 comment) — its "
    "annual total is based on 335/366 days and is likely understated. It is "
    "not the wettest or driest year here, so this does not affect those two "
    "headline figures, but it should not be read as a precise total."
)

monthly_totals_by_point = rainfall_daily.groupby(["grid_id", "year", "month"])["rainfall_mm"].sum()
area_avg_monthly_totals = monthly_totals_by_point.groupby(["year", "month"]).mean()
max_month_key = area_avg_monthly_totals.idxmax()
print(
    f"Highest single-month rainfall total (area-averaged): "
    f"{max_month_key[1]:02d}/{max_month_key[0]} = {area_avg_monthly_totals[max_month_key]:.1f}mm"
)

print(f"\nOverall 39-year mean annual rainfall (area-averaged): {area_avg_annual_totals.mean():.1f}mm")

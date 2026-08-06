"""
Extract daily rainfall at the 7,843-point study grid from the 2026 provisional
HadUK-Grid files (002_Dataset/007_Rainfall_2026_Provisional/, Jan-Jul 2026),
same nearest-cell method as 04_rainfall_extraction.py used for 1987-2025.

This is a year-to-date (YTD) comparison input only — see care_dashboard_*.py's
rainfall-trend section. 2026 is NOT merged into rainfall_daily_1987_2025.parquet
and is NOT used to retrain the model: it's a partial year from a Met Office
"provisional... not an operational service... best endeavours" feed, distinct
from the finalized, citable CEDA v1.3.2.ceda archive the 1987-2025 data comes
from. Blending a partial year into mean_annual_mm_day/wet_days_per_year would
bias those features downward, so it stays in its own file and its own
day-of-year-matched comparison, never in the training feature matrix.

Usage:
    python3 003_Code/archive/08_rainfall_extraction_2026_ytd.py --test   # 1 file only
    python3 003_Code/archive/08_rainfall_extraction_2026_ytd.py          # full 7-file run
"""

import argparse
import glob
import os

import netCDF4 as nc
import numpy as np
import pandas as pd
from shapely.geometry import Point

BASE = "/Users/riteshghorpade/Documents/010_Project/002_Dataset"
FOLDER = os.path.join(BASE, "007_Rainfall_2026_Provisional")
OUT_PATH = os.path.join(BASE, "rainfall_daily_2026_ytd.parquet")

UNI_X, UNI_Y, RADIUS, GRID_SPACING = 260983, 665006, 5000, 100


def build_grid_points():
    x_coords = np.arange(UNI_X - RADIUS, UNI_X + RADIUS, GRID_SPACING)
    y_coords = np.arange(UNI_Y - RADIUS, UNI_Y + RADIUS, GRID_SPACING)
    grid_points = []
    for x in x_coords:
        for y in y_coords:
            if Point(x, y).distance(Point(UNI_X, UNI_Y)) <= RADIUS:
                grid_points.append((x, y))
    return grid_points


def nearest_indices(coord_array, values):
    diffs = np.abs(coord_array[None, :] - values[:, None])
    return diffs.argmin(axis=1)


def get_file_list(test_mode):
    files = sorted(glob.glob(os.path.join(FOLDER, "*.nc")))
    if test_mode:
        return files[:1]
    return files


def extract_from_file(path, row_idx, col_idx):
    ds = nc.Dataset(path)
    try:
        rainfall = ds.variables["rainfall"][:]  # (time, y, x), masked array
        rainfall = np.ma.filled(rainfall, np.nan)

        t = ds.variables["time"]
        dates = nc.num2date(
            t[:], units=t.units, calendar=getattr(t, "calendar", "standard"),
            only_use_cftime_datetimes=False,
        )
        dates = [d.date() for d in dates]

        values = rainfall[:, row_idx, col_idx]  # (n_times, n_points)
    finally:
        ds.close()
    return dates, values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="run on 1 file only")
    args = parser.parse_args()

    grid_points = build_grid_points()
    n_points = len(grid_points)
    print(f"Grid points: {n_points}")

    xs = np.array([p[0] for p in grid_points])
    ys = np.array([p[1] for p in grid_points])
    grid_ids = np.arange(n_points)

    files = get_file_list(test_mode=args.test)
    print(f"Files to process: {len(files)}")

    ref_ds = nc.Dataset(files[0])
    proj_x = ref_ds.variables["projection_x_coordinate"][:]
    proj_y = ref_ds.variables["projection_y_coordinate"][:]
    ref_ds.close()

    col_idx = nearest_indices(proj_x, xs)
    row_idx = nearest_indices(proj_y, ys)

    chunks = []
    for i, path in enumerate(files, 1):
        dates, values = extract_from_file(path, row_idx, col_idx)
        n_times = len(dates)
        date_col = np.repeat(dates, n_points)
        grid_col = np.tile(grid_ids, n_times)
        rain_col = values.reshape(-1)
        chunks.append(
            pd.DataFrame(
                {"grid_id": grid_col, "date": date_col, "rainfall_mm": rain_col}
            )
        )
        print(f"[{i}/{len(files)}] {os.path.basename(path)}: {n_times} days")

    result = pd.concat(chunks, ignore_index=True)
    result["date"] = pd.to_datetime(result["date"])
    result = result.sort_values(["date", "grid_id"]).reset_index(drop=True)

    print("\nOutput shape:", result.shape)
    print(result.head(10))
    print(result.tail(5))

    if not args.test:
        result.to_parquet(OUT_PATH, index=False)
        print(f"\nSaved to {OUT_PATH}")
    else:
        print("\n[test mode] Not saving to parquet.")


if __name__ == "__main__":
    main()

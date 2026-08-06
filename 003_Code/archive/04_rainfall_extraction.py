"""
Extract daily rainfall at the 7,843-point study grid from all HadUK-Grid NetCDF
files spanning 1987-2025, combining 006_Rainfall_40yr/ (1987-2022) and
003_NASA/hadukgrid_daily/ (2023-2025) into one continuous long-format table.

Usage:
    python3 003_Code/04_rainfall_extraction.py --test   # 2 files only, sanity check
    python3 003_Code/04_rainfall_extraction.py          # full 467-file run
"""

import argparse
import glob
import os

import netCDF4 as nc
import numpy as np
import pandas as pd
from shapely.geometry import Point

BASE = "/Users/riteshghorpade/Documents/010_Project/002_Dataset"
FOLDER_1 = os.path.join(BASE, "006_Rainfall_40yr")
FOLDER_2 = os.path.join(BASE, "003_NASA", "hadukgrid_daily")
OUT_PATH = os.path.join(BASE, "rainfall_daily_1987_2025.parquet")

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
    # coord_array: (n_cells,), values: (n_points,) -> nearest index per point
    diffs = np.abs(coord_array[None, :] - values[:, None])
    return diffs.argmin(axis=1)


def get_file_list(test_mode):
    files_1 = sorted(glob.glob(os.path.join(FOLDER_1, "*.nc")))
    files_2 = sorted(glob.glob(os.path.join(FOLDER_2, "*.nc")))
    if test_mode:
        return [files_1[0], files_2[0]]
    all_files = sorted(files_1 + files_2)
    return all_files


def extract_from_file(path, row_idx, col_idx):
    ds = nc.Dataset(path)
    try:
        rainfall = ds.variables["rainfall"][:]  # (time, y, x), masked array
        rainfall = np.ma.filled(rainfall, np.nan)

        t = ds.variables["time"]
        dates = nc.num2date(
            t[:], units=t.units, calendar=t.calendar, only_use_cftime_datetimes=False
        )
        dates = [d.date() for d in dates]

        # (n_times, n_points) via fancy indexing on y/x dims
        values = rainfall[:, row_idx, col_idx]
    finally:
        ds.close()
    return dates, values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="run on 2 files only")
    args = parser.parse_args()

    grid_points = build_grid_points()
    n_points = len(grid_points)
    print(f"Grid points: {n_points}")

    xs = np.array([p[0] for p in grid_points])
    ys = np.array([p[1] for p in grid_points])
    grid_ids = np.arange(n_points)

    files = get_file_list(test_mode=args.test)
    print(f"Files to process: {len(files)}")

    # raster coordinate grid is identical across all files (confirmed earlier),
    # so compute nearest-cell indices once from the first file
    ref_ds = nc.Dataset(files[0])
    proj_x = ref_ds.variables["projection_x_coordinate"][:]
    proj_y = ref_ds.variables["projection_y_coordinate"][:]
    ref_ds.close()

    col_idx = nearest_indices(proj_x, xs)
    row_idx = nearest_indices(proj_y, ys)

    chunks = []
    for i, path in enumerate(files, 1):
        dates, values = extract_from_file(path, row_idx, col_idx)
        # values: (n_times, n_points) -> long format
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

# Raw data sources

Practical acquisition notes for the datasets `003_Code/01_Data_Collection.ipynb`
through `03_Feature_Engineering.ipynb` expect to find here. For the
methodology behind how each dataset becomes a model feature, see dissertation
Chapter 3, not this file.

None of this is required to just **run** the dashboards — see the top-level
`README.md`'s "Data requirements" table for the three files that actually
matter at runtime (`feature_matrix_40yr.csv`, `rf_model_40yr.joblib`,
`raw/sepa/PVAv2.gpkg`, all already included in this repository).

| Source | Purpose | Acquisition | Repository location | Runtime or preprocessing dependency | Licensing / distribution note |
|---|---|---|---|---|---|
| SEPA Potentially Vulnerable Areas (PVA) v2 | Flood-vulnerability zone boundaries — the spatial basis of the `flood_risk` label and the dashboards' "nearest SEPA flood zone" lookup | Requested from SEPA (Scottish Environment Protection Agency); see the included dataset documentation PDF alongside the file | `raw/sepa/PVAv2.gpkg` (+ `Potentially Vulnerable Areas v2 - Dataset Documentation_v0.1.pdf`) | **Runtime** (Version A & B) and preprocessing (`03_Feature_Engineering.ipynb`) | Included in this repository (10.7MB, within GitHub's per-file limit) |
| OpenStreetMap | Buildings, roads, water geometry — `building_count`, `road_count`, `dist_to_water`, `dist_to_clyde` features | Extracted for the 5km Glasgow study circle via `osmnx`/Overpass API | `raw/osm/osm_buildings_glasgow.gpkg`, `osm_roads_glasgow.gpkg`, `osm_water_glasgow.gpkg` | Preprocessing only (`03_Feature_Engineering.ipynb`); not read by the dashboards directly | Included (Glasgow-clipped extracts, ODbL — attribution: © OpenStreetMap contributors) |
| NASA SRTM | Elevation — the single strongest feature (~63% importance) | Extracted for the study area (originally via the `elevation` Python package / NASA SRTM tiles) | `raw/nasa_elevation/nasa_elevation_glasgow.gpkg` | Preprocessing only (`03_Feature_Engineering.ipynb`) | Included (Glasgow-clipped extract, ~29.9MB; NASA SRTM data is public domain) |
| Met Office HadUK-Grid | Daily rainfall, 1987-2025 — the 4 rainfall climatology features (`mean_annual_mm_day`, `mean_winter_mm_day`, `wet_days_per_year`, `max_daily_mm`) | Obtained from CEDA (Centre for Environmental Data Analysis), 5km daily grid, as 467 monthly NetCDF files | **Not included** — `raw/rainfall/*.nc` (~1.4GB total) and `raw/rainfall_2026_provisional/*.nc` are git-ignored; re-download from CEDA and place them here to reproduce `03_Feature_Engineering.ipynb` from raw data | Preprocessing only (`03_Feature_Engineering.ipynb`); the dashboards read the already-aggregated `feature_matrix_40yr.csv`, not the raw archive | Not redistributed — Met Office/CEDA terms not confirmed for redistribution; no single file exceeds GitHub's 100MB limit, but the aggregate (~1.4GB) is unreasonable to bundle |
| postcodes.io | Live UK postcode → coordinate geocoding for the dashboards' postcode search and postcode-district lookup | No download — free public API called live | N/A (API, not a file) | **Runtime** (Version A & B); requires an internet connection | Third-party free service, no local redistribution involved |

## Notes

- `raw/rainfall/` and `raw/rainfall_2026_provisional/` are git-ignored (see
  `.gitignore`) — the directories exist locally but are not part of this
  repository's git history. If you clone this repository, those two folders
  will be empty; download the CEDA HadUK-Grid archive yourself and place the
  monthly NetCDF files there before running `03_Feature_Engineering.ipynb`
  from raw data.
- The derived daily rainfall parquet
  (`002_Dataset/processed/rainfall_daily_1987_2025.parquet`, ~183MB) is also
  git-ignored for the same reason (exceeds GitHub's 100MB per-file limit) —
  it is regenerated from the raw NetCDF archive by
  `03_Feature_Engineering.ipynb`, Step 7a.
- `archive/001_SEPA/` and `archive/003_NASA/` under `002_Dataset/` hold
  earlier, superseded intermediate data from before the `raw`/`processed`/
  `outputs` reorganisation — kept for provenance only, not used by any
  current notebook or script.

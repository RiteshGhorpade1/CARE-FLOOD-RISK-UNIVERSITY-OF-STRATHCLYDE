# CARE Version C — Implementation Audit

Date: 2026-08-10/11. Companion document to `007_Dashboard/VERSION_C_FEASIBILITY_AUDIT.md` (the pre-implementation feasibility audit produced earlier in this session). This file documents what was actually built, what data it uses, how it was tested, and its known limitations.

**No screenshot file was attached to this conversation.** Version C was built from the detailed section-by-section textual specification supplied by the user (header structure, left/right column contents, exact section numbering/titles, card layouts, colour language, chart/table structure), treated as a transcription of the reference design. If an actual screenshot exists, a follow-up visual diff against it is recommended (see Limitations).

---

## 1. Files created

| File | Purpose |
|---|---|
| `007_Dashboard/care_dashboard_versionC.py` | The new dashboard (1,000+ lines). Independent script, run via `streamlit run 007_Dashboard/care_dashboard_versionC.py`. |
| `003_Code/08_Rainfall_Monthly_Seasonal.py` | Offline preprocessing script. Reads the existing 111.5M-row `rainfall_daily_1987_2025.parquet`, produces the two new CSVs below. Not run by the dashboard itself. |
| `002_Dataset/processed/rainfall_monthly_40yr.csv` | New. 94,116 rows (7,843 grid points × 12 months): `grid_id, month, mean_mm_day, wet_days, max_daily_mm`. |
| `002_Dataset/processed/rainfall_annual_40yr.csv` | New. 39 rows (1987–2025): `year, total_mm`, area-averaged across all 7,843 grid points. |

**Files NOT created or modified**: `care_paths.py` (imported unmodified — no new constants added to it; Version C resolves its two new rainfall paths independently, per the instruction to avoid touching it if avoidable), `requirements.txt` (no new dependency needed — see §6), the model, the dissertation, `feature_matrix*.csv`, `rainfall_features_40yr.csv`, or any other existing dataset.

---

## 2. Data used

Everything in Version C traces to data that already existed in the repository before this session, except the two new CSVs above (themselves derived, not newly collected):

- **Model**: `002_Dataset/processed/rf_model_40yr.joblib` — the same trained RandomForestClassifier used by A and B. Not retrained.
- **Feature matrix**: `002_Dataset/processed/feature_matrix_40yr.csv` — same file, same 7,843 rows, same 9 features.
- **SEPA PVA zones**: `002_Dataset/raw/sepa/PVAv2.gpkg` — same file.
- **Monthly/seasonal/annual rainfall**: derived offline from `002_Dataset/processed/rainfall_daily_1987_2025.parquet` (already produced by `03_Feature_Engineering.ipynb`, not re-touched) — see §3.
- **Historical flood events, River Clyde reference points, RAINFALL_TREND, RAINFALL_YTD_2026, PRECAUTIONS, FEATURE_META**: copied by value from `care_dashboard_versionB.py`, unmodified in content.

No screenshot values were copied into the dashboard. All numbers rendered by Version C (risk %, elevation, SHAP values, monthly rainfall figures, wettest/driest year, etc.) come from the real feature matrix, the real trained model, or the real offline-computed rainfall aggregates.

---

## 3. Rainfall preprocessing — methodology

`003_Code/08_Rainfall_Monthly_Seasonal.py` was run once, offline (not inside Streamlit):

```
python3 003_Code/08_Rainfall_Monthly_Seasonal.py
```

It mirrors `03_Feature_Engineering.ipynb` Step 7b's existing methodology exactly, just grouped by calendar month instead of collapsed to annual/winter figures:

- `mean_mm_day`: mean daily rainfall for that grid_id/month across all years present.
- `wet_days`: count of days ≥1.0mm (the same `WET_THRESHOLD_MM` established in `02_EDA.ipynb`) per grid_id/month/year, averaged across years.
- `max_daily_mm`: max daily rainfall per grid_id/month/year, averaged across years (not a single extreme day) — same reasoning `03_Feature_Engineering.ipynb` already uses for its annual `max_daily_mm`.

**Validation performed by the script itself** (assertions, not just prints): row count = 7,843 grid points × 12 months exactly; zero nulls; all 12 calendar months present. The run output confirmed: `94,116 rows, 7,843 grid points x 12 months, no nulls`.

**Annual series**: area-averaged (mean across all 7,843 grid points) total rainfall per year, 1987–2025, following the same convention `RAINFALL_TREND` already uses in `care_dashboard_versionB.py`.

**Data-quality note carried into the audit and the dashboard's own captions**: 2020 is missing all of July in the source archive (335/366 days present) — a pre-existing gap, already disclosed in `versionB.py`'s `RAINFALL_YTD_2026` comment, not introduced by this work. 2020 is neither the wettest nor driest year in the 39-year series, so this doesn't affect those two headline figures, but its own annual total is likely understated. The dashboard's Historical Rainfall Summary caption states this explicitly.

**Computed headline statistics** (real output, printed by the script and transcribed into `HISTORICAL_RAINFALL_STATS` in `care_dashboard_versionC.py`, the same "offline script → hardcoded constant" convention `RAINFALL_TREND`/`RAINFALL_YTD_2026` already use in B):
- Mean annual rainfall (39-yr, area-averaged): **1079.0mm**
- Wettest year: **2011** (1427.8mm)
- Driest year: **2001** (789.1mm)
- Highest single-month total (area-averaged): **February 2020** (250.4mm — consistent with the real, widely-documented Storm Ciara/Dennis winter)

---

## 4. Model and SHAP

Unchanged from `care_dashboard_versionB.py`: `shap.TreeExplainer(model, data=X_train, model_output="probability")`, background = the 80% training split reconstructed via `train_test_split(..., random_state=42, stratify=y)` (same seed as `04_ML_Model.ipynb`), explainer cached via `st.cache_resource`, per-click `shap_values()` computed live per selected point. `FEATURE_META` (definitions, tiered narrative fragments, bar labels) copied verbatim from `versionB.py`. The "Why this result?" section (8) reproduces B's diverging bar chart, its caveat text, and its top-2-feature definitions/expander for the rest — same code, same values, just placed inline in the right column instead of inside a separate `st.tabs()` tab (Version C has no tabs at all, per the fixed two-column layout requirement).

The Section 2 "interpretation card" reuses the same SHAP computation (computed once per rerun, shared between sections 2 and 8 — not recomputed twice) but wraps it in hedged language per the requested terminology: "model assessment indicates," "associated with," "contributed most to the model output," explicitly disclaiming a direct causal claim.

---

## 5. Testing performed

All testing was done against a live `streamlit run 007_Dashboard/care_dashboard_versionC.py` instance (port 8503) via browser automation. Console was checked for JS errors (none found) after page load.

| Test | Result |
|---|---|
| Cold start / default state | Loads correctly; default point = University of Strathclyde; all 9 sections render with real data; no console errors. |
| Postcode search (valid, `G4 0BA`) | Correctly geocoded via postcodes.io; `admin_district` ("Glasgow City") captured and shown in Location Details; risk level, confidence, monthly chart, SHAP panel all updated to the new location. |
| Postcode search (invalid, `ZZ99 9ZZ`) | Correct error message shown ("Postcode 'ZZ99 9ZZ' not found..."); previous selection preserved, not cleared. |
| Reset All | Correctly clears search state, error/warning, and reverts to the default University point; postcode input field cleared. |
| Map click-to-select | Clicking a marker updates `selected_point`, and all dependent sections (Prediction Summary, Location Details, Monthly Rainfall table, SHAP bars) recompute correctly for the newly selected grid point (verified: elevation, coordinates, and monthly rainfall table all changed to match the new point). |
| Risk-level filter | Removing "Low risk" and "High risk" chips correctly reduces the map to only medium-risk (orange) points; historical event markers remain visible. |
| Monthly table/chart | 12 distinct month labels (Jan–Dec), no duplicates; values change correctly per selected point. |
| Historical rainfall chart/cards | Matches the offline-computed constants exactly (1079mm mean, 2011/1428mm wettest, 2001/789mm driest, Feb 2020/250mm max month). |
| Seasonal cards | 4 distinct seasons, each with a relative (Low/Moderate/High) exposure category computed from that point's own seasonal means — verified non-identical across seasons for the default point (Winter=High, Spring=Low, Summer=Moderate, Autumn=Moderate). |
| SHAP panel | Renders 9 ranked, colour-coded bars with real per-point SHAP values; caveat text present; top-2 feature definitions shown inline, remaining 7 behind expander. |
| Recommendations | `PRECAUTIONS` content renders correctly, keyed to the selected point's predicted risk class. |
| Version A still runs | `streamlit run care_dashboard_versionA.py` — loads and renders correctly (verified live in browser), unaffected. |
| Version B still runs | `streamlit run care_dashboard_versionB.py` — loads and renders correctly (verified live in browser), unaffected. |

**Not separately tested**: the "missing data" scenario requested in the task (no meaningful way to trigger this without deleting a real data file, which would violate "do not modify datasets") — the existing `require()` guard in `care_paths.py` and the new `require()` calls for the two rainfall CSVs already fail loudly with a clear message if a file is absent, matching A/B's existing pattern. Responsive/narrow-viewport layout was not tested (browser automation used a standard desktop viewport only).

---

## 6. Dependencies

No new Python packages required. Every import in `care_dashboard_versionC.py` (`streamlit`, `pandas`, `numpy`, `joblib`, `folium`, `requests`, `shap`, `geopandas`, `matplotlib`, `scikit-learn`, `streamlit_folium`, `pyproj`, `shapely`, plus `calendar`/`datetime`/`math`/`pathlib`/`urllib.parse` from the standard library) is already pinned in the repo-root `requirements.txt`. `003_Code/08_Rainfall_Monthly_Seasonal.py` uses only `pandas` and `pathlib`, both already present. `requirements.txt` was not modified.

---

## 7. Version A / B protection

Hashes recorded before any implementation work and re-checked after completion:

```
Before:
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f  care_dashboard_versionA.py
613fa0dc120e9c9b593454d549e27da27385f30aaae9618d77020cd2b7b1745c  care_dashboard_versionB.py

After:
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f  care_dashboard_versionA.py
613fa0dc120e9c9b593454d549e27da27385f30aaae9618d77020cd2b7b1745c  care_dashboard_versionB.py
```

**Identical.** `git diff -- 007_Dashboard/care_dashboard_versionA.py` and `git diff -- 007_Dashboard/care_dashboard_versionB.py` both produce no output. `care_paths.py` was imported but not edited. Both A and B were launched live and confirmed working after Version C was built.

---

## 8. Known limitations / deliberate deviations from the literal spec

1. **No screenshot was actually available.** Built from the written section-by-section description. If a real reference image exists, a direct pixel/layout comparison hasn't been done and should be a follow-up.
2. **Risk scale uses 3 tiers (Low/Medium/High), not 4.** The trained model has exactly 3 classes; a 4th "Very High" tier would be fabricated and was deliberately omitted per the spec's own instruction not to invent a new risk scale.
3. **No functional Version A/B navigation links in the header.** They're rendered as static badges (Version C highlighted as active). Real cross-version navigation isn't safely available without either restructuring how the three scripts are launched (they're three independent `streamlit run` processes with no shared routing) or modifying A/B — both out of scope per the "do not modify A/B" and "don't add functionality that requires touching them" constraints.
4. **Version B's district/landmark "browse" dropdown was dropped.** Section 9 of the spec describes the postcode section as just an input, button, and status line (matching the simpler reference layout); postcode search, map click-to-select, and the map's own postcode-district filter all remain fully functional. This was a deliberate scope trim, documented rather than silently omitted.
5. **Uneven column heights.** Streamlit's `st.columns()` renders both columns independently; because the left column (4 sections) is shorter than the right column (5 sections, several with charts), a visible gap appears beneath the left column's content on tall right-column views. This is a known Streamlit layout constraint (B's own source code comments describe hitting the identical issue elsewhere) — not something CSS alone can reliably fix without deeper restructuring, and out of scope for "don't redesign the layout."
6. **Historical rainfall stats are area-averaged, not per-selected-point.** Matches the existing precedent (`RAINFALL_TREND`) and avoids implying more spatial precision in 39-year extremes than a 5km-resolution rainfall raster actually supports. Monthly/seasonal exposure (sections 5 and 7), by contrast, is genuinely per-selected-grid-point, since that data already exists at that resolution.
7. **"Local authority" is only available for postcode-search results**, not for the default University point or map clicks (postcodes.io's district-only reverse-geocode endpoint used for the map's district filter doesn't return `admin_district`). Displayed honestly as "Not available for this location" rather than fabricated — confirmed working correctly in testing.

---

## 9. Git state

```
$ git status --short | grep -E "versionC|08_Rainfall|rainfall_monthly_40yr|rainfall_annual_40yr|VERSION_C"
?? 002_Dataset/processed/rainfall_annual_40yr.csv
?? 002_Dataset/processed/rainfall_monthly_40yr.csv
?? 003_Code/08_Rainfall_Monthly_Seasonal.py
?? 007_Dashboard/care_dashboard_versionC.py
```

All four new files are untracked. Nothing was staged or committed. The large pre-existing staged diff visible in `git status` (the `002_Dataset/` raw/processed/outputs/archive reorg) predates this session and was not touched. No commit or push was performed, per instruction.

To run Version C:
```bash
python3 003_Code/08_Rainfall_Monthly_Seasonal.py   # one-time, if the two rainfall CSVs don't already exist
python3 -m streamlit run 007_Dashboard/care_dashboard_versionC.py
```

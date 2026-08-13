# CARE Dashboard
## Climate Awareness and Risk Evaluation Dashboard

**Student:** Ritesh Raju Ghorpade (202559288)
**Programme:** MSc Advanced Computer Science with Data Science
**University:** University of Strathclyde, Glasgow
**Supervisor:** Dr Daniel Thomas (d.thomas@strath.ac.uk)
**Submission Deadline:** 17th August 2026, noon UK time

CARE is a geospatial data science MSc dissertation project. It builds a
Random Forest flood-risk classifier for a 5km radius around the University of
Strathclyde, Glasgow (centre: easting 260983, northing 665006, EPSG:27700),
explains individual predictions with SHAP, and serves both through a
Streamlit dashboard.

**Important limitation:** the model predicts/reconstructs an engineered
flood-risk proxy label (SEPA flood-vulnerability zone membership combined
with elevation), and has not been independently validated against observed
real-world flood outcomes. Its outputs are research classifications, not an
official flood risk assessment — see the in-dashboard disclaimers and
Chapter 4/6 of the dissertation for the full discussion.

---

## Quick start — run the dashboards

Tested on **macOS, Python 3.9.6**. Not tested on Windows or Linux.

```bash
git clone <repository-url>
cd <repository>

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python3 -m streamlit run 007_Dashboard/care_dashboard_versionA.py
```

and, in a separate terminal/session:

```bash
python3 -m streamlit run 007_Dashboard/care_dashboard_versionB.py
```

Run both commands from the repository root — the dashboards resolve their
data/model paths relative to their own file location (`007_Dashboard/`, via
`care_paths.py`), and Streamlit's theme (`.streamlit/config.toml`) resolves
relative to the working directory the command is launched from. No source
files need editing and no personal filesystem paths need to be substituted.

**Version A** — risk badge, model confidence, coordinates, compass indicator,
citywide context cards, and the raw feature table. No SHAP.

**Version B** — everything in Version A, plus a live SHAP explanation panel
("Why this prediction?" tab): a plain-English narrative naming the top
driving features, all 9 features as ranked colour-coded bars, and a
dark-themed layout.

### Data requirements

The three files both dashboards need at runtime are already included in this
repository (see the table below) — no separate download is required to run
either dashboard. An internet connection is required for live UK postcode
search (via the free [postcodes.io](https://postcodes.io) API); the rest of
the dashboard works offline.

**No participant or ethics data is required to run the dashboards.** That
material (`004_Ethics/Recruitment/`, the participant questionnaire
spreadsheet, consent forms) is excluded from this repository entirely — see
[Privacy](#privacy) below.

| File | Purpose | Required by |
|---|---|---|
| `002_Dataset/processed/feature_matrix_40yr.csv` | 7,843-point feature matrix (9 features + coordinates) the model predicts over | Version A, Version B |
| `002_Dataset/processed/rf_model_40yr.joblib` | Trained Random Forest classifier | Version A, Version B |
| `002_Dataset/raw/sepa/PVAv2.gpkg` | SEPA Potentially Vulnerable Area flood boundaries (nearest-flood-zone lookup) | Version A, Version B |
| `.streamlit/config.toml` | Shared light theme (Version A; Version B overrides with its own dark theme) | Version A |
| postcodes.io API (live) | Postcode search, postcode-district lookup | Version A, Version B |

If a required file is missing, the dashboard raises a clear
`FileNotFoundError` naming the missing file and pointing back to this
README, rather than a raw path error.

---

## Full research reproduction

The full pipeline — source data through model training — is not required to
run the dashboards (see Quick start above), but every stage is reproducible
from this repository plus publicly available source data.

```
Source datasets (SEPA / OSM / NASA / HadUK-Grid)
        │
        ▼
003_Code/01_Data_Collection.ipynb      — loads & previews all raw datasets
        │
        ▼
003_Code/02_EDA.ipynb                  — per-dataset exploration, dist_to_clyde derivation
        │
        ▼
003_Code/03_Feature_Engineering.ipynb  — 100m grid, 9 features, 39yr rainfall
        │                                 climatology, flood_risk label
        │                                 → 002_Dataset/processed/feature_matrix*.csv
        ▼
003_Code/04_ML_Model.ipynb             — RandomForestClassifier, evaluation, SHAP
        │                                 → 002_Dataset/processed/rf_model_40yr.joblib
        ▼
007_Dashboard/care_dashboard_versionA.py / versionB.py
```

Run the four notebooks in `003_Code/` in numeric order from within that
folder (`003_Code/` is each notebook's default Jupyter working directory —
their paths are resolved relative to it). `003_Code/05_Dissertation_Figures.py`,
`06_Dissertation_Diagrams.py`, and `07_Usability_Figures.py` regenerate the
dissertation's data-driven figures, conceptual diagrams, and usability-study
figures respectively, and can be run standalone (`python3 003_Code/05_Dissertation_Figures.py`
from the repository root).

`003_Code/archive/` holds superseded exploratory notebooks/scripts kept only
for provenance — see `003_Code/archive/README.md`. They are not part of the
maintained pipeline and are not guaranteed to run as-is.

### External source datasets

These are not redistributed in this repository (redistribution licensing was
not confirmed for all of them, and the merged HadUK-Grid rainfall archive
alone totals ~1.4GB, well beyond what's reasonable to bundle even though no
single file exceeds GitHub's 100MB per-file limit). Obtain them from source
to reproduce the pipeline from raw data — see `002_Dataset/raw/README.md`
for exact acquisition instructions and where each one is expected to live
locally:

- **SEPA Potentially Vulnerable Areas (PVA)** — flood boundary zones (the
  processed `PVAv2.gpkg` used by the dashboards *is* included; see the table
  above)
- **OpenStreetMap** — buildings, roads, water (via Overpass/osmnx)
- **NASA SRTM** — elevation
- **Met Office HadUK-Grid** — daily rainfall, 1987-2025 (via CEDA)
- **postcodes.io** — live UK postcode/outcode geocoding API (no download; used at dashboard runtime)

---

## Privacy

`004_Ethics/Recruitment/`, the participant questionnaire spreadsheet, and
personal working notes are git-ignored and have never been committed to this
repository's history — see `.gitignore`. The Consent Form and Participant
Information Sheet templates under `004_Ethics/001_Final_Approved/` are the
blank, ethics-committee-approved templates, not completed participant
submissions, and contain no participant-identifying information. Aggregated,
anonymised findings (e.g. participant counts, thematic summaries) appear in
the dissertation (Chapter 5) as approved by the study's ethics application.

---

## Repository structure

```
001_Proposal_and_Feedback/ Original research proposal and marking feedback (dissertation admin)
002_Dataset/          Raw and processed geospatial/tabular data (see 002_Dataset/raw/README.md)
  raw/                 Source data as obtained from SEPA / OSM / NASA / HadUK-Grid
  processed/           Derived feature matrices, trained model
  outputs/              Generated figures (build artefacts, not source)
  archive/              Superseded intermediate data from earlier reorganisations
003_Code/              Pipeline notebooks (01-04) and dissertation figure scripts (05-07)
  archive/               Superseded exploratory notebooks/scripts (provenance only)
004_Ethics/             Ethics approval documents (templates only — see Privacy)
005_Progress_Logs/      Submitted progress logs
006_Dissertation/       Dissertation chapters, figures, appendix
007_Dashboard/          Streamlit dashboards (versionA, versionB) and their build history
008_Reference_Documents/ Reference material
009_Project Report Structure/ Dissertation structure/style planning docs (admin, not source)
```

## Environment

- **Python:** 3.9.6 (see `requirements.txt` for exact package pins)
- **OS:** Developed and tested on macOS. Not tested on Windows or Linux.
- **Key libraries:** `geopandas`, `shapely`, `pandas`, `numpy`, `scikit-learn`,
  `shap`, `xgboost`, `matplotlib` for the analysis/modelling notebooks;
  `streamlit`, `folium`, `streamlit-folium`, `pyproj`, `requests` for the
  dashboards.

## Coordinate systems

Source geospatial data and all feature engineering use **EPSG:27700**
(British National Grid, easting/northing). Coordinates are converted to
**EPSG:4326** (lat/lon) only at the presentation layer (`folium` map
rendering in the dashboards).

## Known limitations

- The flood-risk label is an engineered proxy (SEPA PVA zone membership +
  elevation threshold), not an independently validated real-world flood
  outcome — model accuracy reflects how well it reconstructs that label, not
  real-world flood prediction skill.
- Spatial autocorrelation: nearby grid points share similar feature values,
  which can inflate cross-validation scores under random splitting — the
  dissertation also reports spatial-block cross-validation as a check
  (Chapter 4).
- Single-city (Glasgow), 5km-radius scope.
- Environmental features (elevation, rainfall) are static/batch snapshots,
  not live sensor feeds.
- The XGBoost comparison model (Chapter 4) is not SHAP-explained in the
  dashboard — only the primary Random Forest model is.
- Usability evaluation is based on a small sample (n=6: 3 Version A, 3
  Version B) — see Chapter 5 for the full discussion, including two
  documented data-quality anomalies in the questionnaire responses.
- Accessibility testing did not specifically recruit assistive-technology
  users.
- No automated test suite exists for this project — verification is via the
  notebooks' own printed diagnostics and manual dashboard walkthroughs.

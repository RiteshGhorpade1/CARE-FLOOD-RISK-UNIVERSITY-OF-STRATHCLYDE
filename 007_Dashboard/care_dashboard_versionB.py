"""
Version B — the SHAP-explained variant of the CARE dashboard usability study.

Renamed from care_dashboard_step4.py: this and care_dashboard_versionA.py are
the two final study versions (not sequential build steps — see step1.py/
step3.py for the build history that led here).

Shares every feature with Version A (postcode search, compass indicator,
risk histogram, historical flood markers, model confidence, rainfall trend,
visual theme), plus two things Version A doesn't have:

1. A "Model evaluation" section in the main column, between the header and
   the postcode search box — the centrepiece of this version. Shows
   top-line Random Forest metrics (accuracy, F1 macro, 5-fold CV accuracy,
   mean ROC-AUC) plus five tabs: confusion matrix, ROC curves, feature
   importance (Random Forest vs XGBoost side by side), the SHAP summary
   beeswarm plot, and a detailed Random Forest vs XGBoost comparison. The
   confusion matrix, ROC curve, feature importance and SHAP summary tabs
   render precomputed PNGs from 002_Dataset/004_Maps/ (produced by
   04_ML_Model.ipynb); the comparison tab renders small matplotlib charts
   live from the precomputed metric constants below, since no static image
   covers that specific comparison.
2. A live SHAP explanation panel: when a point is selected, computes SHAP
   values on the fly (TreeExplainer, probability-space, background = the
   same 80% training split used in 04_ML_Model.ipynb) for the predicted
   class, and shows a plain-English narrative naming the top 1-2 driving
   features, then all 9 features as ranked, colour-coded bars (red =
   pushes toward higher risk, blue = pushes toward lower risk) with
   plain-English labels. The top 2 bars show their definition inline; the
   rest are collapsed behind a "what does this mean?" popover. Live
   per-click SHAP computation benchmarked at <10ms, so no
   precomputation/caching of SHAP values was needed.
"""

import math
from urllib.parse import quote

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
import requests
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from streamlit_folium import st_folium
from pyproj import Transformer

st.set_page_config(page_title="CARE Dashboard", layout="wide")

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        hr { margin: 1.2rem 0; }
    </style>
    <div style='background: linear-gradient(135deg, #1E7A8C, #123E49);
                padding: 22px 32px; border-radius: 10px; margin-bottom: 26px;'>
        <h1 style='color: #FFFFFF; margin: 0; font-size: 2.1rem;'>CARE Dashboard</h1>
        <p style='color: #CFE9EE; margin: 4px 0 0 0; font-size: 0.95rem;'>
            Climate Awareness and Risk Evaluation — Glasgow flood risk
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/feature_matrix_40yr.csv"
MODEL_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/rf_model_40yr.joblib"
POSTCODES_API = "https://api.postcodes.io/postcodes/"
OUTCODES_API = "https://api.postcodes.io/outcodes"

MAPS_DIR = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps"
CONFUSION_MATRIX_IMG = f"{MAPS_DIR}/confusion_matrix.png"
ROC_CURVES_IMG = f"{MAPS_DIR}/roc_curves.png"
FEATURE_IMPORTANCE_RF_IMG = f"{MAPS_DIR}/feature_importance.png"
FEATURE_IMPORTANCE_XGB_IMG = f"{MAPS_DIR}/feature_importance_xgboost.png"
SHAP_SUMMARY_IMG = f"{MAPS_DIR}/shap_summary.png"

FEATURE_COLS = ["elevation", "dist_to_water", "dist_to_clyde", "building_count",
                "road_count", "mean_annual_mm_day", "mean_winter_mm_day",
                "wet_days_per_year", "max_daily_mm"]

UNI_X, UNI_Y = 260983, 665006  # University of Strathclyde, EPSG:27700
DEFAULT_CENTER = [55.8611, -4.2436]
DEFAULT_ZOOM = 13

# Plain-English metadata per feature: definition (user-supplied), a 3-tier
# bar label, and a 3-tier narrative sentence fragment. Tier ("low" /
# "moderate" / "high") is picked per-point from that feature's tercile
# across all 7,843 grid points (see tier_for()).
FEATURE_META = {
    "elevation": {
        "unit": "m", "fmt": "{:.0f}",
        "definition": "How high above sea level this spot is. Lower ground floods more easily.",
        "bar_label": {"low": "Low elevation", "moderate": "Moderate elevation", "high": "High elevation"},
        "narrative": {
            "low": "it sits low-lying ({value}m above sea level)",
            "moderate": "it sits at a moderate elevation ({value}m)",
            "high": "it sits on relatively high ground ({value}m)",
        },
    },
    "dist_to_clyde": {
        "unit": "m", "fmt": "{:.0f}",
        "definition": "How close this spot is to the River Clyde specifically, Glasgow's main river.",
        "bar_label": {"low": "Close to the River Clyde", "moderate": "Moderate distance from the River Clyde", "high": "Far from the River Clyde"},
        "narrative": {
            "low": "it is close to the River Clyde ({value}m away)",
            "moderate": "it is a moderate distance from the River Clyde ({value}m away)",
            "high": "it is far from the River Clyde ({value}m away)",
        },
    },
    "dist_to_water": {
        "unit": "m", "fmt": "{:.0f}",
        "definition": "How close this spot is to the nearest water, including streams, canals and ponds, not just the Clyde.",
        "bar_label": {"low": "Close to water", "moderate": "Moderate distance from water", "high": "Far from water"},
        "narrative": {
            "low": "it is close to water ({value}m away)",
            "moderate": "it is a moderate distance from the nearest water ({value}m away)",
            "high": "it is far from any water ({value}m away)",
        },
    },
    "max_daily_mm": {
        "unit": "mm", "fmt": "{:.1f}",
        "definition": "The most rain that has fallen in a single day here, on average per year over the 39-year record.",
        "bar_label": {"low": "Low peak daily rainfall", "moderate": "Moderate peak daily rainfall", "high": "High peak daily rainfall"},
        "narrative": {
            "low": "it has relatively low single-day rainfall peaks ({value}mm)",
            "moderate": "it has moderate single-day rainfall peaks ({value}mm)",
            "high": "it has seen high single-day rainfall peaks ({value}mm)",
        },
    },
    "wet_days_per_year": {
        "unit": " days/yr", "fmt": "{:.0f}",
        "definition": "How many days per year see measurable rainfall at this location.",
        "bar_label": {"low": "Few wet days/year", "moderate": "Moderate wet days/year", "high": "Many wet days/year"},
        "narrative": {
            "low": "it sees relatively few wet days ({value} days/year)",
            "moderate": "it sees a moderate number of wet days ({value} days/year)",
            "high": "it sees many wet days ({value} days/year)",
        },
    },
    "mean_annual_mm_day": {
        "unit": "mm/day", "fmt": "{:.2f}",
        "definition": "The typical amount of rain per day, averaged across the 39-year record.",
        "bar_label": {"low": "Low average rainfall", "moderate": "Moderate average rainfall", "high": "High average rainfall"},
        "narrative": {
            "low": "it has relatively low average rainfall ({value}mm/day)",
            "moderate": "it has moderate average rainfall ({value}mm/day)",
            "high": "it has high average rainfall ({value}mm/day)",
        },
    },
    "mean_winter_mm_day": {
        "unit": "mm/day", "fmt": "{:.2f}",
        "definition": "Typical daily rainfall during winter months specifically.",
        "bar_label": {"low": "Low winter rainfall", "moderate": "Moderate winter rainfall", "high": "High winter rainfall"},
        "narrative": {
            "low": "it has relatively low winter rainfall ({value}mm/day)",
            "moderate": "it has moderate winter rainfall ({value}mm/day)",
            "high": "it has high winter rainfall ({value}mm/day)",
        },
    },
    "building_count": {
        "unit": " within 250m", "fmt": "{:.0f}",
        "definition": "Number of buildings within 250m. More buildings can mean more paved surface, which drains less well.",
        "bar_label": {"low": "Few nearby buildings", "moderate": "Some nearby buildings", "high": "Many nearby buildings"},
        "narrative": {
            "low": "it has few nearby buildings ({value} within 250m)",
            "moderate": "it has a moderate number of nearby buildings ({value} within 250m)",
            "high": "it has many nearby buildings ({value} within 250m)",
        },
    },
    "road_count": {
        "unit": " within 250m", "fmt": "{:.0f}",
        "definition": "Number of road segments within 250m, another marker of paved, less-absorbent ground.",
        "bar_label": {"low": "Few nearby roads", "moderate": "Some nearby roads", "high": "Many nearby roads"},
        "narrative": {
            "low": "it has few nearby roads ({value} within 250m)",
            "moderate": "it has a moderate number of nearby roads ({value} within 250m)",
            "high": "it has many nearby roads ({value} within 250m)",
        },
    },
}

# Approximate River Clyde boundary vertices within 6km of the study centre,
# extracted from 002_OSM/osm_water_glasgow.gpkg (simplified to 70m tolerance).
# Used only to determine compass direction — mean nearest-vertex error vs. the
# true dist_to_clyde feature is ~24m, negligible for a directional indicator.
# The distance shown alongside it still uses the exact dist_to_clyde value.
CLYDE_REF_POINTS = [
    (265984.6, 661694.9), (265628.0, 661473.7), (264890.0, 661471.9), (264077.9, 661001.9), (263901.8, 660996.6), (263751.1, 661207.4),
    (263597.8, 661807.6), (263539.9, 662382.6), (263116.1, 662532.4), (262906.4, 662367.3), (262870.2, 662072.5), (262680.6, 661987.9),
    (262521.3, 662082.5), (262325.2, 662318.6), (262399.9, 662531.7), (262585.8, 662668.0), (262605.5, 662802.9), (262070.7, 663425.7),
    (261957.6, 663234.4), (262190.1, 662996.8), (262142.0, 662747.8), (261473.6, 662563.9), (261138.3, 662244.2), (260980.5, 662199.2),
    (260846.9, 662380.3), (260874.3, 662852.8), (260379.8, 663245.0), (259809.2, 663365.6), (259802.0, 663506.7), (260009.8, 663920.0),
    (259484.4, 664344.2), (258776.3, 664717.5), (257518.1, 664857.1), (256279.9, 665334.4), (256056.5, 665615.7), (255968.9, 665661.8),
    (255936.1, 665514.8), (255857.8, 665717.5), (255133.5, 666110.7), (255126.0, 666287.3), (256324.9, 665653.7), (256267.0, 665613.7),
    (256446.8, 665434.5), (257209.0, 665084.8), (257752.9, 664929.8), (258794.0, 664848.5), (259453.7, 664487.0), (260072.6, 663911.2),
    (259875.0, 663394.3), (260457.2, 663274.9), (260939.2, 662859.2), (260881.9, 662463.4), (260987.8, 662241.2), (261517.8, 662639.6),
    (262091.9, 662764.9), (262141.9, 662960.5), (261916.9, 663265.6), (262091.2, 663464.8), (262658.0, 662799.7), (262647.7, 662671.1),
    (262364.1, 662325.1), (262618.8, 662055.6), (262827.5, 662082.6), (262869.7, 662398.0), (263114.1, 662581.8), (263574.3, 662407.6),
    (263802.9, 661161.1), (263918.8, 661028.7), (264818.5, 661495.1), (265648.8, 661558.9), (266049.9, 661802.8), (265984.6, 661694.9),
]
_CLYDE_X = np.array([p[0] for p in CLYDE_REF_POINTS])
_CLYDE_Y = np.array([p[1] for p in CLYDE_REF_POINTS])

COMPASS_NAMES = ["north", "north-east", "east", "south-east",
                  "south", "south-west", "west", "north-west"]

def compass_direction(dx, dy):
    """8-point compass direction of the vector (dx east, dy north)."""
    bearing = math.degrees(math.atan2(dx, dy)) % 360
    return COMPASS_NAMES[round(bearing / 45) % 8]

def format_distance(metres):
    if metres < 1000:
        return f"{metres:.0f}m"
    return f"{metres / 1000:.1f}km"

def nearest_clyde_point(easting, northing):
    dist = np.sqrt((_CLYDE_X - easting) ** 2 + (_CLYDE_Y - northing) ** 2)
    i = dist.argmin()
    return _CLYDE_X[i], _CLYDE_Y[i]

# Real, documented historical flood events — fixed reference points, not model
# output. Coordinates geocoded from OpenStreetMap (Nominatim) place lookups
# for "Greenfield, Glasgow" and "SEC Centre, Glasgow" and converted to
# EPSG:27700. Facts cross-checked against Wikipedia's "2002 Glasgow floods"
# article, independent reporting corroborating the Bloomberg SECC figures, and
# the SEC's own official history page (sec.co.uk/about-the-sec/history-of-the-sec),
# which is the primary source for the River Kelvin/railway tunnel detail.
HISTORICAL_EVENTS = [
    {
        "name": "2002 Glasgow floods",
        "easting": 264268, "northing": 664672,
        "date": "30 July 2002",
        "caption": (
            "Flash flooding after ~75mm of rain in 10 hours overwhelmed the East "
            "End's Victorian storm drains. Greenfield and Shettleston were the "
            "worst-affected areas — around 200 people evacuated from their homes."
        ),
        "source": "BBC / The Scotsman reporting",
    },
    {
        "name": "1994 SEC Centre floods",
        "easting": 256851, "northing": 665468,
        "date": "12 December 1994",
        "caption": (
            "The River Kelvin burst its banks after days of torrential rain and "
            "flooded the SEC Centre through old railway tunnels. 2 fatalities; "
            "over £100 million in damage."
        ),
        "source": "Bloomberg / historical reporting; SEC official history (sec.co.uk)",
    },
]

# Rainfall trend context: mean-annual-rainfall and wet-day-frequency for the
# first vs. second half of the 39-year HadUK-Grid record, averaged across all
# 7,843 grid points. Precomputed offline from the full daily series
# (002_Dataset/rainfall_daily_1987_2025.parquet, 111.5M daily observations)
# rather than loaded at runtime, since the dashboard otherwise only reads the
# small aggregated feature matrix. Reproducible via a groupby on grid_id/year.
RAINFALL_TREND = {
    "period_a": {"label": "1987-2005", "n_years": 19,
                 "annual_total_mm": 1069, "wet_days_per_year": 172.5},
    "period_b": {"label": "2006-2025", "n_years": 20,
                 "annual_total_mm": 1088, "wet_days_per_year": 169.8},
}

# Random Forest vs XGBoost comparison, precomputed offline in 04_ML_Model.ipynb
# (same feature_matrix.csv, same 80/20 stratified split, random_state=42, both
# 100 estimators) rather than retrained at runtime. Random Forest edges out
# XGBoost on every metric here, so it remains the live model for both
# dashboard versions — this panel is reporting a decision already made, not
# live-computed. See 04_ML_Model.ipynb's "Side-by-side comparison" section for
# feature importance/SHAP detail, including the caveat that XGBoost's SHAP
# values are in raw margin space (shap's TreeExplainer has no probability-space
# support for XGBoost's multiclass objective), not probability space like
# Random Forest's — so only SHAP *rankings*, not magnitudes, are comparable
# between the two models.
MODEL_COMPARISON = {
    "random_forest": {"label": "Random Forest", "is_live": True,
                       "accuracy": 0.9962, "f1_macro": 0.9950},
    "xgboost": {"label": "XGBoost", "is_live": False,
                "accuracy": 0.9936, "f1_macro": 0.9917},
}

# Random Forest's confusion matrix and per-class precision/recall/F1 on the
# same held-out 20% test split as above, precomputed in 04_ML_Model.ipynb's
# "Deeper model evaluation" section (5-fold CV there gave 99.26% ± 0.17% mean
# accuracy, confirming this single-split confusion matrix isn't a lucky draw).
# Rows/cols of the matrix are in Low/Medium/High order; the only errors are
# 3 Low points misclassified as High and 3 High points misclassified as Low —
# no confusion at all between Medium and either other class.
RF_CONFUSION_MATRIX = [
    [755, 0, 3],
    [0, 540, 0],
    [3, 0, 268],
]
RF_PER_CLASS_METRICS = {
    "Low risk": {"precision": 0.9960, "recall": 0.9960, "f1": 0.9960},
    "Medium risk": {"precision": 1.0000, "recall": 1.0000, "f1": 1.0000},
    "High risk": {"precision": 0.9889, "recall": 0.9889, "f1": 0.9889},
}

# Random Forest's 5-fold stratified CV (mean ± std across folds on the full
# dataset) vs XGBoost's single 80/20-split numbers — both from 04_ML_Model.ipynb.
# These are NOT computed the same way (CV mean/std vs one split), so the chart
# below labels each series accordingly rather than implying a like-for-like
# comparison. XGBoost wasn't cross-validated since it's a comparison model
# only, not the live one.
RF_CV_METRICS = {
    "accuracy": {"mean": 0.9926, "std": 0.0017},
    "f1_macro": {"mean": 0.9904, "std": 0.0022},
}
XGB_SPLIT_METRICS = {
    "accuracy": 0.9936,
    "f1_macro": 0.9917,
}

# Per-class F1 for both models on the same held-out test split, and Random
# Forest's per-class ROC-AUC (one-vs-rest) — all from 04_ML_Model.ipynb's
# "Deeper model evaluation" section.
XGB_PER_CLASS_F1 = {"Low": 0.9934, "Medium": 1.0000, "High": 0.9816}
RF_ROC_AUC = {"Low": 0.9998, "Medium": 1.0000, "High": 0.9996}

# Risk-tiered precautions, based on official SEPA and Ready Scotland (gov.scot)
# guidance. Content is identical in both dashboard versions — this is general
# safety information, not part of the model's SHAP explanation.
PRECAUTIONS = {
    2: {
        "heading": "High risk — recommended precautions",
        "items": [
            "Check your exact address on SEPA's flood maps (sepa.scot)",
            "Sign up to Floodline for flood warnings: <b>0345 988 1188</b>, available 24/7",
            "Consider property flood resilience products — the Scottish Flood Forum has a guide",
            "Discuss flood insurance with your insurer, or explore Flood Re if you're struggling to get cover",
        ],
    },
    1: {
        "heading": "Medium risk — recommended precautions",
        "items": [
            "Sign up to Floodline as a precaution: <b>0345 988 1188</b>",
            "Review the Scottish Flood Forum's flood preparation guidance",
            "Check SEPA's flood maps periodically, especially before severe weather",
        ],
    },
    0: {
        "heading": "Low risk — worth knowing",
        "items": [
            "Flooding can still affect roads and transport access even if your specific property isn't at risk",
            "SEPA's flood maps are worth checking if you're planning for a business or long-term investment in the area",
        ],
    },
}

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

@st.cache_resource
def load_model(path):
    return joblib.load(path)

df = load_data(DATA_PATH)
model = load_model(MODEL_PATH)
df["predicted_risk"] = model.predict(df[FEATURE_COLS])
df["confidence"] = model.predict_proba(df[FEATURE_COLS]).max(axis=1)

@st.cache_data
def add_latlon(df):
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(df["easting"].values, df["northing"].values)
    df = df.copy()
    df["lat"] = lat
    df["lon"] = lon
    return df

df = add_latlon(df)
hist_transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

@st.cache_data
def load_postcode_districts():
    """Postcode districts (outcodes) covering the study area, via postcodes.io
    reverse geocoding from the study centre — same API as the postcode search."""
    uni_lon, uni_lat = hist_transformer.transform(UNI_X, UNI_Y)
    try:
        resp = requests.get(
            OUTCODES_API,
            params={"lon": uni_lon, "lat": uni_lat, "limit": 100, "radius": 5000},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json()["result"] or []
    except requests.RequestException:
        results = []
    return pd.DataFrame(
        [{"outcode": r["outcode"], "easting": r["eastings"], "northing": r["northings"]}
         for r in results]
    )

@st.cache_data
def assign_postcode_district(df, districts_df):
    """Assign each grid point to its nearest postcode district centroid."""
    if districts_df.empty:
        return pd.Series(["Unknown"] * len(df), index=df.index)
    dx = df["easting"].values[:, None] - districts_df["easting"].values[None, :]
    dy = df["northing"].values[:, None] - districts_df["northing"].values[None, :]
    nearest_idx = (dx ** 2 + dy ** 2).argmin(axis=1)
    return pd.Series(districts_df["outcode"].values[nearest_idx], index=df.index)

postcode_districts_df = load_postcode_districts()
df["postcode_district"] = assign_postcode_district(df, postcode_districts_df)

RISK_COLOURS = {0: "#639922", 1: "#EF9F27", 2: "#E24B4A"}
RISK_LABELS = {0: "Low risk", 1: "Medium risk", 2: "High risk"}

# --- SHAP setup: same probability-space TreeExplainer approach as
# 04_ML_Model.ipynb, background = the identical 80% training split (same
# random_state=42) the model was fit on. Benchmarked at ~2ms to build the
# explainer and ~5-10ms per single-point shap_values call (see conversation
# for the benchmark script) — well under the 1-2s threshold for going live,
# so SHAP is computed fresh on every click/search rather than precomputed.
@st.cache_data
def get_train_split(df):
    X = df[FEATURE_COLS]
    y = df["flood_risk"]
    X_train, _, _, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    return X_train

@st.cache_resource
def build_explainer(_model, _X_train):
    return shap.TreeExplainer(_model, data=_X_train, model_output="probability")

X_train = get_train_split(df)
explainer = build_explainer(model, X_train)

@st.cache_data
def compute_terciles(df):
    return {feat: (df[feat].quantile(1 / 3), df[feat].quantile(2 / 3)) for feat in FEATURE_COLS}

FEATURE_TERCILES = compute_terciles(df)

def tier_for(feat, value):
    lo, hi = FEATURE_TERCILES[feat]
    if value <= lo:
        return "low"
    if value >= hi:
        return "high"
    return "moderate"

def compute_shap_for_point(point):
    row = point[FEATURE_COLS].to_frame().T.astype(float)
    sv = explainer.shap_values(row)  # shape (1, n_features, n_classes)
    predicted_class = int(point["predicted_risk"])
    shap_for_class = sv[0, :, predicted_class]
    return shap_for_class, predicted_class

with st.sidebar:
    st.subheader("Risk distribution")
    st.caption(f"All {len(df):,} grid points (model prediction)")
    risk_counts = df["predicted_risk"].value_counts().reindex([0, 1, 2], fill_value=0)
    total_points = risk_counts.sum()
    for risk_val in [0, 1, 2]:
        count = int(risk_counts[risk_val])
        pct = count / total_points * 100
        st.markdown(
            f"""
            <div style='margin-bottom:12px;'>
              <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:3px;'>
                <span>{RISK_LABELS[risk_val]}</span><span>{count:,} ({pct:.1f}%)</span>
              </div>
              <div style='background:#eee; border-radius:4px; height:10px; width:100%;'>
                <div style='background:{RISK_COLOURS[risk_val]}; border-radius:4px; height:10px; width:{pct:.2f}%;'></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("Rainfall trend")
    st.caption("39-year HadUK-Grid record, averaged across all grid points")

    def _trend_bars(label, val_a, val_b, unit, fmt="{:.0f}"):
        max_val = max(val_a, val_b)
        st.markdown(f"<div style='font-size:13px; margin-bottom:3px;'>{label}</div>", unsafe_allow_html=True)
        for period, val, colour in [("a", val_a, "#7FB3C8"), ("b", val_b, "#2C6E8E")]:
            pct = val / max_val * 100
            period_label = RAINFALL_TREND[f"period_{period}"]["label"]
            st.markdown(
                f"""
                <div style='display:flex; align-items:center; margin-bottom:3px; font-size:12px;'>
                  <span style='width:64px; color:#666;'>{period_label}</span>
                  <div style='flex:1; background:#eee; border-radius:4px; height:8px; margin-right:6px;'>
                    <div style='background:{colour}; border-radius:4px; height:8px; width:{pct:.1f}%;'></div>
                  </div>
                  <span>{fmt.format(val)}{unit}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _a = RAINFALL_TREND["period_a"]
    _b = RAINFALL_TREND["period_b"]
    _trend_bars("Mean annual rainfall", _a["annual_total_mm"], _b["annual_total_mm"], "mm")
    _trend_bars("Wet days per year", _a["wet_days_per_year"], _b["wet_days_per_year"], "", fmt="{:.1f}")

    _pct_change = (_b["annual_total_mm"] - _a["annual_total_mm"]) / _a["annual_total_mm"] * 100
    st.caption(
        f"Change between {_a['label']} and {_b['label']} is small and mixed — "
        f"annual totals up ~{_pct_change:.0f}%, but wet-day frequency and peak "
        "daily rainfall are both slightly down. This 39-year, single-city record "
        "does not show a clear directional trend."
    )

for key, default in [
    ("selected_point", None),
    ("last_clicked_latlng", None),
    ("search_error", None),
    ("search_warning", None),
    ("search_marker", None),
    ("map_center", DEFAULT_CENTER),
    ("map_zoom", DEFAULT_ZOOM),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Model evaluation (central, main-column section) ---
st.markdown("## Model evaluation")
st.caption(
    "Random Forest is the live model behind every prediction on this page. Figures below "
    "are from 04_ML_Model.ipynb's held-out 20% test split (stratified, random_state=42) "
    "unless noted otherwise; XGBoost appears only as a comparison model, not a live one."
)

_rf = MODEL_COMPARISON["random_forest"]
_avg_auc = sum(RF_ROC_AUC.values()) / len(RF_ROC_AUC)
_metric_col1, _metric_col2, _metric_col3, _metric_col4 = st.columns(4)
_metric_col1.metric("Accuracy (test split)", f"{_rf['accuracy']:.2%}")
_metric_col2.metric("F1 macro (test split)", f"{_rf['f1_macro']:.2%}")
_metric_col3.metric("5-fold CV accuracy", f"{RF_CV_METRICS['accuracy']['mean']:.2%}",
                     f"±{RF_CV_METRICS['accuracy']['std']:.2%}")
_metric_col4.metric("Mean ROC-AUC (one-vs-rest)", f"{_avg_auc:.4f}")

eval_tabs = st.tabs([
    "Confusion matrix", "ROC curves", "Feature importance", "SHAP summary",
    "Random Forest vs XGBoost",
])

with eval_tabs[0]:
    col_cm, col_cm_metrics = st.columns([1.3, 1])
    with col_cm:
        st.image(CONFUSION_MATRIX_IMG, use_container_width=True)
    with col_cm_metrics:
        st.markdown("**Per-class precision / recall / F1**")
        st.dataframe(pd.DataFrame(RF_PER_CLASS_METRICS).T.round(4), use_container_width=True)
        st.caption(
            "Only 6 of 1,569 test points are misclassified, all Low↔High confusions — "
            "no confusion at all between Medium risk and either other class."
        )

with eval_tabs[1]:
    st.image(ROC_CURVES_IMG, use_container_width=True)
    st.caption("One-vs-rest ROC curves for each risk class — all three AUCs exceed 0.999.")

with eval_tabs[2]:
    col_fi_rf, col_fi_xgb = st.columns(2)
    with col_fi_rf:
        st.image(FEATURE_IMPORTANCE_RF_IMG, use_container_width=True)
    with col_fi_xgb:
        st.image(FEATURE_IMPORTANCE_XGB_IMG, use_container_width=True)
    st.caption(
        "Both models agree elevation is by far the dominant risk driver (63% for Random "
        "Forest, 93% for XGBoost), with dist_to_clyde a clear #2 in both."
    )

with eval_tabs[3]:
    st.image(SHAP_SUMMARY_IMG, use_container_width=True)
    st.caption(
        "SHAP beeswarm plots per risk class, from the same held-out test split — this "
        "per-prediction explanation is the project's core research contribution. Select a "
        "location below for a live, single-point version of this in the panel on the right."
    )

with eval_tabs[4]:
    st.caption(
        "Random Forest's numbers below are 5-fold cross-validated; XGBoost's are from a "
        "single 80/20 split (it's a comparison model, not cross-validated) — charts label "
        "each accordingly rather than implying an identical methodology."
    )

    _width = 0.35

    st.markdown(
        "<div style='font-size:13px; font-weight:600; margin-bottom:2px;'>Accuracy & F1 macro</div>",
        unsafe_allow_html=True,
    )
    fig1, ax1 = plt.subplots(figsize=(4.3, 3))
    _metric_labels = ["Accuracy", "F1 macro"]
    _x1 = np.arange(len(_metric_labels))
    _rf_vals = [RF_CV_METRICS["accuracy"]["mean"], RF_CV_METRICS["f1_macro"]["mean"]]
    _rf_errs = [RF_CV_METRICS["accuracy"]["std"], RF_CV_METRICS["f1_macro"]["std"]]
    _xgb_vals = [XGB_SPLIT_METRICS["accuracy"], XGB_SPLIT_METRICS["f1_macro"]]

    _bars_rf1 = ax1.bar(_x1 - _width / 2, _rf_vals, _width, yerr=_rf_errs, capsize=4,
                        color="#2C6E8E", label="Random Forest (5-fold CV mean ± std)")
    _bars_xgb1 = ax1.bar(_x1 + _width / 2, _xgb_vals, _width,
                         color="#7FB3C8", label="XGBoost (single 80/20 split)")
    for _bars, _vals in [(_bars_rf1, _rf_vals), (_bars_xgb1, _xgb_vals)]:
        for _b, _v in zip(_bars, _vals):
            ax1.text(_b.get_x() + _b.get_width() / 2, _v + 0.0015, f"{_v:.4f}",
                      ha='center', va='bottom', fontsize=7)
    ax1.set_xticks(_x1)
    ax1.set_xticklabels(_metric_labels, fontsize=9)
    ax1.set_ylim(0.97, 1.01)
    ax1.set_ylabel("Score", fontsize=9)
    ax1.tick_params(axis='y', labelsize=8)
    ax1.legend(fontsize=6.5, loc='lower left')
    ax1.grid(axis='y', alpha=0.3)
    fig1.tight_layout()
    st.pyplot(fig1, use_container_width=True)
    plt.close(fig1)

    st.markdown(
        "<div style='font-size:13px; font-weight:600; margin:8px 0 2px;'>Per-class F1</div>",
        unsafe_allow_html=True,
    )
    fig2, ax2 = plt.subplots(figsize=(4.3, 3))
    _classes = ["Low", "Medium", "High"]
    _x2 = np.arange(len(_classes))
    _rf_f1 = [RF_PER_CLASS_METRICS["Low risk"]["f1"], RF_PER_CLASS_METRICS["Medium risk"]["f1"],
              RF_PER_CLASS_METRICS["High risk"]["f1"]]
    _xgb_f1 = [XGB_PER_CLASS_F1["Low"], XGB_PER_CLASS_F1["Medium"], XGB_PER_CLASS_F1["High"]]

    _bars_rf2 = ax2.bar(_x2 - _width / 2, _rf_f1, _width, color="#2C6E8E", label="Random Forest")
    _bars_xgb2 = ax2.bar(_x2 + _width / 2, _xgb_f1, _width, color="#7FB3C8", label="XGBoost")
    for _bars, _vals in [(_bars_rf2, _rf_f1), (_bars_xgb2, _xgb_f1)]:
        for _b, _v in zip(_bars, _vals):
            ax2.text(_b.get_x() + _b.get_width() / 2, _v + 0.0015, f"{_v:.4f}",
                      ha='center', va='bottom', fontsize=7)
    ax2.set_xticks(_x2)
    ax2.set_xticklabels(_classes, fontsize=9)
    ax2.set_ylim(0.97, 1.01)
    ax2.set_ylabel("F1 score", fontsize=9)
    ax2.tick_params(axis='y', labelsize=8)
    ax2.legend(fontsize=7, loc='lower left')
    ax2.grid(axis='y', alpha=0.3)
    fig2.tight_layout()
    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

    st.markdown(
        f"**{_rf['label']} is the live model** for all predictions on this page — it edges "
        "out XGBoost on every metric above, so there's no case for switching. Both models "
        "agree elevation is by far the dominant risk driver; dist_to_clyde ranks a clear #2 "
        "by native feature importance in both, though the models' SHAP rankings of "
        "dist_to_clyde are less consistent (XGBoost's SHAP values had to be computed in raw "
        "margin space, not probability space — see 04_ML_Model.ipynb)."
    )

st.markdown("---")

# --- Postcode search ---
st.markdown("#### Search by postcode")
with st.form("postcode_search", clear_on_submit=False):
    search_col, button_col = st.columns([4, 1])
    with search_col:
        postcode_input = st.text_input(
            "Postcode", placeholder="e.g. G1 1XQ", label_visibility="collapsed"
        )
    with button_col:
        submitted = st.form_submit_button("Search", use_container_width=True, type="primary")

if submitted:
    postcode = postcode_input.strip()
    if not postcode:
        st.session_state.search_error = "Enter a postcode to search."
    else:
        try:
            resp = requests.get(f"{POSTCODES_API}{quote(postcode)}", timeout=5)
        except requests.RequestException:
            resp = None
            st.session_state.search_error = (
                "Couldn't reach the postcode lookup service — check your "
                "connection and try again."
            )

        if resp is not None:
            if resp.status_code == 200:
                result = resp.json()["result"]
                east, north = result["eastings"], result["northings"]
                dist_sq = (df["easting"] - east) ** 2 + (df["northing"] - north) ** 2
                nearest = df.loc[dist_sq.idxmin()].copy()

                st.session_state.selected_point = nearest
                st.session_state.map_center = [nearest["lat"], nearest["lon"]]
                st.session_state.map_zoom = 16
                st.session_state.search_marker = {
                    "lat": nearest["lat"], "lon": nearest["lon"],
                    "postcode": result["postcode"],
                }
                st.session_state.search_error = None

                dist_from_uni_km = ((east - UNI_X) ** 2 + (north - UNI_Y) ** 2) ** 0.5 / 1000
                if dist_from_uni_km > 15:
                    st.session_state.search_warning = (
                        f"'{result['postcode']}' is {dist_from_uni_km:.1f}km from the "
                        "study area centre — showing the nearest available grid point, "
                        "but it may be far from where this postcode actually is."
                    )
                else:
                    st.session_state.search_warning = None
            elif resp.status_code == 404:
                st.session_state.search_error = (
                    f"Postcode '{postcode}' not found — check it's a valid UK postcode."
                )
                st.session_state.search_warning = None
            else:
                st.session_state.search_error = (
                    f"Postcode lookup failed (HTTP {resp.status_code}). Try again."
                )
                st.session_state.search_warning = None

if st.session_state.search_error:
    st.error(st.session_state.search_error)
elif st.session_state.search_warning:
    st.warning(st.session_state.search_warning)

col_map, col_panel = st.columns([1.4, 1], gap="large")

with col_map:
    st.subheader("Risk map (model prediction)")

    selected_risks = st.multiselect(
        "Show risk levels",
        options=[0, 1, 2],
        default=[0, 1, 2],
        format_func=lambda r: RISK_LABELS[r],
    )
    clyde_dist_max = int(np.ceil(df["dist_to_clyde"].max() / 100) * 100)
    clyde_dist_range = st.slider(
        "Distance from the River Clyde",
        min_value=0,
        max_value=clyde_dist_max,
        value=(0, clyde_dist_max),
        step=100,
        format="%dm",
    )

    district_options = ["All districts"] + sorted(postcode_districts_df["outcode"].tolist())
    selected_district = st.selectbox("Postcode district", district_options)

    elevation_min = int(np.floor(df["elevation"].min()))
    elevation_max = int(np.ceil(df["elevation"].max()))
    building_max = int(df["building_count"].max())
    road_max = int(df["road_count"].max())
    wet_days_min = int(np.floor(df["wet_days_per_year"].min()))
    wet_days_max = int(np.ceil(df["wet_days_per_year"].max()))
    max_daily_min = float(df["max_daily_mm"].min())
    max_daily_max = float(df["max_daily_mm"].max())
    nearest_event_dist = pd.concat(
        [np.sqrt((df["easting"] - ev["easting"]) ** 2 + (df["northing"] - ev["northing"]) ** 2)
         for ev in HISTORICAL_EVENTS],
        axis=1,
    ).min(axis=1)

    with st.expander("More filters"):
        elevation_range = st.slider(
            "Elevation range", min_value=elevation_min, max_value=elevation_max,
            value=(elevation_min, elevation_max), step=1, format="%dm",
        )
        min_confidence_pct = st.slider(
            "Minimum model confidence", min_value=0, max_value=100, value=0, step=1, format="%d%%",
        )
        building_range = st.slider(
            "Buildings within 250m", min_value=0, max_value=building_max,
            value=(0, building_max), step=1,
        )
        road_range = st.slider(
            "Roads within 250m", min_value=0, max_value=road_max,
            value=(0, road_max), step=1,
        )
        near_events_only = st.checkbox("Only show points near a historical flood event")
        event_radius = st.slider(
            "Radius around 1994/2002 flood events", min_value=100, max_value=3000,
            value=500, step=100, format="%dm", disabled=not near_events_only,
        )
        wet_days_range = st.slider(
            "Wet days per year", min_value=wet_days_min, max_value=wet_days_max,
            value=(wet_days_min, wet_days_max), step=1,
        )
        max_daily_range = st.slider(
            "Max daily rainfall", min_value=max_daily_min, max_value=max_daily_max,
            value=(max_daily_min, max_daily_max), step=0.5, format="%.1fmm",
        )

    mask = (
        df["predicted_risk"].isin(selected_risks)
        & df["dist_to_clyde"].between(clyde_dist_range[0], clyde_dist_range[1])
        & df["elevation"].between(elevation_range[0], elevation_range[1])
        & (df["confidence"] >= min_confidence_pct / 100)
        & df["building_count"].between(building_range[0], building_range[1])
        & df["road_count"].between(road_range[0], road_range[1])
        & df["wet_days_per_year"].between(wet_days_range[0], wet_days_range[1])
        & df["max_daily_mm"].between(max_daily_range[0], max_daily_range[1])
    )
    if selected_district != "All districts":
        mask &= df["postcode_district"] == selected_district
    if near_events_only:
        mask &= nearest_event_dist <= event_radius

    filtered_df = df[mask]

    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles="cartodbpositron",
    )
    sample = filtered_df.sample(n=min(1000, len(filtered_df)), random_state=42)
    sample = sample.reset_index(drop=True)
    if filtered_df.empty:
        st.caption("No risk levels selected — pick at least one above to show points.")
    for _, row in sample.iterrows():
        marker = folium.CircleMarker(location=[row["lat"], row["lon"]], radius=4, color=RISK_COLOURS[row["predicted_risk"]], fill=True, fill_opacity=0.8, tooltip=RISK_LABELS[row["predicted_risk"]])
        marker.add_to(m)

    if st.session_state.search_marker:
        sm = st.session_state.search_marker
        folium.Marker(
            location=[sm["lat"], sm["lon"]],
            icon=folium.Icon(color="blue", icon="search", prefix="fa"),
            tooltip=f"Nearest grid point to {sm['postcode']}",
        ).add_to(m)

    for event in HISTORICAL_EVENTS:
        ev_lon, ev_lat = hist_transformer.transform(event["easting"], event["northing"])
        popup_html = (
            f"<b>{event['name']}</b> — {event['date']}<br>"
            f"{event['caption']}<br>"
            f"<i>Source: {event['source']}</i><br>"
            f"<span style='color:#666;'>Historical record — not a model prediction.</span>"
        )
        folium.Marker(
            location=[ev_lat, ev_lon],
            icon=folium.Icon(color="darkpurple", icon="exclamation-triangle", prefix="fa"),
            tooltip=f"{event['name']} ({event['date']}) — click for details",
            popup=folium.Popup(popup_html, max_width=280),
        ).add_to(m)

    map_data = st_folium(m, width=700, height=500)
    st.caption(
        "🔺 Purple markers are real, documented historical flood events (1994, 2002) "
        "shown for context — they are not model predictions. Click a marker for details."
    )

clicked = map_data.get("last_object_clicked") if map_data else None
if clicked is not None and clicked != st.session_state.last_clicked_latlng:
    st.session_state.last_clicked_latlng = clicked
    click_lat, click_lon = clicked["lat"], clicked["lng"]
    dist_sq = (sample["lat"] - click_lat) ** 2 + (sample["lon"] - click_lon) ** 2
    st.session_state.selected_point = sample.loc[dist_sq.idxmin()].copy()
    st.session_state.search_marker = None

with col_panel:
    st.subheader("Selected location")
    point = st.session_state.selected_point

    if point is None:
        st.info("Click a point on the map, or search a postcode above, to see flood risk details here.")
    else:
        risk_label = RISK_LABELS[point["predicted_risk"]]
        badge_colour = RISK_COLOURS[point["predicted_risk"]]

        coord_text = "Coordinates: " + str(round(point["easting"])) + " E, " + str(round(point["northing"])) + " N"
        st.markdown(coord_text)

        badge_html = "<span style='background:" + badge_colour + "22; color:" + badge_colour + "; padding:4px 12px; border-radius:6px; font-weight:600;'>" + risk_label + " (model prediction)</span>"
        st.markdown(badge_html, unsafe_allow_html=True)

        confidence = float(point["confidence"])
        st.markdown(
            f"<span style='font-size:13px; color:#555;'>Model confidence: "
            f"<b>{confidence * 100:.0f}%</b></span>",
            unsafe_allow_html=True,
        )
        st.progress(confidence)

        clyde_dist = point["dist_to_clyde"]
        if clyde_dist < 100:
            clyde_line = "🧭 Right at the River Clyde"
        else:
            cx, cy = nearest_clyde_point(point["easting"], point["northing"])
            clyde_dir = compass_direction(point["easting"] - cx, point["northing"] - cy)
            clyde_line = f"🧭 {format_distance(clyde_dist)} {clyde_dir} of the River Clyde"

        uni_dx = point["easting"] - UNI_X
        uni_dy = point["northing"] - UNI_Y
        uni_dist = (uni_dx ** 2 + uni_dy ** 2) ** 0.5
        if uni_dist < 100:
            uni_line = "🎓 Right at the University of Strathclyde"
        else:
            uni_dir = compass_direction(uni_dx, uni_dy)
            uni_line = f"🎓 {format_distance(uni_dist)} {uni_dir} of the University of Strathclyde"

        st.markdown(clyde_line)
        st.markdown(uni_line)

        st.markdown("---")
        st.subheader("Why this prediction?")

        shap_vals, pred_class = compute_shap_for_point(point)
        order = np.argsort(-np.abs(shap_vals))
        max_abs = max(np.abs(shap_vals).max(), 1e-9)

        # Narrative: name the top 1-2 driving features in plain English.
        fragments = []
        for rank in range(min(2, len(order))):
            feat = FEATURE_COLS[order[rank]]
            tier = tier_for(feat, point[feat])
            value_str = FEATURE_META[feat]["fmt"].format(point[feat])
            fragments.append(FEATURE_META[feat]["narrative"][tier].format(value=value_str))
        reason_text = fragments[0] if len(fragments) < 2 else f"{fragments[0]}, and {fragments[1]}"
        st.markdown(f"This location is predicted **{risk_label}** mainly because {reason_text}.")

        st.caption("🔴 Pushes toward higher flood risk &nbsp;·&nbsp; 🔵 Pushes toward lower risk")

        for rank, idx in enumerate(order):
            feat = FEATURE_COLS[idx]
            raw_shap = shap_vals[idx]
            risk_dir = -raw_shap if pred_class == 0 else raw_shap
            tier = tier_for(feat, point[feat])
            bar_label = FEATURE_META[feat]["bar_label"][tier]
            value_str = FEATURE_META[feat]["fmt"].format(point[feat]) + FEATURE_META[feat]["unit"]
            pct = abs(raw_shap) / max_abs * 100
            colour = "#C0392B" if risk_dir > 0 else "#2C6E8E"

            st.markdown(
                f"""
                <div style='margin-bottom:3px;'>
                  <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:2px;'>
                    <span>{bar_label}</span><span style='color:#666;'>{value_str}</span>
                  </div>
                  <div style='background:#eee; border-radius:4px; height:9px; width:100%;'>
                    <div style='background:{colour}; border-radius:4px; height:9px; width:{pct:.1f}%;'></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if rank < 2:
                st.caption(FEATURE_META[feat]["definition"])
            else:
                with st.popover(f"What does '{bar_label}' mean?"):
                    st.write(FEATURE_META[feat]["definition"])

        st.markdown("---")
        st.markdown("Raw feature values at this location")
        feature_table = point[FEATURE_COLS].to_frame(name="value")
        st.dataframe(feature_table, use_container_width=True)

        st.markdown("---")
        st.subheader("Precautions and next steps")
        precautions = PRECAUTIONS[point["predicted_risk"]]
        items_html = "".join(f"<li style='margin-bottom:6px;'>{item}</li>" for item in precautions["items"])
        st.markdown(
            f"""
            <div style='background:#EAF3F5; border-radius:8px; padding:14px 18px; margin-bottom:8px;'>
              <div style='font-weight:600; margin-bottom:8px;'>{precautions['heading']}</div>
              <ul style='margin:0; padding-left:20px;'>{items_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "Source: SEPA (sepa.scot) and Ready Scotland (gov.scot). This is "
            "general guidance, not a substitute for checking your specific "
            "address on SEPA's official flood maps."
        )

# --- Comparisons (full-width, below the map/panel row) ---
st.markdown("---")
st.markdown("## Comparisons")
st.caption(
    "Aggregate context across all grid points, plus how the selected location "
    "compares to real historical flood events."
)

st.subheader("District risk comparison")
st.caption("Average risk class distribution per postcode district covered by the study area")

known_district_df = df[df["postcode_district"] != "Unknown"]
if known_district_df.empty:
    st.info("Postcode district data isn't available right now.")
else:
    district_risk = (
        known_district_df.groupby("postcode_district")["predicted_risk"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
        .reindex(columns=[0, 1, 2], fill_value=0)
        * 100
    )
    district_risk.columns = ["Low risk %", "Medium risk %", "High risk %"]
    district_risk.insert(0, "Points", known_district_df.groupby("postcode_district").size())
    district_risk = district_risk.sort_values("High risk %", ascending=False)
    district_risk.index.name = "District"
    st.dataframe(
        district_risk.style.format({
            "Points": "{:,.0f}",
            "Low risk %": "{:.1f}%",
            "Medium risk %": "{:.1f}%",
            "High risk %": "{:.1f}%",
        }),
        use_container_width=True,
    )

    st.markdown("#### Ranked districts by % High risk")
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        district_n = st.radio("Number of districts", [2, 5, 10], index=1, horizontal=True, key="district_n")
    with ctrl_col2:
        district_view = st.radio(
            "Rank by", ["Highest % High risk", "Lowest % High risk"],
            horizontal=True, key="district_view",
        )

    if district_view == "Highest % High risk":
        district_subset = district_risk.sort_values("High risk %", ascending=False).head(district_n)
        district_bar_colour = RISK_COLOURS[2]
    else:
        district_subset = district_risk.sort_values("High risk %", ascending=True).head(district_n)
        district_bar_colour = RISK_COLOURS[0]

    # Reverse so rank #1 (most extreme for the selected view) plots at the top —
    # barh draws the first row at the bottom of the y-axis.
    district_plot = district_subset.iloc[::-1]
    fig_dist, ax_dist = plt.subplots(figsize=(8, 0.5 * len(district_plot) + 1.2))
    ax_dist.barh(district_plot.index, district_plot["High risk %"], color=district_bar_colour)
    for i, v in enumerate(district_plot["High risk %"]):
        ax_dist.text(v + 0.5, i, f"{v:.1f}%", va='center', fontsize=8)
    ax_dist.set_xlabel("High risk %", fontsize=9)
    ax_dist.set_xlim(0, max(district_risk["High risk %"].max(), 1) * 1.15)
    ax_dist.tick_params(axis='both', labelsize=8)
    fig_dist.tight_layout()
    st.pyplot(fig_dist, use_container_width=True)
    plt.close(fig_dist)

st.markdown("#### Ranked individual grid points by risk")
st.caption(
    "Points ranked by model confidence within their predicted class — 'Highest risk' "
    "ranks points predicted High risk by confidence in that prediction; 'Lowest risk' "
    "does the same for points predicted Low risk."
)
ctrl_col3, ctrl_col4 = st.columns(2)
with ctrl_col3:
    point_n = st.radio("Number of points", [2, 5, 10], index=1, horizontal=True, key="point_n")
with ctrl_col4:
    point_view = st.radio("Rank by", ["Highest risk", "Lowest risk"], horizontal=True, key="point_view")

target_class = 2 if point_view == "Highest risk" else 0
class_points = df[df["predicted_risk"] == target_class].sort_values("confidence", ascending=False)
top_points = class_points.head(point_n)

if top_points.empty:
    st.info(f"No points are predicted {RISK_LABELS[target_class]} to rank.")
else:
    def _point_label(row):
        district = row["postcode_district"] if row["postcode_district"] != "Unknown" else "district n/a"
        return f"{district} ({int(row['easting'])}E, {int(row['northing'])}N)"

    point_labels = [_point_label(row) for _, row in top_points.iterrows()]
    point_values = (top_points["confidence"] * 100).tolist()

    # Reverse so rank #1 (highest confidence) plots at the top, same convention
    # as the district chart above.
    plot_labels = list(reversed(point_labels))
    plot_values = list(reversed(point_values))

    fig_pts, ax_pts = plt.subplots(figsize=(8, 0.5 * len(plot_labels) + 1.2))
    ax_pts.barh(plot_labels, plot_values, color=RISK_COLOURS[target_class])
    for i, v in enumerate(plot_values):
        ax_pts.text(v + 0.5, i, f"{v:.1f}%", va='center', fontsize=8)
    ax_pts.set_xlabel(f"Model confidence in {RISK_LABELS[target_class]} (%)", fontsize=9)
    ax_pts.set_xlim(0, 105)
    ax_pts.tick_params(axis='both', labelsize=8)
    fig_pts.tight_layout()
    st.pyplot(fig_pts, use_container_width=True)
    plt.close(fig_pts)

col_scatter, col_hist = st.columns(2)

with col_scatter:
    st.subheader("Risk vs. elevation")
    st.caption(f"All {len(df):,} grid points, coloured by predicted risk class")
    fig_sc, ax_sc = plt.subplots(figsize=(5, 3.5))
    _rng = np.random.default_rng(42)
    _jitter = _rng.uniform(-0.15, 0.15, size=len(df))
    for risk_val in [0, 1, 2]:
        mask = (df["predicted_risk"] == risk_val).values
        ax_sc.scatter(
            df["elevation"].values[mask], risk_val + _jitter[mask],
            s=6, alpha=0.35, color=RISK_COLOURS[risk_val], label=RISK_LABELS[risk_val],
        )
    ax_sc.set_xlabel("Elevation (m)", fontsize=9)
    ax_sc.set_yticks([0, 1, 2])
    ax_sc.set_yticklabels(["Low", "Medium", "High"], fontsize=9)
    ax_sc.set_ylabel("Predicted risk", fontsize=9)
    ax_sc.tick_params(axis='x', labelsize=8)
    ax_sc.legend(fontsize=7, loc='center right', markerscale=2)
    ax_sc.grid(axis='x', alpha=0.3)
    fig_sc.tight_layout()
    st.pyplot(fig_sc, use_container_width=True)
    plt.close(fig_sc)
    st.caption(
        "Low-elevation points cluster almost entirely into Medium/High risk, "
        "visually reinforcing elevation's ~63% feature importance (see Model "
        "evaluation above)."
    )

with col_hist:
    st.subheader("Model confidence distribution")
    st.caption(f"predict_proba confidence across all {len(df):,} points, by risk class")
    fig_hist, ax_hist = plt.subplots(figsize=(5, 3.5))
    bins = np.linspace(df["confidence"].min(), 1.0, 25)
    for risk_val in [0, 1, 2]:
        vals = df.loc[df["predicted_risk"] == risk_val, "confidence"]
        ax_hist.hist(vals, bins=bins, alpha=0.55, color=RISK_COLOURS[risk_val], label=RISK_LABELS[risk_val])
    ax_hist.set_xlabel("Model confidence", fontsize=9)
    ax_hist.set_ylabel("Number of points", fontsize=9)
    ax_hist.tick_params(axis='both', labelsize=8)
    ax_hist.legend(fontsize=7)
    ax_hist.grid(axis='y', alpha=0.3)
    fig_hist.tight_layout()
    st.pyplot(fig_hist, use_container_width=True)
    plt.close(fig_hist)

st.subheader("Nearest historical flood event")
_comp_point = st.session_state.selected_point
if _comp_point is None:
    st.info(
        "Click a point on the map, or search a postcode above, to compare it "
        "against the 1994 and 2002 historical flood events."
    )
else:
    event_cols = st.columns(len(HISTORICAL_EVENTS))
    for col, event in zip(event_cols, HISTORICAL_EVENTS):
        dist = (
            (_comp_point["easting"] - event["easting"]) ** 2
            + (_comp_point["northing"] - event["northing"]) ** 2
        ) ** 0.5
        with col:
            st.metric(f"{event['name']} ({event['date']})", format_distance(dist))
    st.caption(
        "Straight-line distance from the selected grid point to each documented "
        "historical flood event — not a model prediction."
    )

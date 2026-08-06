"""
Version B — the SHAP-explained variant of the CARE dashboard usability study.

Renamed from care_dashboard_step4.py: this and care_dashboard_versionA.py are
the two final study versions (not sequential build steps — see step1.py/
step3.py for the build history that led here).

Shares every feature with Version A (postcode search, compass indicator,
risk histogram, historical flood markers, classification confidence, rainfall trend,
visual theme), plus two things Version A doesn't have:

1. A "Model evaluation" tab — top-line Random Forest metrics (accuracy, F1
   macro, 5-fold CV accuracy, mean ROC-AUC, per-class F1) as st.metric cards,
   a small confusion-matrix table, and three expanders for secondary detail
   (feature importance RF vs XGBoost, the SHAP summary beeswarm, and a full
   RF vs XGBoost comparison table). Deliberately metric-card-first rather
   than chart-first: the standalone ROC-curve plot and the RF-vs-XGBoost bar
   charts from an earlier iteration were dropped in favour of compact
   numeric tables, since the mean ROC-AUC and per-model metrics already
   convey the same information at a glance without a chart-heavy page.
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

Layout: everything below the postcode search box sits inside four
st.tabs() — Overview (map + filters + at-a-glance selected-location panel),
Why this prediction? (the SHAP panel above, kept as its own tab so it isn't
buried under comparisons/evaluation content), Comparisons (district/landmark/
point rankings and distribution charts, mostly behind expanders so the
default view is just the nearest-historical-event card), and Model
evaluation (above). This replaced an earlier single-column, all-stacked
layout — same content, but tabbed and expander-collapsed so a first view
doesn't require scrolling past every section to reach what's relevant.

The Overview tab's selected-location panel also carries five compact
st.metric "more about this location" cards below the badge/confidence/
compass block: elevation framed against the citywide distribution, this
point's risk class as a % share of all 7,843 points, live distance to the
nearest SEPA PVA zone (geopandas, computed on the fly against the same
7-zone Glasgow subset used for the flood_risk label — cheap, since it's
just 7 polygons), and two static-ish cards (data-vintage note; winter vs.
annual rainfall) computed from the loaded feature matrix rather than
hardcoded. This is the final planned addition to the Overview tab — further
location-specific detail belongs in Why this prediction? or Comparisons,
not here, to keep this panel from creeping back into a full page.
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
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from sklearn.model_selection import train_test_split
from streamlit_folium import st_folium
from pyproj import Transformer
from shapely.geometry import Point

st.set_page_config(page_title="CARE Dashboard", layout="wide")

# --- Theme: Version B carries its own light/dark toggle (session_state,
# default dark), independent of the shared .streamlit/config.toml — that file
# stays on its original light values so care_dashboard_versionA.py (no
# toggle, always light) is completely unaffected regardless of how either
# script is launched. Everything theme-dependent in this file reads DARK_MODE
# or THEME below rather than the config.toml base theme.
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
DARK_MODE = st.session_state.dark_mode

if DARK_MODE:
    THEME = dict(
        bg_track="rgba(255,255,255,0.14)",
        trend_label="#9BA7B4",
        confidence_text="#9BA7B4",
        why_bg="linear-gradient(135deg, #163A42, #0F262C)",
        why_border="#4FB3C9",
        why_h2="#EAF6F8",
        why_p1="#E6EDF3",
        why_p2="#9BC6CF",
        precautions_bg="#161B22",
        chart_dark=True,
        chart_text="#E6EDF3",
        chart_highlight="#4FB3C9",
    )
else:
    THEME = dict(
        bg_track="#eee",
        trend_label="#666",
        confidence_text="#555",
        why_bg="linear-gradient(135deg, #EAF3F5, #D9EBEF)",
        why_border="#1E7A8C",
        why_h2="#123E49",
        why_p1="#222",
        why_p2="#5A6B70",
        precautions_bg="#EAF3F5",
        chart_dark=False,
        chart_text="#333333",
        chart_highlight="#123E49",
    )

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        hr { margin: 1.2rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

if DARK_MODE:
    st.markdown(
        """
        <style>
        /* --- Dark theme override, scoped to this script only (config.toml
           stays light for Version A) --- */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0E1117;
            color: #E6EDF3;
        }
        [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
        [data-testid="stSidebar"] {
            background-color: #131720;
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        [data-testid="stSidebar"] * { color: #E6EDF3; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12); }

        .stApp hr { border-color: rgba(255,255,255,0.14); }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp span, .stApp label, .stApp li { color: #E6EDF3; }

        /* Captions */
        [data-testid="stCaptionContainer"], .stCaption { color: #9BA7B4 !important; }

        /* Buttons */
        [data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
            background-color: #1E7A8C;
            color: #FFFFFF;
            border: 1px solid rgba(255,255,255,0.1);
        }
        [data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
            background-color: #2C93A8;
            border-color: #4FB3C9;
            color: #FFFFFF;
        }

        /* Text inputs / selects */
        [data-testid="stTextInput"] input,
        [data-baseweb="select"] > div,
        [data-baseweb="base-input"] {
            background-color: #161B22 !important;
            color: #E6EDF3 !important;
            border-color: rgba(255,255,255,0.14) !important;
        }
        [data-baseweb="popover"], [data-baseweb="menu"] {
            background-color: #161B22 !important;
        }
        [data-baseweb="tag"] { background-color: #1E7A8C !important; }

        /* Sliders */
        [data-testid="stSlider"] [data-baseweb="slider"] > div:first-child {
            background: rgba(255,255,255,0.14) !important;
        }

        /* Checkbox / radio labels already covered by .stApp label rule */

        /* Expanders */
        [data-testid="stExpander"] {
            background-color: #161B22;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        [data-testid="stExpander"] summary { color: #E6EDF3; }

        /* Tabs */
        [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid rgba(255,255,255,0.12); }
        [data-baseweb="tab"] { color: #9BA7B4; }
        [data-baseweb="tab"] p { color: inherit; }
        [aria-selected="true"][data-baseweb="tab"] { color: #4FB3C9 !important; }
        [data-baseweb="tab-highlight"] { background-color: #4FB3C9 !important; }

        /* Metrics — bolder, larger stat cards */
        [data-testid="stMetric"] {
            background: linear-gradient(160deg, #1B222C 0%, #131822 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 18px 20px 16px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        }
        [data-testid="stMetricLabel"] {
            color: #9BA7B4 !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em;
        }
        [data-testid="stMetricValue"] {
            color: #F4FAFB !important;
            font-size: 1.95rem !important;
            font-weight: 800 !important;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            line-height: 1.2 !important;
        }
        [data-testid="stMetricValue"] > div {
            white-space: normal !important;
            overflow-wrap: break-word !important;
        }

        /* Alerts */
        [data-testid="stAlert"] { color: #0E1117; }

        /* Progress bar track */
        [data-testid="stProgress"] > div > div { background-color: rgba(255,255,255,0.14); }

        /* st.dataframe and st.image render light-baked content (canvas grid /
           precomputed PNGs) that can't be recoloured via CSS — frame them as
           deliberate light cards instead of letting them float unbounded. */
        [data-testid="stDataFrame"] {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 6px;
        }
        [data-testid="stImage"] {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
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
SEPA_PVA_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/001_SEPA/GeoPackage/Data/PVAv2.gpkg"
POSTCODES_API = "https://api.postcodes.io/postcodes/"
OUTCODES_API = "https://api.postcodes.io/outcodes"

MAPS_DIR = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps"
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

def nearest_point(df, easting, northing):
    dist_sq = (df["easting"] - easting) ** 2 + (df["northing"] - northing) ** 2
    return df.loc[dist_sq.idxmin()].copy()

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

# Well-known Glasgow landmarks for the "jump to a landmark" browser and
# comparison chart — recognisable place names as an alternative to postcode
# search/districts. Coordinates geocoded via OpenStreetMap Nominatim (place
# name + ", Glasgow, UK", first result) and converted from EPSG:4326 to
# EPSG:27700 with pyproj, the same pipeline used for CLYDE_REF_POINTS and
# HISTORICAL_EVENTS above. Ibrox and Partick sit ~5.5km from the study
# centre, just outside the 5km grid radius — their nearest grid point is
# flagged as an edge-of-area approximation in the browse UI below.
LANDMARKS = [
    {"name": "George Square", "easting": 259264, "northing": 665398},
    {"name": "Kelvingrove Park", "easting": 256974, "northing": 666375},
    {"name": "Merchant City", "easting": 259501, "northing": 665164},
    {"name": "Glasgow Cathedral", "easting": 260247, "northing": 665573},
    {"name": "SEC (Scottish Event Campus)", "easting": 256897, "northing": 665427},
    {"name": "Glasgow Green", "easting": 260204, "northing": 663871},
    {"name": "Buchanan Street", "easting": 259069, "northing": 665544},
    {"name": "Ibrox", "easting": 255537, "northing": 664627},
    {"name": "Partick", "easting": 255641, "northing": 666668},
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

# 2026 year-to-date rainfall: Jan-Jul 2026 (Met Office's provisional,
# near-real-time HadUK-Grid feed — 002_Dataset/007_Rainfall_2026_Provisional/,
# distinct from the finalized CEDA v1.3.2.ceda archive the 1987-2025 data
# above comes from) against the SAME Jan-Jul calendar window in each prior
# year, not full annual figures, so a 7-month partial year is never compared
# against 12-month ones. The 1987-2025 baseline excludes 2020, whose source
# archive is missing all of July 2020 (a pre-existing gap, unrelated to the
# 2026 extraction) — 38 of 39 years contribute. Precomputed offline from
# rainfall_daily_2026_ytd.parquet and rainfall_daily_1987_2025.parquet
# (003_Code/archive/08_rainfall_extraction_2026_ytd.py), averaged across all
# 7,843 grid points, WET_THRESHOLD_MM=1.0 matching 02_EDA.ipynb.
RAINFALL_YTD_2026 = {
    "label": "2026 YTD (Jan-Jul)",
    "total_mm": 458.3,
    "wet_days": 99.1,
    "hist_avg_total_mm": 559.3,
    "hist_avg_wet_days": 94.5,
    "hist_n_years": 38,
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

@st.cache_data
def load_pva_zones(path, centre_x, centre_y, radius=5000):
    """SEPA Potentially Vulnerable Area zones intersecting the study circle —
    same source and filter as 03_Feature_Engineering.ipynb's flood-risk label
    (Section 3.2.2/3.3.4), loaded independently here since PVA *geometry*
    isn't itself in the feature matrix, only PVA *membership* (baked into
    flood_risk) is."""
    pva = gpd.read_file(path)
    centre = Point(centre_x, centre_y)
    return pva[pva.geometry.intersects(centre.buffer(radius))].copy()

pva_zones = load_pva_zones(SEPA_PVA_PATH, UNI_X, UNI_Y)

def nearest_pva_zone(easting, northing):
    """Distance (0 if inside) and name of the nearest SEPA PVA zone. Only 7
    zones survive the study-circle filter above, so an exact per-click
    shapely distance is effectively instant — no precomputation needed."""
    dists = pva_zones.geometry.distance(Point(easting, northing))
    idx = dists.idxmin()
    return float(dists.loc[idx]), str(pva_zones.loc[idx, "PVA_Name"])

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

def style_dark_chart(fig, *axes):
    """Recolour a matplotlib figure/axes for the dark theme so charts sit
    naturally inside the dark app shell instead of floating as a white
    rectangle. No-op in light mode, where matplotlib's normal styling
    already matches the page."""
    if not THEME["chart_dark"]:
        return
    fig.patch.set_facecolor("#131822")
    for ax in axes:
        ax.set_facecolor("#131822")
        ax.tick_params(colors="#C7D1DA")
        ax.xaxis.label.set_color("#E6EDF3")
        ax.yaxis.label.set_color("#E6EDF3")
        ax.title.set_color("#E6EDF3")
        for spine in ax.spines.values():
            spine.set_color("#3A4048")
        ax.grid(color="#3A4048")
        legend = ax.get_legend()
        if legend is not None:
            legend.get_frame().set_facecolor("#1B222C")
            legend.get_frame().set_edgecolor("#3A4048")
            for text in legend.get_texts():
                text.set_color("#E6EDF3")

with st.sidebar:
    st.toggle("🌙 Dark mode", key="dark_mode", help="Switch between dark and light theme")
    st.markdown("---")

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
              <div style='background:{THEME["bg_track"]}; border-radius:4px; height:10px; width:100%;'>
                <div style='background:{RISK_COLOURS[risk_val]}; border-radius:4px; height:10px; width:{pct:.2f}%;'></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("Rainfall trend")
    st.caption("39-year HadUK-Grid record, averaged across all grid points")

    def _trend_bars(title, bars, unit, fmt="{:.0f}"):
        # bars: list of (label, value, colour) — generalised from the original
        # fixed pair so the 2026 YTD row below can reuse it too.
        max_val = max(val for _, val, _ in bars)
        st.markdown(f"<div style='font-size:13px; margin-bottom:3px;'>{title}</div>", unsafe_allow_html=True)
        for label, val, colour in bars:
            pct = val / max_val * 100
            st.markdown(
                f"""
                <div style='display:flex; align-items:center; margin-bottom:3px; font-size:12px;'>
                  <span style='width:64px; color:{THEME["trend_label"]};'>{label}</span>
                  <div style='flex:1; background:{THEME["bg_track"]}; border-radius:4px; height:8px; margin-right:6px;'>
                    <div style='background:{colour}; border-radius:4px; height:8px; width:{pct:.1f}%;'></div>
                  </div>
                  <span>{fmt.format(val)}{unit}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _a = RAINFALL_TREND["period_a"]
    _b = RAINFALL_TREND["period_b"]
    _trend_bars(
        "Mean annual rainfall",
        [(_a["label"], _a["annual_total_mm"], "#7FB3C8"), (_b["label"], _b["annual_total_mm"], "#2C6E8E")],
        "mm",
    )
    _trend_bars(
        "Wet days per year",
        [(_a["label"], _a["wet_days_per_year"], "#7FB3C8"), (_b["label"], _b["wet_days_per_year"], "#2C6E8E")],
        "", fmt="{:.1f}",
    )

    _pct_change = (_b["annual_total_mm"] - _a["annual_total_mm"]) / _a["annual_total_mm"] * 100
    st.caption(
        f"Change between {_a['label']} and {_b['label']} is small and mixed — "
        f"annual totals up ~{_pct_change:.0f}%, but wet-day frequency and peak "
        "daily rainfall are both slightly down. This 39-year, single-city record "
        "does not show a clear directional trend."
    )

    # 2026 year-to-date — a separate comparison, deliberately not scaled
    # against the full-year bars above: it's Jan-Jul 2026 against the SAME
    # Jan-Jul window averaged across the 38 comparable prior years (see
    # RAINFALL_YTD_2026), so a 7-month partial year is never held up next to
    # 12-month figures.
    _ytd = RAINFALL_YTD_2026
    _trend_bars(
        f"{_ytd['label']} rainfall",
        [("Hist. avg", _ytd["hist_avg_total_mm"], "#7FB3C8"), ("2026", _ytd["total_mm"], "#2C6E8E")],
        "mm",
    )
    _ytd_pct = (_ytd["total_mm"] - _ytd["hist_avg_total_mm"]) / _ytd["hist_avg_total_mm"] * 100
    st.caption(
        f"2026 is running ~{abs(_ytd_pct):.0f}% drier than the {_ytd['hist_n_years']}-year "
        f"Jan-Jul average so far ({_ytd['total_mm']:.1f}mm vs {_ytd['hist_avg_total_mm']:.1f}mm), "
        f"but with more frequent, lighter rainfall days than typical ({_ytd['wet_days']:.1f} vs "
        f"{_ytd['hist_avg_wet_days']:.1f} wet days). Provisional Met Office data, not yet part "
        "of the finalized archive."
    )

    st.markdown("---")
    with st.expander("ℹ️ About this dashboard"):
        st.markdown(
            "**CARE** (Climate Awareness and Risk Evaluation) classifies flood "
            "risk across a 5km radius around the University of Strathclyde, "
            "Glasgow, using a Random Forest model trained on "
            f"{len(df):,} grid points to reconstruct a rule-based risk label "
            "built from elevation and SEPA flood-vulnerability (PVA) zone "
            "membership — see the **Model evaluation** tab for what its high "
            "accuracy figures do and don't demonstrate.\n\n"
            "**Data sources:**\n"
            "- SEPA Potentially Vulnerable Areas (flood boundaries)\n"
            "- OpenStreetMap (buildings, roads, water)\n"
            "- NASA SRTM (elevation)\n"
            "- Met Office HadUK-Grid rainfall (39-year climatology, 1987–2025)\n\n"
            "This is an MSc dissertation research prototype (University of "
            "Strathclyde, Advanced Computer Science with Data Science). Its "
            "outputs are model classifications, not validated predictions of "
            "real-world flooding, and not an official flood risk assessment — "
            "always check [SEPA's flood maps](https://www.sepa.scot) for your "
            "specific address."
        )

for key, default in [
    ("selected_point", None),
    ("is_default_point", True),
    ("last_clicked_latlng", None),
    ("search_error", None),
    ("search_warning", None),
    ("search_marker", None),
    ("map_center", DEFAULT_CENTER),
    ("map_zoom", DEFAULT_ZOOM),
    ("last_browsed_district", None),
    ("last_browsed_landmark", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Populate the panel with the university itself on first load, rather than
# leaving it blank until a click/search — see selected-location panel below.
if st.session_state.selected_point is None:
    st.session_state.selected_point = nearest_point(df, UNI_X, UNI_Y)

# --- Postcode search ---
st.markdown("#### Search by postcode")
st.caption(
    "Try a full postcode like **G1 1XQ** (University of Strathclyde) or "
    "**G4 0BA** — or browse by postcode district below."
)
with st.form("postcode_search", clear_on_submit=False):
    search_col, button_col = st.columns([4, 1])
    with search_col:
        postcode_input = st.text_input(
            "Postcode", placeholder="e.g. G1 1XQ", label_visibility="collapsed"
        )
    with button_col:
        submitted = st.form_submit_button("Search", use_container_width=True, type="primary")

browse_options = ["Browse by postcode district..."] + sorted(postcode_districts_df["outcode"].tolist())
browsed_district = st.selectbox(
    "Or browse by postcode district", browse_options, label_visibility="collapsed"
)
if browsed_district != "Browse by postcode district..." and browsed_district != st.session_state.last_browsed_district:
    st.session_state.last_browsed_district = browsed_district
    district_row = postcode_districts_df.loc[postcode_districts_df["outcode"] == browsed_district].iloc[0]
    nearest = nearest_point(df, district_row["easting"], district_row["northing"])
    st.session_state.selected_point = nearest
    st.session_state.is_default_point = False
    st.session_state.map_center = [nearest["lat"], nearest["lon"]]
    st.session_state.map_zoom = 15
    st.session_state.search_marker = {
        "lat": nearest["lat"], "lon": nearest["lon"],
        "postcode": f"{browsed_district} district",
    }
    st.session_state.search_error = None
    st.session_state.search_warning = None

landmark_options = ["Or jump to a landmark..."] + [lm["name"] for lm in LANDMARKS]
browsed_landmark = st.selectbox(
    "Or jump to a landmark", landmark_options, label_visibility="collapsed"
)
if browsed_landmark != "Or jump to a landmark..." and browsed_landmark != st.session_state.last_browsed_landmark:
    st.session_state.last_browsed_landmark = browsed_landmark
    landmark = next(lm for lm in LANDMARKS if lm["name"] == browsed_landmark)
    nearest = nearest_point(df, landmark["easting"], landmark["northing"])
    snap_dist = (
        (nearest["easting"] - landmark["easting"]) ** 2
        + (nearest["northing"] - landmark["northing"]) ** 2
    ) ** 0.5
    st.session_state.selected_point = nearest
    st.session_state.is_default_point = False
    st.session_state.map_center = [nearest["lat"], nearest["lon"]]
    st.session_state.map_zoom = 16
    st.session_state.search_marker = {
        "lat": nearest["lat"], "lon": nearest["lon"],
        "postcode": browsed_landmark,
    }
    st.session_state.search_error = None
    if snap_dist > 300:
        st.session_state.search_warning = (
            f"'{browsed_landmark}' is near the edge of the study area — showing the "
            f"nearest available grid point, {snap_dist:.0f}m away."
        )
    else:
        st.session_state.search_warning = None

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
                nearest = nearest_point(df, east, north)

                st.session_state.selected_point = nearest
                st.session_state.is_default_point = False
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

tab_overview, tab_why, tab_compare, tab_eval = st.tabs(
    ["🗺️ Overview", "🔍 Why this prediction?", "📊 Comparisons", "🧪 Model evaluation"]
)

with tab_overview:
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
                "Minimum classification confidence", min_value=0, max_value=100, value=0, step=1, format="%d%%",
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

        map_data = st_folium(m, height=500, use_container_width=True)
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
        st.session_state.is_default_point = False
        st.session_state.search_marker = None

    with col_panel:
        st.subheader("Selected location")
        point = st.session_state.selected_point

        if point is None:
            st.info("Click a point on the map, or search a postcode above, to see flood risk details here.")
        else:
            if st.session_state.is_default_point:
                st.caption(
                    "📍 Showing the University of Strathclyde by default — search "
                    "a postcode or click the map to check a location of your own."
                )

            risk_label = RISK_LABELS[point["predicted_risk"]]
            badge_colour = RISK_COLOURS[point["predicted_risk"]]

            coord_text = "Coordinates: " + str(round(point["easting"])) + " E, " + str(round(point["northing"])) + " N"
            st.markdown(coord_text)

            badge_html = "<span style='background:" + badge_colour + "22; color:" + badge_colour + "; padding:4px 12px; border-radius:6px; font-weight:600;'>" + risk_label + " (model prediction)</span>"
            st.markdown(badge_html, unsafe_allow_html=True)

            confidence = float(point["confidence"])
            st.markdown(
                f"<span style='font-size:13px; color:{THEME['confidence_text']};'>Confidence in this risk classification: "
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

            # --- Compact context cards: quick-glance facts to sit alongside
            # the badge/confidence/compass above, without turning the panel
            # into another scrollable section — five st.metric cards (two
            # 2-up rows, one full-width) rather than prose, matching the
            # "compact card" style established by the Overview tab redesign.
            st.markdown("---")
            st.markdown("##### More about this location")

            # st.metric's delta slot is deliberately unused below: it's
            # single-line and truncates with an ellipsis, and delta_color="off"
            # still renders a misleading up-arrow glyph on plain text. A
            # regular st.caption() underneath wraps properly instead.
            elev = float(point["elevation"])
            elev_pct_lower = float((df["elevation"] < elev).mean() * 100)
            if elev_pct_lower <= 33:
                elev_context = "One of the lower-lying areas of the study zone."
            elif elev_pct_lower >= 66:
                elev_context = "Relatively high ground for this area."
            else:
                elev_context = "Close to the middle of the local elevation range."

            risk_val = int(point["predicted_risk"])
            risk_share_count = int(risk_counts[risk_val])
            risk_share_pct = risk_share_count / total_points * 100

            pva_dist, pva_zone_name = nearest_pva_zone(point["easting"], point["northing"])
            pva_value = "Inside zone" if pva_dist < 1 else format_distance(pva_dist)

            winter_avg = float(df["mean_winter_mm_day"].mean())
            annual_avg = float(df["mean_annual_mm_day"].mean())

            card_1a, card_1b = st.columns(2)
            with card_1a:
                st.metric("Elevation", f"{elev:.0f}m")
                st.caption(elev_context)
            with card_1b:
                st.metric(f"{RISK_LABELS[risk_val]} citywide", f"{risk_share_pct:.1f}%")
                st.caption(f"{risk_share_count:,} of {total_points:,} study points")

            card_2a, card_2b = st.columns(2)
            with card_2a:
                st.metric("Nearest SEPA flood zone", pva_value)
                st.caption(pva_zone_name)
            with card_2b:
                st.metric("Data basis", "1987–2025")
                st.caption("39-yr rainfall climatology + current elevation/terrain data")

            st.metric("Seasonal pattern", "Winter is wettest")
            st.caption(
                f"~{winter_avg:.2f}mm/day in winter vs ~{annual_avg:.2f}mm/day annual average, "
                "across all study points"
            )

with tab_why:
    # --- "Why this prediction?" — the project's core research contribution,
    # given a full-width, visually distinct treatment (own container, wide
    # centred column, large diverging bar chart) so it reads as the dashboard's
    # centrepiece rather than one panel competing with the filters/tabs/
    # comparisons around it. Pulled out of the narrow col_panel above for this
    # reason. Raw feature values and precautions were also moved out (further
    # below) — keeping col_panel to just the at-a-glance badge/coords/compass
    # keeps its height in the same ballpark as col_map's (filters + map +
    # caption), avoiding the large dead-space gap that opens up beneath the
    # shorter column when st.columns() renders two very different heights
    # side by side and full-width content afterwards has to start below both.
    point = st.session_state.selected_point
    if point is not None:
        pad_l, shap_col, pad_r = st.columns([1, 10, 1])
        with shap_col:
            risk_label = RISK_LABELS[point["predicted_risk"]]
            shap_vals, pred_class = compute_shap_for_point(point)
            order = np.argsort(-np.abs(shap_vals))

            fragments = []
            for rank in range(min(2, len(order))):
                feat = FEATURE_COLS[order[rank]]
                tier = tier_for(feat, point[feat])
                value_str = FEATURE_META[feat]["fmt"].format(point[feat])
                fragments.append(FEATURE_META[feat]["narrative"][tier].format(value=value_str))
            reason_text = fragments[0] if len(fragments) < 2 else f"{fragments[0]}, and {fragments[1]}"

            st.markdown(
                f"""
                <div style='background: {THEME["why_bg"]};
                            border-left: 6px solid {THEME["why_border"]}; border-radius: 12px;
                            padding: 30px 40px; margin: 28px 0 26px 0;'>
                  <h2 style='margin:0 0 12px 0; color:{THEME["why_h2"]}; font-size:1.8rem;'>
                    🔍 Why this prediction?
                  </h2>
                  <p style='margin:0 0 6px 0; color:{THEME["why_p1"]}; font-size:1.1rem; line-height:1.55;'>
                    This location is predicted <b>{risk_label}</b> mainly because {reason_text}.
                  </p>
                  <p style='margin:0; color:{THEME["why_p2"]}; font-size:0.87rem;'>
                    Live SHAP explanation (TreeExplainer, probability space) computed for this exact
                    grid point — the model's own reasoning, feature by feature.
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Diverging bar chart: signed SHAP contribution per feature (zero
            # baseline = no effect either way), sorted by |impact|, reversed
            # before plotting so rank #1 lands at the top (barh draws the first
            # row at the bottom of the y-axis).
            bar_labels, value_strs, risk_dirs, colours, definitions = [], [], [], [], []
            for idx in order:
                feat = FEATURE_COLS[idx]
                raw_shap = shap_vals[idx]
                risk_dir = -raw_shap if pred_class == 0 else raw_shap
                tier = tier_for(feat, point[feat])
                bar_labels.append(FEATURE_META[feat]["bar_label"][tier])
                value_strs.append(FEATURE_META[feat]["fmt"].format(point[feat]) + FEATURE_META[feat]["unit"])
                risk_dirs.append(risk_dir)
                colours.append("#C0392B" if risk_dir > 0 else "#2C6E8E")
                definitions.append((feat, FEATURE_META[feat]["definition"]))

            bar_labels, value_strs, risk_dirs, plot_colours = (
                bar_labels[::-1], value_strs[::-1], risk_dirs[::-1], colours[::-1]
            )

            fig, ax = plt.subplots(figsize=(10, 0.62 * len(bar_labels) + 1.3))
            y_pos = np.arange(len(bar_labels))
            ax.barh(y_pos, risk_dirs, color=plot_colours, height=0.58, zorder=3)
            ax.axvline(0, color=THEME["chart_text"], linewidth=1.4, zorder=4)

            max_abs = max(max(abs(v) for v in risk_dirs), 1e-9)
            ax.set_xlim(-max_abs * 1.4, max_abs * 1.65)
            for i, (v, vs) in enumerate(zip(risk_dirs, value_strs)):
                offset = max_abs * 0.04
                ax.text(v + offset if v >= 0 else v - offset, i, vs,
                         va="center", ha="left" if v >= 0 else "right",
                         fontsize=11, color=THEME["chart_text"])

            ax.set_yticks(y_pos)
            ax.set_yticklabels(bar_labels, fontsize=12.5)
            ax.set_xlabel("Impact on predicted risk  (SHAP value, probability space)", fontsize=11)
            ax.tick_params(axis="x", labelsize=10)
            ax.grid(axis="x", alpha=0.25, zorder=0)
            for spine in ("top", "right", "left"):
                ax.spines[spine].set_visible(False)
            legend = ax.legend(
                handles=[
                    Patch(facecolor="#C0392B", label="Pushes risk up"),
                    Patch(facecolor="#2C6E8E", label="Pushes risk down"),
                ],
                loc="lower right", fontsize=10.5, frameon=False,
            )
            for text in legend.get_texts():
                text.set_color(THEME["chart_text"])
            style_dark_chart(fig, ax)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            top_two = definitions[:2]
            def_col1, def_col2 = st.columns(2)
            for col, (feat, definition) in zip([def_col1, def_col2], top_two):
                with col:
                    tier = tier_for(feat, point[feat])
                    st.markdown(f"**{FEATURE_META[feat]['bar_label'][tier]}**")
                    st.caption(definition)

            with st.expander("What do the other features mean?"):
                for feat, definition in definitions[2:]:
                    tier = tier_for(feat, point[feat])
                    st.markdown(f"**{FEATURE_META[feat]['bar_label'][tier]}** — {definition}")

            # Stacked full-width, not side-by-side columns: two blocks of
            # noticeably different natural height (a 9-row table vs. a 3-item
            # precaution list) left a gap under the shorter one when columned,
            # the same class of issue as the earlier col_map/col_panel gap.
            st.markdown("---")
            st.subheader("Precautions and next steps")
            precautions = PRECAUTIONS[point["predicted_risk"]]
            items_html = "".join(f"<li style='margin-bottom:6px;'>{item}</li>" for item in precautions["items"])
            st.markdown(
                f"""
                <div style='background:{THEME["precautions_bg"]}; border-radius:8px; padding:14px 18px; margin-bottom:8px;'>
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

            with st.expander("Raw feature values at this location"):
                feature_table = point[FEATURE_COLS].to_frame(name="value")
                st.dataframe(feature_table, use_container_width=True)

with tab_compare:
    st.caption(
        "Aggregate context across all grid points, plus how the selected location "
        "compares to real historical flood events."
    )

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

    with st.expander("District risk comparison"):
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

            st.markdown("**Ranked districts by % High risk**")
            st.caption("Your selected location's district is always included and outlined below.")
            ctrl_col1, ctrl_col2 = st.columns(2)
            with ctrl_col1:
                district_n = st.radio("Number of districts", [2, 5, 10], index=1, horizontal=True, key="district_n")
            with ctrl_col2:
                district_view = st.radio(
                    "Rank by", ["Highest % High risk", "Lowest % High risk"],
                    horizontal=True, key="district_view",
                )

            selected_district_for_chart = None
            _sel_point = st.session_state.selected_point
            if _sel_point is not None:
                _candidate = _sel_point["postcode_district"]
                if _candidate != "Unknown":
                    selected_district_for_chart = _candidate

            if district_view == "Highest % High risk":
                district_subset = district_risk.sort_values("High risk %", ascending=False).head(district_n)
                district_bar_colour = RISK_COLOURS[2]
            else:
                district_subset = district_risk.sort_values("High risk %", ascending=True).head(district_n)
                district_bar_colour = RISK_COLOURS[0]

            if (
                selected_district_for_chart
                and selected_district_for_chart not in district_subset.index
                and selected_district_for_chart in district_risk.index
            ):
                district_subset = pd.concat(
                    [district_subset, district_risk.loc[[selected_district_for_chart]]]
                )

            district_plot = district_subset.sort_values(
                "High risk %", ascending=(district_view != "Highest % High risk")
            ).iloc[::-1]
            edge_colours = [THEME["chart_highlight"] if idx == selected_district_for_chart else "none" for idx in district_plot.index]
            edge_widths = [2.4 if idx == selected_district_for_chart else 0 for idx in district_plot.index]

            fig_dist, ax_dist = plt.subplots(figsize=(8, 0.5 * len(district_plot) + 1.2))
            ax_dist.barh(
                district_plot.index, district_plot["High risk %"],
                color=district_bar_colour, edgecolor=edge_colours, linewidth=edge_widths,
            )
            for i, v in enumerate(district_plot["High risk %"]):
                ax_dist.text(v + 0.5, i, f"{v:.1f}%", va='center', fontsize=8, color=THEME["chart_text"])
            ylabels = [
                f"{idx} ← your area" if idx == selected_district_for_chart else idx
                for idx in district_plot.index
            ]
            ax_dist.set_yticklabels(ylabels, fontsize=8)
            ax_dist.set_xlabel("High risk %", fontsize=9)
            ax_dist.set_xlim(0, max(district_risk["High risk %"].max(), 1) * 1.15)
            ax_dist.tick_params(axis='both', labelsize=8)
            style_dark_chart(fig_dist, ax_dist)
            fig_dist.tight_layout()
            st.pyplot(fig_dist, use_container_width=True)
            plt.close(fig_dist)

    with st.expander("Landmark risk comparison"):
        st.caption(
            "Predicted flood risk class and classification confidence at well-known Glasgow "
            "landmarks, so you can compare recognisable parts of the city without searching."
        )

        landmark_rows = []
        for lm in LANDMARKS:
            lm_point = nearest_point(df, lm["easting"], lm["northing"])
            landmark_rows.append({
                "name": lm["name"],
                "risk": int(lm_point["predicted_risk"]),
                "confidence": float(lm_point["confidence"]),
            })
        landmark_df = pd.DataFrame(landmark_rows).sort_values(
            ["risk", "confidence"], ascending=False
        )
        landmark_plot = landmark_df.iloc[::-1]

        fig_lm, ax_lm = plt.subplots(figsize=(8, 0.5 * len(landmark_plot) + 1.2))
        lm_colours = [RISK_COLOURS[r] for r in landmark_plot["risk"]]
        ax_lm.barh(landmark_plot["name"], landmark_plot["confidence"] * 100, color=lm_colours)
        for i, (risk, conf) in enumerate(zip(landmark_plot["risk"], landmark_plot["confidence"])):
            ax_lm.text(conf * 100 + 1.5, i, f"{RISK_LABELS[risk]} · {conf * 100:.0f}% confidence",
                       va='center', fontsize=8, color=THEME["chart_text"])
        ax_lm.set_xlabel("Classification confidence (%)", fontsize=9)
        ax_lm.set_xlim(0, 135)
        ax_lm.tick_params(axis='both', labelsize=8)
        style_dark_chart(fig_lm, ax_lm)
        fig_lm.tight_layout()
        st.pyplot(fig_lm, use_container_width=True)
        plt.close(fig_lm)
        st.caption(
            "Bar colour shows the predicted risk class (green = Low, amber = Medium, red = "
            "High); bar length shows the model's confidence in that classification, not a "
            "probability of flooding. Ibrox and Partick sit right at the edge of the 5km "
            "study area."
        )

    with st.expander("Ranked individual grid points by risk"):
        st.caption(
            "Points ranked by classification confidence within their predicted class — "
            "'Highest risk' ranks points predicted High risk by confidence in that "
            "classification; 'Lowest risk' does the same for points predicted Low risk."
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

            plot_labels = list(reversed(point_labels))
            plot_values = list(reversed(point_values))

            fig_pts, ax_pts = plt.subplots(figsize=(8, 0.5 * len(plot_labels) + 1.2))
            ax_pts.barh(plot_labels, plot_values, color=RISK_COLOURS[target_class])
            for i, v in enumerate(plot_values):
                ax_pts.text(v + 0.5, i, f"{v:.1f}%", va='center', fontsize=8, color=THEME["chart_text"])
            ax_pts.set_xlabel(f"Classification confidence in {RISK_LABELS[target_class]} (%)", fontsize=9)
            ax_pts.set_xlim(0, 105)
            ax_pts.tick_params(axis='both', labelsize=8)
            style_dark_chart(fig_pts, ax_pts)
            fig_pts.tight_layout()
            st.pyplot(fig_pts, use_container_width=True)
            plt.close(fig_pts)

    with st.expander("Distribution charts: risk vs. elevation, confidence"):
        col_scatter, col_hist = st.columns(2)

        with col_scatter:
            st.markdown("**Risk vs. elevation**")
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
            style_dark_chart(fig_sc, ax_sc)
            fig_sc.tight_layout()
            st.pyplot(fig_sc, use_container_width=True)
            plt.close(fig_sc)
            st.caption(
                "Low-elevation points cluster almost entirely into Medium/High risk, "
                "visually reinforcing elevation's ~63% feature importance (see the Model "
                "evaluation tab)."
            )

        with col_hist:
            st.markdown("**Classification confidence distribution**")
            st.caption(f"predict_proba confidence in the model's own classification across all {len(df):,} points, by risk class — not a probability of flooding")
            fig_hist, ax_hist = plt.subplots(figsize=(5, 3.5))
            bins = np.linspace(df["confidence"].min(), 1.0, 25)
            for risk_val in [0, 1, 2]:
                vals = df.loc[df["predicted_risk"] == risk_val, "confidence"]
                ax_hist.hist(vals, bins=bins, alpha=0.55, color=RISK_COLOURS[risk_val], label=RISK_LABELS[risk_val])
            ax_hist.set_xlabel("Classification confidence", fontsize=9)
            ax_hist.set_ylabel("Number of points", fontsize=9)
            ax_hist.tick_params(axis='both', labelsize=8)
            ax_hist.legend(fontsize=7)
            ax_hist.grid(axis='y', alpha=0.3)
            style_dark_chart(fig_hist, ax_hist)
            fig_hist.tight_layout()
            st.pyplot(fig_hist, use_container_width=True)
            plt.close(fig_hist)

with tab_eval:
    st.caption(
        "Random Forest is the live model behind every prediction on this page. Figures below "
        "are from 04_ML_Model.ipynb's held-out 20% test split (stratified, random_state=42) "
        "unless noted otherwise; XGBoost appears only as a comparison model, not a live one."
    )

    _rf = MODEL_COMPARISON["random_forest"]
    _avg_auc = sum(RF_ROC_AUC.values()) / len(RF_ROC_AUC)

    st.markdown("##### Headline metrics")
    _metric_col1, _metric_col2, _metric_col3, _metric_col4 = st.columns(4)
    _metric_col1.metric("Accuracy (test split)", f"{_rf['accuracy']:.2%}")
    _metric_col2.metric("F1 macro (test split)", f"{_rf['f1_macro']:.2%}")
    _metric_col3.metric("5-fold CV accuracy", f"{RF_CV_METRICS['accuracy']['mean']:.2%}",
                         f"±{RF_CV_METRICS['accuracy']['std']:.2%}")
    _metric_col4.metric("Mean ROC-AUC (one-vs-rest)", f"{_avg_auc:.4f}")

    st.warning(
        "⚠️ **This model's high accuracy reflects its ability to reconstruct a known "
        "elevation/SEPA-PVA-zone-based rule, not validated prediction of real-world flood "
        "events.** The `flood_risk` label itself is derived from elevation and SEPA PVA "
        "zone membership — two quantities closely related to several of the model's own "
        "input features — so the figures above show the classifier successfully recovering "
        "a defensible labelling rule from continuous inputs, not independent validation "
        "against observed historical flooding."
    )

    st.markdown("##### Per-class F1 (test split)")
    _f1_col1, _f1_col2, _f1_col3 = st.columns(3)
    _f1_col1.metric("Low risk F1", f"{RF_PER_CLASS_METRICS['Low risk']['f1']:.2%}")
    _f1_col2.metric("Medium risk F1", f"{RF_PER_CLASS_METRICS['Medium risk']['f1']:.2%}")
    _f1_col3.metric("High risk F1", f"{RF_PER_CLASS_METRICS['High risk']['f1']:.2%}")

    st.markdown("##### Confusion matrix (test split)")
    _cm_df = pd.DataFrame(
        RF_CONFUSION_MATRIX,
        index=["Actual: Low", "Actual: Medium", "Actual: High"],
        columns=["Pred: Low", "Pred: Medium", "Pred: High"],
    )
    st.dataframe(_cm_df, use_container_width=True)
    st.caption(
        "Only 6 of 1,569 test points are misclassified, all Low↔High confusions — "
        "no confusion at all between Medium risk and either other class."
    )

    with st.expander("Feature importance (Random Forest vs XGBoost)"):
        col_fi_rf, col_fi_xgb = st.columns(2)
        with col_fi_rf:
            st.image(FEATURE_IMPORTANCE_RF_IMG, use_container_width=True)
        with col_fi_xgb:
            st.image(FEATURE_IMPORTANCE_XGB_IMG, use_container_width=True)
        st.caption(
            "Both models agree elevation is by far the dominant risk driver (63% for Random "
            "Forest, 93% for XGBoost), with dist_to_clyde a clear #2 in both."
        )

    with st.expander("SHAP summary (global, all points)"):
        st.image(SHAP_SUMMARY_IMG, use_container_width=True)
        st.caption(
            "SHAP beeswarm plots per risk class, from the same held-out test split — this "
            "per-prediction explanation is the project's core research contribution. Select a "
            "location on the Overview tab for a live, single-point version of this on the "
            "'Why this prediction?' tab."
        )

    with st.expander("Random Forest vs XGBoost — full comparison"):
        st.caption(
            "Random Forest's numbers below are 5-fold cross-validated; XGBoost's are from a "
            "single 80/20 split (it's a comparison model, not cross-validated) — labelled "
            "accordingly rather than implying an identical methodology."
        )
        _comparison_df = pd.DataFrame(
            {
                "Random Forest": [
                    f"{RF_CV_METRICS['accuracy']['mean']:.2%} ± {RF_CV_METRICS['accuracy']['std']:.2%}",
                    f"{RF_CV_METRICS['f1_macro']['mean']:.2%} ± {RF_CV_METRICS['f1_macro']['std']:.2%}",
                    f"{RF_PER_CLASS_METRICS['Low risk']['f1']:.2%}",
                    f"{RF_PER_CLASS_METRICS['Medium risk']['f1']:.2%}",
                    f"{RF_PER_CLASS_METRICS['High risk']['f1']:.2%}",
                ],
                "XGBoost": [
                    f"{XGB_SPLIT_METRICS['accuracy']:.2%}",
                    f"{XGB_SPLIT_METRICS['f1_macro']:.2%}",
                    f"{XGB_PER_CLASS_F1['Low']:.2%}",
                    f"{XGB_PER_CLASS_F1['Medium']:.2%}",
                    f"{XGB_PER_CLASS_F1['High']:.2%}",
                ],
            },
            index=["Accuracy", "F1 macro", "F1 — Low", "F1 — Medium", "F1 — High"],
        )
        st.dataframe(_comparison_df, use_container_width=True)
        st.markdown(
            f"**{_rf['label']} is the live model** for all predictions on this page — it edges "
            "out XGBoost on every metric above, so there's no case for switching. Both models "
            "agree elevation is by far the dominant risk driver; dist_to_clyde ranks a clear #2 "
            "by native feature importance in both, though the models' SHAP rankings of "
            "dist_to_clyde are less consistent (XGBoost's SHAP values had to be computed in raw "
            "margin space, not probability space — see 04_ML_Model.ipynb)."
        )

st.markdown("---")
st.caption(
    "**CARE Dashboard** — MSc dissertation research prototype by Ritesh Raju "
    "Ghorpade, supervised by Dr Daniel Thomas (Advanced Computer Science with "
    "Data Science, University of Strathclyde). Data: SEPA PVA flood "
    "boundaries, OpenStreetMap, NASA SRTM elevation, Met Office HadUK-Grid "
    "rainfall (1987–2025). Model outputs are research classifications, not "
    "validated predictions of real-world flooding, and not an official flood "
    "risk assessment — always check "
    "[SEPA's flood maps](https://www.sepa.scot) for your specific address."
)

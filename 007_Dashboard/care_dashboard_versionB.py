

import calendar
import datetime
import math
from pathlib import Path
from urllib.parse import quote

from care_paths import DATA_PATH, MODEL_PATH, SEPA_PVA_PATH, require

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

st.set_page_config(page_title="CARE Dashboard — Version B", layout="wide")

# ============================================================================
# Fixed dark theme — Version B's design identity. Independent of the shared
# .streamlit/config.toml (which stays light, for versionA.py) and of
# versionB.py's own user-togglable theme; nothing here can affect either.
# ============================================================================
BG_APP = "#0B0F17"
BG_CARD = "#131822"
BG_CARD_2 = "#1B222C"
BORDER = "rgba(255,255,255,0.09)"
TEXT_MAIN = "#E6EDF3"
TEXT_MUTED = "#93A1B0"
ACCENT = "#2F8FCF"
ACCENT_2 = "#4FB3C9"
RISK_LOW, RISK_MED, RISK_HIGH = "#4CA94C", "#EF9F27", "#E24B4A"

st.markdown(
    f"""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {BG_APP};
            color: {TEXT_MAIN};
        }}
        [data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); }}
        .block-container {{ padding-top: 0.7rem; padding-bottom: 1rem; max-width: 1650px; }}
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp span, .stApp label, .stApp li {{ color: {TEXT_MAIN}; }}
        [data-testid="stCaptionContainer"], .stCaption {{ color: {TEXT_MUTED} !important; }}
        hr {{ border-color: rgba(255,255,255,0.12); margin: 0.4rem 0; }}

        /* Compact spacing pass, scoped to this app only — tightens
           Streamlit's default block/element gaps so the page reads as one
           dense research dashboard rather than stacked widgets. */
        [data-testid="stVerticalBlock"] {{ gap: 0.5rem; }}
        [data-testid="stHorizontalBlock"] {{ gap: 0.6rem; }}
        /* Deliberately NOT zeroing [data-testid="stElementContainer"]'s
           margin here (an earlier pass did, relying entirely on the gap
           value above for spacing) — that made every element's separation
           depend on flex gap resolving correctly in every context, and it
           didn't always: Streamlit's own internal styling for some
           components (bordered containers in particular) can override or
           interact with gap unpredictably. A small explicit margin gives
           every element pair a spacing floor that doesn't depend on that. */
        [data-testid="stElementContainer"] {{ margin-bottom: 0.35rem; }}
        [data-testid="stMarkdownContainer"] p {{ margin-bottom: 0.3rem; overflow-wrap: break-word; }}
        [data-testid="stCaptionContainer"] p {{ margin: 0; line-height: 1.35; overflow-wrap: break-word; }}
        [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] {{
            gap: 0.5rem;
        }}
        /* align-items:flex-start (don't force equal height) is scoped to
           ONLY the page's top-level left/right column split — that's the
           one place we deliberately don't want a short column stretched to
           match a much taller sibling. Every other st.columns() row in the
           app (metric cards, season cards, stat grids, etc.) keeps
           Streamlit's own default align-items:stretch, so sibling columns
           with different text lengths still end at the same height instead
           of leaving ragged card edges that can crowd whatever renders
           immediately below them. */
        .st-key-page_columns [data-testid="stHorizontalBlock"] {{ align-items: flex-start; }}

        [data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {{
            background-color: {ACCENT};
            color: #FFFFFF;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 8px;
        }}
        [data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {{
            background-color: {ACCENT_2};
            border-color: {ACCENT_2};
            color: #FFFFFF;
        }}

        [data-testid="stTextInput"] input, [data-baseweb="select"] > div, [data-baseweb="base-input"] {{
            background-color: {BG_CARD} !important;
            color: {TEXT_MAIN} !important;
            border-color: {BORDER} !important;
        }}
        [data-baseweb="popover"], [data-baseweb="menu"] {{ background-color: {BG_CARD} !important; }}
        [data-baseweb="tag"] {{ background-color: {ACCENT} !important; }}
        [data-testid="stSlider"] [data-baseweb="slider"] > div:first-child {{
            background: rgba(255,255,255,0.14) !important;
        }}

        [data-testid="stExpander"] {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 10px;
        }}
        [data-testid="stExpander"] summary {{ color: {TEXT_MAIN}; }}

        /* Native bordered containers (st.container(border=True)) become the
           dashboard's "card" unit — one per numbered section — matching the
           reference's rounded panels / thin borders / subtle shadow. */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(160deg, {BG_CARD_2} 0%, {BG_CARD} 100%);
            border: 1px solid {BORDER} !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        }}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {{
            box-shadow: none;
        }}
        /* Streamlit pads the inner block of a bordered container at ~1rem;
           this tightens that to the 8-12px target without touching padding
           on nested containers (e.g. the risk-scale/interpretation divs
           below, which set their own). */
        [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] {{
            padding: 10px 12px;
        }}

        [data-testid="stMetric"] {{
            background: transparent;
            border: none;
            padding: 2px 0 0 0;
        }}
        [data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-weight: 600 !important; font-size: 0.7rem !important; }}
        [data-testid="stMetricValue"] {{ color: #F4FAFB !important; font-weight: 800 !important; font-size: 1.2rem !important; }}
        [data-testid="stMetricDelta"] {{ font-size: 0.72rem !important; }}

        [data-testid="stAlert"] {{ color: #0E1117; padding: 6px 10px; }}

        /* st.pyplot() charts placed directly inside an auto-height
           st.container(border=True) — i.e. with no st.columns() ahead of
           them in the same block — inherit align-items:flex-start from
           Streamlit's own container CSS instead of the usual stretch,
           which otherwise leaves the image to its unstyled intrinsic
           width. Forcing width here sidesteps that rather than fighting
           Streamlit's internal flex state. */
        [data-testid="stImageContainer"], [data-testid="stImage"] {{ width: 100% !important; }}
        [data-testid="stImage"] img {{ width: 100% !important; height: auto !important; }}

        /* One consistent section-header standard for all 9 sections. The
           title always has margin:0 on top (it's the first thing in the
           card) and carries its own safe bottom gap into whatever follows
           it directly. Where a subtitle is present, the title's own gap
           collapses to a small separator instead — the subtitle then owns
           the safe gap into the section's actual content, so there is
           never a double gap and never a zero gap, regardless of which
           element (title or subtitle) is immediately followed by content. */
        .care-section-title {{
            font-size: 0.94rem; font-weight: 800; letter-spacing: 0.01em;
            color: {ACCENT_2}; margin: 0 0 10px 0; text-transform: uppercase;
            line-height: 1.2;
        }}
        .care-section-title.has-subtitle {{ margin-bottom: 3px; }}
        .care-section-subtitle {{
            font-size: 0.73rem; color: {TEXT_MUTED}; line-height: 1.3;
            margin: 3px 0 10px 0;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def section_header(number, title, subtitle=None):
    title_cls = "care-section-title has-subtitle" if subtitle else "care-section-title"
    st.markdown(f"<div class='{title_cls}'>{number}. {title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='care-section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


# ============================================================================
# Paths — the three shared files resolve via the unmodified care_paths.py
# (same as A/B); the two new rainfall files resolve independently, right
# here, so care_paths.py never needs to change for Version B to exist.
# ============================================================================
DATA_PATH = require(DATA_PATH, "feature matrix (feature_matrix_40yr.csv)")
MODEL_PATH = require(MODEL_PATH, "trained Random Forest model (rf_model_40yr.joblib)")
SEPA_PVA_PATH = require(SEPA_PVA_PATH, "SEPA PVA flood boundaries (PVAv2.gpkg)")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONTHLY_RAINFALL_PATH = PROJECT_ROOT / "002_Dataset" / "processed" / "rainfall_monthly_40yr.csv"
ANNUAL_RAINFALL_PATH = PROJECT_ROOT / "002_Dataset" / "processed" / "rainfall_annual_40yr.csv"
require(MONTHLY_RAINFALL_PATH, "monthly rainfall climatology (rainfall_monthly_40yr.csv) — "
        "run 003_Code/08_Rainfall_Monthly_Seasonal.py to generate it")
require(ANNUAL_RAINFALL_PATH, "annual rainfall series (rainfall_annual_40yr.csv) — "
        "run 003_Code/08_Rainfall_Monthly_Seasonal.py to generate it")

POSTCODES_API = "https://api.postcodes.io/postcodes/"
OUTCODES_API = "https://api.postcodes.io/outcodes"

FEATURE_COLS = ["elevation", "dist_to_water", "dist_to_clyde", "building_count",
                "road_count", "mean_annual_mm_day", "mean_winter_mm_day",
                "wet_days_per_year", "max_daily_mm"]

UNI_X, UNI_Y = 260983, 665006  # University of Strathclyde, EPSG:27700
DEFAULT_CENTER = [55.8611, -4.2436]
DEFAULT_ZOOM = 13

# --- Feature metadata, SHAP narrative fragments — verbatim from
# care_dashboard_versionB.py (FEATURE_META), unmodified. ---
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

# --- River Clyde reference points, compass helpers — verbatim from
# care_dashboard_versionB.py. ---
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

# --- Historical flood events — verbatim from care_dashboard_versionB.py. ---
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
    {
        "name": "1994 Glasgow Central (Low Level) floods",
        "easting": 258736, "northing": 665373,
        "date": "12 December 1994",
        "caption": (
            "Same event as the SEC Centre flood: River Kelvin floodwater surged "
            "through disused railway tunnels (Kelvingrove/Yorkhill) and reached "
            "Glasgow Central's Low Level underground platforms, several miles "
            "from the river itself."
        ),
        "source": "Bloomberg / Grokipedia reporting; GlasgowWorld and Railscot historical accounts",
    },
    {
        "name": "1795 Saltmarket bridge flood",
        "easting": 259413, "northing": 664441,
        "date": "18 November 1795",
        "caption": (
            "The River Clyde, in spate, flooded the centre of Glasgow and brought "
            "down the recently erected stone bridge at the foot of the Saltmarket "
            "— two arches collapsed near noon, the remaining three that evening. "
            "Marker placed at Albert Bridge, rebuilt on the same site in 1871."
        ),
        "source": "Wikipedia, \"1795 in Scotland\"",
    },
]

# --- Rainfall trend context — verbatim from care_dashboard_versionB.py. ---
RAINFALL_TREND = {
    "period_a": {"label": "1987-2005", "n_years": 19,
                 "annual_total_mm": 1069, "wet_days_per_year": 172.5},
    "period_b": {"label": "2006-2025", "n_years": 20,
                 "annual_total_mm": 1088, "wet_days_per_year": 169.8},
}

# --- New: 39-year historical rainfall headline stats. Precomputed offline
# by 003_Code/08_Rainfall_Monthly_Seasonal.py from the same daily parquet
# RAINFALL_TREND above was built from (area-averaged across all 7,843 grid
# points, same convention). Reproducible by re-running that script. 2020's
# annual total is based on 335/366 days (source archive is missing all of
# July 2020, a pre-existing gap — see RAINFALL_YTD_2026 below); 2020 is
# neither the wettest nor driest year, so this doesn't affect either figure. ---
HISTORICAL_RAINFALL_STATS = {
    "period_start": 1987, "period_end": 2025, "n_years": 39,
    "mean_annual_mm": 1079.0,
    "wettest_year": {"year": 2011, "total_mm": 1427.8},
    "driest_year": {"year": 2001, "total_mm": 789.1},
    "max_month": {"year": 2020, "month": 2, "total_mm": 250.4},
}

# --- 2026 year-to-date rainfall — verbatim from care_dashboard_versionB.py. ---
RAINFALL_YTD_2026 = {
    "label": "2026 YTD (Jan-Jul)",
    "total_mm": 458.3,
    "wet_days": 99.1,
    "hist_avg_total_mm": 559.3,
    "hist_avg_wet_days": 94.5,
    "hist_n_years": 38,
}

# --- Risk-tiered precautions — verbatim from care_dashboard_versionB.py. ---
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

RISK_COLOURS = {0: RISK_LOW, 1: RISK_MED, 2: RISK_HIGH}
RISK_LABELS = {0: "Low risk", 1: "Medium risk", 2: "High risk"}
RISK_SWATCH = {0: "🟢", 1: "🟡", 2: "🔴"}

SEASON_MONTHS = {"Winter": [12, 1, 2], "Spring": [3, 4, 5], "Summer": [6, 7, 8], "Autumn": [9, 10, 11]}
SEASON_ICONS = {"Winter": "❄️", "Spring": "🌱", "Summer": "☀️", "Autumn": "🍂"}
MONTH_ABBR = [calendar.month_abbr[m] for m in range(1, 13)]  # Jan..Dec, each exactly once

# ============================================================================
# Data / model loading — same cached pattern as A/B.
# ============================================================================
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
# grid_id = the CSV's original row order, which is exactly how
# rainfall_features_40yr.csv / rainfall_daily_1987_2025.parquet /
# rainfall_monthly_40yr.csv key their rows (confirmed in the feasibility
# audit). Stored as an explicit column, not relied on via the pandas index,
# because filtering/sampling downstream (the map's random sample, in
# particular) resets the index but must still carry a correct grid_id.
df["grid_id"] = df.index
hist_transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

@st.cache_data
def load_monthly_rainfall(path):
    return pd.read_csv(path)

@st.cache_data
def load_annual_rainfall(path):
    return pd.read_csv(path)

monthly_rainfall_df = load_monthly_rainfall(MONTHLY_RAINFALL_PATH)
annual_rainfall_df = load_annual_rainfall(ANNUAL_RAINFALL_PATH)

@st.cache_data
def load_postcode_districts():
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
    if districts_df.empty:
        return pd.Series(["Unknown"] * len(df), index=df.index)
    dx = df["easting"].values[:, None] - districts_df["easting"].values[None, :]
    dy = df["northing"].values[:, None] - districts_df["northing"].values[None, :]
    nearest_idx = (dx ** 2 + dy ** 2).argmin(axis=1)
    return pd.Series(districts_df["outcode"].values[nearest_idx], index=df.index)

postcode_districts_df = load_postcode_districts()
df["postcode_district"] = assign_postcode_district(df, postcode_districts_df)

@st.cache_data
def load_pva_zones(path, centre_x, centre_y, radius=5000):
    pva = gpd.read_file(path)
    centre = Point(centre_x, centre_y)
    return pva[pva.geometry.intersects(centre.buffer(radius))].copy()

pva_zones = load_pva_zones(SEPA_PVA_PATH, UNI_X, UNI_Y)

def nearest_pva_zone(easting, northing):
    dists = pva_zones.geometry.distance(Point(easting, northing))
    idx = dists.idxmin()
    return float(dists.loc[idx]), str(pva_zones.loc[idx, "PVA_Name"])

risk_counts = df["predicted_risk"].value_counts().reindex([0, 1, 2], fill_value=0)
total_points = int(risk_counts.sum())

# --- SHAP setup — same probability-space TreeExplainer approach as
# care_dashboard_versionB.py / 04_ML_Model.ipynb. ---
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
    sv = explainer.shap_values(row)
    predicted_class = int(point["predicted_risk"])
    shap_for_class = sv[0, :, predicted_class]
    return shap_for_class, predicted_class

def style_dark_chart(fig, *axes):
    fig.patch.set_facecolor(BG_CARD)
    for ax in axes:
        ax.set_facecolor(BG_CARD)
        ax.tick_params(colors="#C7D1DA")
        ax.xaxis.label.set_color(TEXT_MAIN)
        ax.yaxis.label.set_color(TEXT_MAIN)
        ax.title.set_color(TEXT_MAIN)
        for spine in ax.spines.values():
            spine.set_color("#3A4048")
        ax.grid(color="#3A4048")
        legend = ax.get_legend()
        if legend is not None:
            legend.get_frame().set_facecolor(BG_CARD_2)
            legend.get_frame().set_edgecolor("#3A4048")
            for text in legend.get_texts():
                text.set_color(TEXT_MAIN)

# ============================================================================
# Rainfall-exposure helpers (new). All operate on the small, precomputed
# monthly/annual CSVs — never the 111M-row daily parquet, which is only ever
# touched offline by 003_Code/08_Rainfall_Monthly_Seasonal.py.
# ============================================================================
def monthly_exposure_for_point(grid_id):
    """This point's 12-month rainfall climatology, plus a 0-1 'exposure
    index' (min-max normalised across that point's own 12 months) and a
    Low/Moderate/High tier per month (terciles across those 12 months).
    Historical rainfall climatology only — not a model output, not a
    prediction, and not derived from the flood-risk classifier."""
    sub = (
        monthly_rainfall_df[monthly_rainfall_df["grid_id"] == grid_id]
        .sort_values("month")
        .reset_index(drop=True)
        .copy()
    )
    lo, hi = sub["mean_mm_day"].min(), sub["mean_mm_day"].max()
    span = hi - lo if hi > lo else 1.0
    sub["exposure_index"] = (sub["mean_mm_day"] - lo) / span
    q1, q2 = sub["mean_mm_day"].quantile([1 / 3, 2 / 3])
    sub["relative_level"] = sub["mean_mm_day"].apply(
        lambda v: "Low" if v <= q1 else ("High" if v >= q2 else "Moderate")
    )
    sub["month_abbr"] = sub["month"].apply(lambda m: MONTH_ABBR[m - 1])
    return sub

def seasonal_exposure_for_point(grid_id):
    """Same point's rainfall aggregated into the 4 meteorological seasons,
    with a relative Low/Moderate/High exposure category ranked across that
    point's own 4 seasons (not an absolute or model-derived scale)."""
    sub = monthly_rainfall_df[monthly_rainfall_df["grid_id"] == grid_id]
    rows = []
    for season, months in SEASON_MONTHS.items():
        s = sub[sub["month"].isin(months)]
        rows.append({
            "season": season,
            "months": "/".join(MONTH_ABBR[m - 1] for m in months),
            "mean_mm_day": s["mean_mm_day"].mean(),
            "wet_days": s["wet_days"].sum(),
        })
    seasonal = pd.DataFrame(rows)
    order = np.argsort(seasonal["mean_mm_day"].values)
    tier_by_rank = ["Low", "Moderate", "Moderate", "High"]
    tiers = [None] * len(seasonal)
    for rank, idx in enumerate(order):
        tiers[idx] = tier_by_rank[rank]
    seasonal["exposure_category"] = tiers
    return seasonal

def current_season():
    month = datetime.date.today().month
    for season, months in SEASON_MONTHS.items():
        if month in months:
            return season
    return "Winter"

# ============================================================================
# Session state
# ============================================================================
for key, default in [
    ("selected_point", None),
    ("is_default_point", True),
    ("last_clicked_latlng", None),
    ("search_error", None),
    ("search_warning", None),
    ("search_marker", None),
    ("map_center", DEFAULT_CENTER),
    ("map_zoom", DEFAULT_ZOOM),
    ("filters_version", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def reset_search_and_filters():
    st.session_state.selected_point = None
    st.session_state.is_default_point = True
    st.session_state.search_marker = None
    st.session_state.search_error = None
    st.session_state.search_warning = None
    st.session_state.last_clicked_latlng = None
    st.session_state.map_center = DEFAULT_CENTER
    st.session_state.map_zoom = DEFAULT_ZOOM
    st.session_state.filters_version += 1

_fv = st.session_state.filters_version

if st.session_state.selected_point is None:
    st.session_state.selected_point = nearest_point(df, UNI_X, UNI_Y)

# ============================================================================
# Header
# ============================================================================
with st.container(key="care_header"):
    st.markdown(
        f"""
        <style>
        .st-key-care_header {{
            background: linear-gradient(135deg, #123241, #0B1D26);
            border: 1px solid {BORDER};
            border-radius: 12px; padding: 10px 20px; margin-bottom: 10px;
        }}
        .st-key-care_header [data-testid="stVerticalBlock"] {{ gap: 4px; }}
        /* Explicit clearance for the Reset All button below the version
           badges/subtitle text — without this, Streamlit's own button
           wrapper renders with enough negative offset to sit on top of the
           text above it once the header's ambient gap is compacted. */
        .st-key-care_header [data-testid="stButton"] {{ margin-top: 10px; }}
        .care-logo {{
            width: 32px; height: 32px; border-radius: 8px;
            background: linear-gradient(135deg, {ACCENT}, {ACCENT_2});
            display: flex; align-items: center; justify-content: center;
            font-size: 1.05rem;
        }}
        .care-version-badge {{
            display: inline-block; padding: 2px 9px; border-radius: 999px;
            font-size: 0.66rem; font-weight: 700; margin-left: 5px;
            border: 1px solid {BORDER}; color: {TEXT_MUTED};
        }}
        .care-version-badge.active {{
            background: {ACCENT}; color: #FFFFFF; border-color: {ACCENT_2};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    h_logo, h_title, h_versions = st.columns([0.4, 5, 2.6])
    with h_logo:
        st.markdown("<div class='care-logo'>💧</div>", unsafe_allow_html=True)
    with h_title:
        st.markdown(
            "<div style='font-size:1.08rem; font-weight:800; line-height:1.15;'>"
            "CARE — Climate Awareness &amp; Risk Evaluation</div>"
            "<div style='font-size:0.74rem; color:" + TEXT_MUTED + "; line-height:1.2;'>"
            "Flood-Risk Assessment Dashboard</div>",
            unsafe_allow_html=True,
        )
    with h_versions:
        st.markdown(
            "<div style='text-align:right; margin-bottom:3px;'>"
            "<span class='care-version-badge active'>Version B</span>"
            "</div>"
            "<div style='text-align:right; font-size:0.62rem; color:" + TEXT_MUTED + "; margin-bottom:3px;'>"
            "Advanced Explainable Flood-Risk Dashboard</div>",
            unsafe_allow_html=True,
        )
        if st.button("Reset All", use_container_width=True):
            reset_search_and_filters()
            st.rerun()

# ============================================================================
# Layout: fixed left / right columns, no tabs — sections 1-4 left, 5-9 right.
# ============================================================================
with st.container(key="page_columns"):
    col_left, col_right = st.columns([0.95, 1.45], gap="small")

# ----------------------------------------------------------------------------
# LEFT COLUMN
# ----------------------------------------------------------------------------
with col_left:

    # --- 1. Enter postcode ---
    with st.container(border=True):
        section_header("1", "Enter Postcode")
        st.caption("Enter a UK postcode to locate the nearest CARE grid point.")
        with st.form("postcode_search", clear_on_submit=False):
            search_col, button_col = st.columns([4.2, 1])
            with search_col:
                postcode_input = st.text_input(
                    "Postcode", placeholder="e.g. G1 1XQ", label_visibility="collapsed",
                    key=f"postcode_input_{_fv}",
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
                        nearest = nearest_point(df, east, north)
                        st.session_state.selected_point = nearest
                        st.session_state.is_default_point = False
                        st.session_state.map_center = [nearest["lat"], nearest["lon"]]
                        st.session_state.map_zoom = 16
                        st.session_state.search_marker = {
                            "lat": nearest["lat"], "lon": nearest["lon"],
                            "postcode": result["postcode"],
                            "admin_district": result.get("admin_district"),
                        }
                        st.session_state.search_error = None
                        dist_from_uni_km = ((east - UNI_X) ** 2 + (north - UNI_Y) ** 2) ** 0.5 / 1000
                        if dist_from_uni_km > 15:
                            st.session_state.search_warning = (
                                f"'{result['postcode']}' is {dist_from_uni_km:.1f}km from the "
                                "study area centre — showing the nearest available grid point."
                            )
                        else:
                            st.session_state.search_warning = None
                    elif resp.status_code == 404:
                        st.session_state.search_error = f"Postcode '{postcode}' not found — check it's a valid UK postcode."
                        st.session_state.search_warning = None
                    else:
                        st.session_state.search_error = f"Postcode lookup failed (HTTP {resp.status_code}). Try again."
                        st.session_state.search_warning = None

        if st.session_state.search_error:
            st.error(st.session_state.search_error)
        elif st.session_state.search_warning:
            st.warning(st.session_state.search_warning)
        elif st.session_state.search_marker and not st.session_state.is_default_point:
            sm = st.session_state.search_marker
            loc_bits = sm["postcode"]
            if sm.get("admin_district"):
                loc_bits += f", {sm['admin_district']}"
            st.success(f"Location found: {loc_bits}")
        elif st.session_state.is_default_point:
            st.caption("Showing the University of Strathclyde by default — search a postcode above to check a location of your own.")

    point = st.session_state.selected_point
    shap_vals, pred_class = compute_shap_for_point(point)
    shap_order = np.argsort(-np.abs(shap_vals))
    monthly_exposure = monthly_exposure_for_point(int(point["grid_id"]))
    seasonal_exposure = seasonal_exposure_for_point(int(point["grid_id"]))
    this_season = current_season()
    this_season_row = seasonal_exposure[seasonal_exposure["season"] == this_season].iloc[0]

    # --- 2. Prediction summary ---
    with st.container(border=True):
        section_header("2", "Prediction Summary")

        risk_val = int(point["predicted_risk"])
        risk_label = RISK_LABELS[risk_val]
        confidence = float(point["confidence"])

        def _mini_card(label, value, value_colour, note):
            # min-height (not a fixed height) plus box-sizing:border-box: the
            # note text's length varies with season/risk-class, so the card
            # must grow for a two-line note rather than clip it, while the
            # .st-key-page_columns stretch rule (see main CSS block) still
            # keeps all 3 cards in this row equal height for the common case.
            return (
                f"<div class='care-metric-card' style='background:{BG_CARD}; border:1px solid {BORDER}; "
                f"border-radius:8px; padding:7px 9px; min-height:72px; box-sizing:border-box;'>"
                f"<div style='font-size:0.66rem; color:{TEXT_MUTED}; font-weight:600;'>{label}</div>"
                f"<div style='font-size:1.2rem; font-weight:800; color:{value_colour}; line-height:1.25;'>{value}</div>"
                f"<div style='font-size:0.63rem; color:{TEXT_MUTED}; margin-top:1px;'>{note}</div>"
                f"</div>"
            )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(_mini_card("RISK LEVEL", risk_label, RISK_COLOURS[risk_val], "Model classification"), unsafe_allow_html=True)
        with c2:
            st.markdown(_mini_card("MODEL CONFIDENCE", f"{confidence * 100:.0f}%", TEXT_MAIN, "Not a flood probability"), unsafe_allow_html=True)
        with c3:
            st.markdown(_mini_card("SEASONAL RAINFALL", this_season_row["exposure_category"], TEXT_MAIN, f"{this_season} — historical, not model risk"), unsafe_allow_html=True)

        # Risk scale — the model's actual 3 classes only (Low/Medium/High);
        # no "Very High" tier is invented since the classifier has none.
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        seg_labels = [(0, "LOW"), (1, "MODERATE"), (2, "HIGH")]
        segs_html = ""
        for val, label in seg_labels:
            active = val == risk_val
            colour = RISK_COLOURS[val]
            opacity = "1" if active else "0.28"
            border = f"2px solid {colour}" if active else "1px solid transparent"
            segs_html += (
                f"<div style='flex:1; text-align:center; padding:4px 4px; background:{colour}; "
                f"opacity:{opacity}; border:{border}; border-radius:5px; font-size:0.64rem; "
                f"font-weight:800; color:#0B0F17;'>{label}</div>"
            )
        st.markdown(f"<div style='display:flex; gap:4px;'>{segs_html}</div>", unsafe_allow_html=True)

        # Interpretation card — hedged, non-causal language per project
        # convention; reuses the same SHAP top-2 features as the "Why this
        # result?" panel below, computed once per rerun.
        fragments = []
        for rank in range(min(2, len(shap_order))):
            feat = FEATURE_COLS[shap_order[rank]]
            tier = tier_for(feat, point[feat])
            value_str = FEATURE_META[feat]["fmt"].format(point[feat])
            fragments.append(FEATURE_META[feat]["narrative"][tier].format(value=value_str))
        reason_text = fragments[0] if len(fragments) < 2 else f"{fragments[0]}, and {fragments[1]}"
        st.markdown(
            f"""
            <div style='background:{BG_CARD}; border-left:3px solid {ACCENT_2}; border-radius:6px;
                        padding:8px 10px; margin-top:6px; font-size:0.79rem; line-height:1.35;'>
              The model assessment indicates <b>{risk_label}</b> for this location. This is
              associated with {reason_text}, which contributed most to the model output.
              This reflects patterns learned from the training data, not a direct causal
              claim about flooding at this specific site.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- 3. Location details ---
    with st.container(border=True):
        section_header("3", "Location Details")

        sm = st.session_state.search_marker
        postcode_val = sm["postcode"] if (sm and not st.session_state.is_default_point) else "—"
        admin_district_val = sm.get("admin_district") if (sm and not st.session_state.is_default_point) else None
        admin_district_val = admin_district_val or "Not available for this location"

        clyde_dist = point["dist_to_clyde"]
        if clyde_dist < 100:
            clyde_line = "Right at the River Clyde"
        else:
            cx, cy = nearest_clyde_point(point["easting"], point["northing"])
            clyde_dir = compass_direction(point["easting"] - cx, point["northing"] - cy)
            clyde_line = f"{format_distance(clyde_dist)} {clyde_dir} of the River Clyde"

        details = [
            ("Postcode", postcode_val), ("Latitude", f"{point['lat']:.5f}"),
            ("Longitude", f"{point['lon']:.5f}"), ("Elevation", f"{point['elevation']:.0f}m"),
            ("Dist. to Clyde", clyde_line), ("Grid point", f"#{int(point['grid_id'])} (100m)"),
            ("Local authority", admin_district_val), ("Data source", "SEPA, OSM, NASA, HadUK-Grid"),
        ]
        # Label stacked above value (rather than a same-line label/value
        # pair) so longer values — compass direction, "Not available for
        # this location" — wrap within their own cell instead of colliding
        # with the next row.
        cells_html = "".join(
            f"<div style='padding:3px 0; border-bottom:1px solid {BORDER};'>"
            f"<div style='font-size:0.65rem; color:{TEXT_MUTED};'>{label}</div>"
            f"<div style='font-size:0.78rem; line-height:1.25;'>{value}</div></div>"
            for label, value in details
        )
        st.markdown(
            f"<div style='display:grid; grid-template-columns:1fr 1fr; gap:0 14px;'>{cells_html}</div>"
            f"<div style='font-size:0.75rem; color:{TEXT_MUTED}; margin-top:6px;'>"
            f"Nearest 100m grid point, not an exact property-level assessment.</div>",
            unsafe_allow_html=True,
        )

    # --- 4. Risk map ---
    with st.container(border=True):
        section_header("4", "Risk Map")

        filt_row1_a, filt_row1_b = st.columns(2)
        with filt_row1_a:
            selected_risks = st.multiselect(
                "Show risk levels", options=[0, 1, 2], default=[0, 1, 2],
                format_func=lambda r: f"{RISK_SWATCH[r]} {RISK_LABELS[r]}",
                key=f"selected_risks_{_fv}",
            )
        with filt_row1_b:
            clyde_dist_max = int(np.ceil(df["dist_to_clyde"].max() / 100) * 100)
            clyde_dist_range = st.slider(
                "Distance from the River Clyde", min_value=0, max_value=clyde_dist_max,
                value=(0, clyde_dist_max), step=100, format="%dm",
                key=f"clyde_dist_range_{_fv}",
            )
        district_options = ["All districts"] + sorted(postcode_districts_df["outcode"].tolist())
        selected_district = st.selectbox("Postcode district", district_options, key=f"selected_district_{_fv}")

        elevation_min = int(np.floor(df["elevation"].min()))
        elevation_max = int(np.ceil(df["elevation"].max()))
        building_max = int(df["building_count"].max())
        road_max = int(df["road_count"].max())
        wet_days_min = int(np.floor(df["wet_days_per_year"].min()))
        wet_days_max = int(np.ceil(df["wet_days_per_year"].max()))
        max_daily_min = float(df["max_daily_mm"].min())
        max_daily_max = float(df["max_daily_mm"].max())

        with st.expander("More filters"):
            elevation_range = st.slider("Elevation range", elevation_min, elevation_max, (elevation_min, elevation_max), step=1, format="%dm", key=f"elevation_range_{_fv}")
            min_confidence_pct = st.slider("Minimum classification confidence", 0, 100, 0, step=1, format="%d%%", key=f"min_confidence_pct_{_fv}")
            building_range = st.slider("Buildings within 250m", 0, building_max, (0, building_max), step=1, key=f"building_range_{_fv}")
            road_range = st.slider("Roads within 250m", 0, road_max, (0, road_max), step=1, key=f"road_range_{_fv}")
            wet_days_range = st.slider("Wet days per year", wet_days_min, wet_days_max, (wet_days_min, wet_days_max), step=1, key=f"wet_days_range_{_fv}")
            max_daily_range = st.slider("Max daily rainfall", max_daily_min, max_daily_max, (max_daily_min, max_daily_max), step=0.5, format="%.1fmm", key=f"max_daily_range_{_fv}")

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
        filtered_df = df[mask]

        m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom, tiles="cartodbpositron")
        sample = filtered_df.sample(n=min(1000, len(filtered_df)), random_state=42).reset_index(drop=True)
        if filtered_df.empty:
            st.caption("No risk levels selected — pick at least one above to show points.")
        for _, row in sample.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]], radius=4, color=RISK_COLOURS[row["predicted_risk"]],
                fill=True, fill_opacity=0.8, tooltip=RISK_LABELS[row["predicted_risk"]],
            ).add_to(m)

        if st.session_state.search_marker:
            sm2 = st.session_state.search_marker
            folium.Marker(
                location=[sm2["lat"], sm2["lon"]],
                icon=folium.Icon(color="blue", icon="search", prefix="fa"),
                tooltip=f"Nearest grid point to {sm2['postcode']}",
            ).add_to(m)

        for event in HISTORICAL_EVENTS:
            ev_lon, ev_lat = hist_transformer.transform(event["easting"], event["northing"])
            popup_html = (
                f"<b>{event['name']}</b> — {event['date']}<br>{event['caption']}<br>"
                f"<i>Source: {event['source']}</i><br>"
                f"<span style='color:#666;'>Historical record — not a model prediction.</span>"
            )
            folium.Marker(
                location=[ev_lat, ev_lon],
                icon=folium.Icon(color="darkpurple", icon="exclamation-triangle", prefix="fa"),
                tooltip=f"{event['name']} ({event['date']}) — click for details",
                popup=folium.Popup(popup_html, max_width=280),
            ).add_to(m)

        map_data = st_folium(m, height=380, use_container_width=True)
        st.caption("Purple markers = real historical flood events (1795, 1994, 2002), not model predictions.")

        clicked = map_data.get("last_object_clicked") if map_data else None
        if clicked is not None and clicked != st.session_state.last_clicked_latlng:
            st.session_state.last_clicked_latlng = clicked
            click_lat, click_lon = clicked["lat"], clicked["lng"]
            dist_sq = (sample["lat"] - click_lat) ** 2 + (sample["lon"] - click_lon) ** 2
            st.session_state.selected_point = sample.loc[dist_sq.idxmin()].copy()
            st.session_state.is_default_point = False
            st.session_state.search_marker = None
            st.rerun()

# ----------------------------------------------------------------------------
# RIGHT COLUMN
# ----------------------------------------------------------------------------
with col_right:

    # --- 5. Monthly rainfall exposure ---
    with st.container(border=True):
        section_header("5", "Monthly Rainfall Exposure", "Historical Rainfall Climatology")

        highest_row = monthly_exposure.loc[monthly_exposure["mean_mm_day"].idxmax()]
        lowest_row = monthly_exposure.loc[monthly_exposure["mean_mm_day"].idxmin()]
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.metric("Highest exposure", highest_row["month_abbr"], f"{highest_row['mean_mm_day']:.2f}mm/day")
        with mc2:
            st.metric("Lowest exposure", lowest_row["month_abbr"], f"{lowest_row['mean_mm_day']:.2f}mm/day")
        with mc3:
            st.metric("Current season", this_season, this_season_row["exposure_category"])

        fig, ax = plt.subplots(figsize=(6.4, 2.15))
        colours = [plt.cm.Blues(0.35 + 0.55 * v) for v in monthly_exposure["exposure_index"]]
        ax.bar(monthly_exposure["month_abbr"], monthly_exposure["exposure_index"], color=colours, zorder=3)
        ax.axhline(0.5, color=TEXT_MUTED, linestyle="--", linewidth=1, alpha=0.6, zorder=2)
        ax.set_ylabel("Exposure (0-1)", fontsize=8.5)
        ax.set_ylim(0, 1.05)
        ax.tick_params(axis="both", labelsize=8)
        ax.grid(axis="y", alpha=0.2, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        style_dark_chart(fig, ax)
        fig.tight_layout(pad=0.4)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        # Plain HTML table, not st.dataframe: st.dataframe renders via a
        # canvas grid whose row height/font size aren't reachable with CSS,
        # which fights the compact-table target here. The caption above it
        # is folded into the same markdown call (rather than a separate
        # st.caption()) so there's guaranteed spacing between the caption
        # text and the table header row.
        rows_html = "".join(
            f"<tr><td>{r.month_abbr}</td><td>{r.mean_mm_day:.2f}</td>"
            f"<td>{r.exposure_index:.2f}</td><td>{r.relative_level}</td></tr>"
            for r in monthly_exposure.itertuples()
        )
        st.markdown(
            f"""
            <style>
              .care-monthly-table {{ width:100%; border-collapse:collapse; font-size:0.72rem; }}
              .care-monthly-table th {{ text-align:left; color:{TEXT_MUTED}; font-weight:600;
                padding:2px 6px; border-bottom:1px solid {BORDER}; }}
              .care-monthly-table td {{ padding:2px 6px; border-bottom:1px solid {BORDER}; }}
            </style>
            <div style='font-size:0.75rem; color:{TEXT_MUTED}; margin-bottom:6px;'>
              Relative historical rainfall exposure: 0 = driest month, 1 = wettest month;
              not flood probability.
            </div>
            <table class='care-monthly-table'>
              <tr><th>Month</th><th>Avg. Rainfall (mm)</th><th>Exposure Index (0-1)</th><th>Relative Level</th></tr>
              {rows_html}
            </table>
            """,
            unsafe_allow_html=True,
        )

    # --- 6. Historical rainfall summary ---
    with st.container(border=True):
        section_header("6", "Historical Rainfall Summary", f"{HISTORICAL_RAINFALL_STATS['period_start']}–{HISTORICAL_RAINFALL_STATS['period_end']} HadUK-Grid record, area-averaged")

        wy = HISTORICAL_RAINFALL_STATS["wettest_year"]["year"]
        dy = HISTORICAL_RAINFALL_STATS["driest_year"]["year"]
        mm_stat = HISTORICAL_RAINFALL_STATS["max_month"]

        chart_col, stats_col = st.columns([1.6, 1])
        with chart_col:
            fig, ax = plt.subplots(figsize=(6.2, 2.25))
            ax.plot(annual_rainfall_df["year"], annual_rainfall_df["total_mm"], color=ACCENT_2, linewidth=1.6, zorder=3)
            ax.axhline(HISTORICAL_RAINFALL_STATS["mean_annual_mm"], color=TEXT_MUTED, linestyle="--", linewidth=1, zorder=2, label="39-yr average")
            ax.scatter([wy], [HISTORICAL_RAINFALL_STATS["wettest_year"]["total_mm"]], color=RISK_HIGH, zorder=4, label="Wettest year")
            ax.scatter([dy], [HISTORICAL_RAINFALL_STATS["driest_year"]["total_mm"]], color=ACCENT, zorder=4, label="Driest year")
            ax.set_ylabel("Annual rainfall (mm)", fontsize=8.5)
            ax.tick_params(axis="both", labelsize=7.5)
            ax.grid(axis="y", alpha=0.2, zorder=0)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            legend = ax.legend(fontsize=7.5, frameon=False, loc="upper left")
            style_dark_chart(fig, ax)
            fig.tight_layout(pad=0.4)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with stats_col:
            m2a, m2b = st.columns(2)
            with m2a:
                st.metric("Avg. annual", f"{HISTORICAL_RAINFALL_STATS['mean_annual_mm']:.0f}mm")
                st.metric("Driest yr", f"{dy}", f"{HISTORICAL_RAINFALL_STATS['driest_year']['total_mm']:.0f}mm")
            with m2b:
                st.metric("Wettest yr", f"{wy}", f"{HISTORICAL_RAINFALL_STATS['wettest_year']['total_mm']:.0f}mm")
                st.metric("Max month", f"{MONTH_ABBR[mm_stat['month']-1]} {mm_stat['year']}", f"{mm_stat['total_mm']:.0f}mm")

        _a, _b = RAINFALL_TREND["period_a"], RAINFALL_TREND["period_b"]
        _pct = (_b["annual_total_mm"] - _a["annual_total_mm"]) / _a["annual_total_mm"] * 100
        st.caption(
            f"39-yr area-averaged HadUK-Grid record (2020 has a July data gap, so its "
            f"total is understated). {_a['label']} vs {_b['label']}: annual totals up "
            f"~{_pct:.0f}%, no clear directional trend."
        )

    # --- 7. Seasonal risk overview ---
    with st.container(border=True):
        section_header("7", "Seasonal Risk Overview", "Historical rainfall-exposure categories by season — not model-predicted flood probabilities")

        s_cols = st.columns(4)
        season_desc = {
            "Low": "Rainfall here is typically lighter than other seasons at this location.",
            "Moderate": "Rainfall here sits around the middle of this location's seasonal range.",
            "High": "Rainfall here is typically heavier than other seasons at this location.",
        }
        for col, (_, srow) in zip(s_cols, seasonal_exposure.iterrows()):
            with col:
                st.markdown(
                    f"""
                    <div style='background:{BG_CARD}; border:1px solid {BORDER}; border-radius:8px;
                                padding:8px 7px; text-align:center;'>
                      <div style='font-size:1.25rem;'>{SEASON_ICONS[srow['season']]}</div>
                      <div style='font-weight:700; font-size:0.8rem;'>{srow['season']}</div>
                      <div style='font-size:0.64rem; color:{TEXT_MUTED};'>{srow['months']}</div>
                      <div style='margin-top:3px; font-weight:700; font-size:0.74rem; color:{ACCENT_2};'>
                        {srow['exposure_category']} exposure
                      </div>
                      <div style='font-size:0.64rem; color:{TEXT_MUTED}; margin-top:2px;'>
                        {season_desc[srow['exposure_category']]}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- 8. Why this result? ---
    with st.container(border=True):
        section_header("8", "Why This Result?", "Live SHAP explanation (TreeExplainer, probability space) for this exact grid point")

        st.markdown(
            "**These bars show what influenced this model classification. "
            "They do not prove what caused flooding.**"
        )

        bar_labels, value_strs, risk_dirs, colours, definitions = [], [], [], [], []
        for idx in shap_order:
            feat = FEATURE_COLS[idx]
            raw_shap = shap_vals[idx]
            risk_dir = -raw_shap if pred_class == 0 else raw_shap
            tier = tier_for(feat, point[feat])
            bar_labels.append(FEATURE_META[feat]["bar_label"][tier])
            value_strs.append(FEATURE_META[feat]["fmt"].format(point[feat]) + FEATURE_META[feat]["unit"])
            risk_dirs.append(risk_dir)
            colours.append("#C0392B" if risk_dir > 0 else "#2C6E8E")
            definitions.append((feat, FEATURE_META[feat]["definition"]))

        bar_labels, value_strs, risk_dirs, plot_colours = bar_labels[::-1], value_strs[::-1], risk_dirs[::-1], colours[::-1]

        fig, ax = plt.subplots(figsize=(7.6, 0.35 * len(bar_labels) + 0.7))
        y_pos = np.arange(len(bar_labels))
        ax.barh(y_pos, risk_dirs, color=plot_colours, height=0.6, zorder=3)
        ax.axvline(0, color=TEXT_MAIN, linewidth=1.2, zorder=4)
        max_abs = max(max(abs(v) for v in risk_dirs), 1e-9)
        ax.set_xlim(-max_abs * 1.4, max_abs * 1.65)
        for i, (v, vs) in enumerate(zip(risk_dirs, value_strs)):
            offset = max_abs * 0.04
            ax.text(v + offset if v >= 0 else v - offset, i, vs, va="center",
                     ha="left" if v >= 0 else "right", fontsize=8.5, color=TEXT_MAIN)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(bar_labels, fontsize=9)
        ax.set_xlabel("Impact on predicted risk (SHAP value, probability space)", fontsize=8.5)
        ax.tick_params(axis="x", labelsize=7.5)
        ax.grid(axis="x", alpha=0.25, zorder=0)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        legend = ax.legend(
            handles=[Patch(facecolor="#C0392B", label="Pushes risk up"), Patch(facecolor="#2C6E8E", label="Pushes risk down")],
            loc="lower right", fontsize=8, frameon=False,
        )
        for text in legend.get_texts():
            text.set_color(TEXT_MAIN)
        style_dark_chart(fig, ax)
        fig.tight_layout(pad=0.4)
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

    # --- 9. Recommendations ---
    with st.container(border=True):
        section_header("9", "Recommendations")
        precautions = PRECAUTIONS[point["predicted_risk"]]
        items_html = "".join(f"<li style='margin-bottom:2px;'>{item}</li>" for item in precautions["items"])
        st.markdown(
            f"""
            <div style='font-weight:700; margin-bottom:3px; color:{ACCENT_2}; font-size:0.85rem;'>{precautions['heading']}</div>
            <ul style='margin:0 0 6px 0; padding-left:16px; font-size:0.78rem; line-height:1.3;'>{items_html}</ul>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Source: SEPA (sepa.scot) and Ready Scotland (gov.scot) — general guidance only.")

# ============================================================================
# Footer — two compact lines rather than one long paragraph.
# ============================================================================
st.markdown("---")
st.markdown(
    f"""
    <div style='font-size:0.8rem; color:{TEXT_MUTED}; line-height:1.35;'>
      ℹ️ <b>CARE Version B</b> — MSc research prototype by Ritesh Raju Ghorpade,
      supervised by Dr Daniel Thomas (University of Strathclyde).
    </div>
    <div style='font-size:0.8rem; color:{TEXT_MUTED}; line-height:1.35; margin-top:6px;'>
      <b>Data:</b> SEPA PVA, OpenStreetMap, NASA SRTM, Met Office HadUK-Grid rainfall
      (1987–2025). Monthly/seasonal aggregates computed offline 2026-08-10 via
      003_Code/08_Rainfall_Monthly_Seasonal.py.
    </div>
    """,
    unsafe_allow_html=True,
)

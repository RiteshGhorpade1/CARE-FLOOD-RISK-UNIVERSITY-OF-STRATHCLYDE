"""
Step 3 — adds the 39-year rainfall climatology and live model inference.

Loads feature_matrix_40yr.csv (1987-2025 rainfall aggregates, replacing the
original 3-year window) and the retrained rf_model_40yr.joblib. The risk map
and side panel now show the model's live prediction for each point rather
than the precomputed flood_risk label. This build history is superseded by
care_dashboard_versionA.py / versionB.py, the final usability-study versions,
which is where the SHAP explanation panel actually landed.

Also adds postcode search: type a UK postcode, geocode it via the free
postcodes.io API, and jump to + highlight the nearest grid point.
"""

import math
from urllib.parse import quote

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
import requests
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

DATA_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/processed/feature_matrix_40yr.csv"
MODEL_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/processed/rf_model_40yr.joblib"
POSTCODES_API = "https://api.postcodes.io/postcodes/"

FEATURE_COLS = ["elevation", "dist_to_water", "dist_to_clyde", "building_count",
                "road_count", "mean_annual_mm_day", "mean_winter_mm_day",
                "wet_days_per_year", "max_daily_mm"]

UNI_X, UNI_Y = 260983, 665006  # University of Strathclyde, EPSG:27700
DEFAULT_CENTER = [55.8611, -4.2436]
DEFAULT_ZOOM = 13

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
# (002_Dataset/processed/rainfall_daily_1987_2025.parquet, 111.5M daily observations)
# rather than loaded at runtime, since the dashboard otherwise only reads the
# small aggregated feature matrix. Reproducible via a groupby on grid_id/year.
RAINFALL_TREND = {
    "period_a": {"label": "1987-2005", "n_years": 19,
                 "annual_total_mm": 1069, "wet_days_per_year": 172.5},
    "period_b": {"label": "2006-2025", "n_years": 20,
                 "annual_total_mm": 1088, "wet_days_per_year": 169.8},
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

RISK_COLOURS = {0: "#639922", 1: "#EF9F27", 2: "#E24B4A"}
RISK_LABELS = {0: "Low risk", 1: "Medium risk", 2: "High risk"}

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
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles="cartodbpositron",
    )
    sample = df.sample(n=min(1000, len(df)), random_state=42)
    sample = sample.reset_index(drop=True)
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
        st.markdown("Feature values at this location")
        feature_table = point[FEATURE_COLS].to_frame(name="value")
        st.dataframe(feature_table, use_container_width=True)
        st.caption("SHAP explanation panel added in care_dashboard_versionB.py.")

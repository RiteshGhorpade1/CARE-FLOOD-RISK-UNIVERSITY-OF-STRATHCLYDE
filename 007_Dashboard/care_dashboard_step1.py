"""
CARE Dashboard — Step 1
------------------------
Basic risk map: loads feature_matrix_with_coords.csv, renders a folium map
of a 1000-point sample colour-coded by the precomputed flood_risk label, and
adds click interaction — clicking a point updates the right-hand panel with
that point's risk level, coordinates, and feature values. No live model
inference yet — that's Step 3 (see care_dashboard_step3.py). No SHAP
explanation panel yet either.

Run with:
    python3 -m streamlit run care_dashboard_step1.py

Build-history file, kept for provenance only (see care_dashboard_versionA.py/
versionB.py for the current, maintained dashboards) — DATA_PATH below still
uses the author's original absolute filesystem path and will not run
unmodified on another machine.
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pyproj import Transformer

st.set_page_config(page_title="CARE Dashboard", layout="wide")

st.title("CARE Dashboard")
st.caption("Climate awareness and risk evaluation — Glasgow flood risk")

DATA_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/processed/feature_matrix_with_coords.csv"

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data(DATA_PATH)

@st.cache_data
def add_latlon(df):
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(df["easting"].values, df["northing"].values)
    df = df.copy()
    df["lat"] = lat
    df["lon"] = lon
    return df

df = add_latlon(df)

RISK_COLOURS = {0: "#639922", 1: "#EF9F27", 2: "#E24B4A"}
RISK_LABELS = {0: "Low risk", 1: "Medium risk", 2: "High risk"}

col_map, col_panel = st.columns([1.4, 1], gap="large")

with col_map:
    st.subheader("Risk map")

    m = folium.Map(location=[55.8611, -4.2436], zoom_start=13, tiles="cartodbpositron")

    sample = df.sample(n=min(1000, len(df)), random_state=42).reset_index(drop=True)

    for _, row in sample.iterrows():
        # Encode this point's row index in the tooltip so we can look it
        # up again after a click — a simple way to pass data back from
        # the map to Streamlit without extra libraries.
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            color=RISK_COLOURS[row["flood_risk"]],
            fill=True,
            fill_opacity=0.8,
            tooltip=RISK_LABELS[row["flood_risk"]],
        ).add_to(m)

    # st_folium returns info about the last click, including its
    # lat/lon — we use that to find the nearest point in our sample.
    map_data = st_folium(m, width=700, height=500)

with col_panel:
    st.subheader("Selected location")

    clicked = map_data.get("last_object_clicked") if map_data else None

    if clicked is None:
        st.info("Click a point on the map to see its flood risk details here.")
    else:
        # Find the sampled point closest to the click location.
        click_lat, click_lon = clicked["lat"], clicked["lng"]
        sample["dist"] = (
            (sample["lat"] - click_lat) ** 2 + (sample["lon"] - click_lon) ** 2
        )
        point = sample.loc[sample["dist"].idxmin()]

        risk_label = RISK_LABELS[point["flood_risk"]]
        badge_colour = RISK_COLOURS[point["flood_risk"]]

        st.markdown(
            f"**Coordinates:** {point['easting']:.0f} E, {point['northing']:.0f} N "
            f"&nbsp;·&nbsp; {point['lat']:.4f}°N, {point['lon']:.4f}°W"
        )
        st.markdown(
            f"<span style='background:{badge_colour}22; color:{badge_colour}; "
            f"padding:4px 12px; border-radius:6px; font-weight:600;'>{risk_label}</span>",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("**Feature values at this location**")
        feature_cols = [
            "elevation", "dist_to_water", "dist_to_clyde",
            "building_count", "road_count", "mean_annual_mm_day",
            "mean_winter_mm_day", "wet_days_per_year", "max_daily_mm",
        ]
        st.dataframe(
            point[feature_cols].to_frame(name="value"),
            use_container_width=True,
        )

        st.caption("Live model inference comes in Step 3; SHAP explanation panel after that.")
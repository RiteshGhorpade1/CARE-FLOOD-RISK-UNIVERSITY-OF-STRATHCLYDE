import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pyproj import Transformer

st.set_page_config(page_title="CARE Dashboard", layout="wide")
st.title("CARE Dashboard")
st.caption("Climate awareness and risk evaluation — Glasgow flood risk")

DATA_PATH = "/Users/riteshghorpade/Documents/010_Project/002_Dataset/feature_matrix_with_coords.csv"

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
    sample = df.sample(n=min(1000, len(df)), random_state=42)
    sample = sample.reset_index(drop=True)
    for _, row in sample.iterrows():
        marker = folium.CircleMarker(location=[row["lat"], row["lon"]], radius=4, color=RISK_COLOURS[row["flood_risk"]], fill=True, fill_opacity=0.8, tooltip=RISK_LABELS[row["flood_risk"]])
        marker.add_to(m)
    map_data = st_folium(m, width=700, height=500)

with col_panel:
    st.subheader("Selected location")
    clicked = None
    if map_data:
        clicked = map_data.get("last_object_clicked")

    if clicked is None:
        st.info("Click a point on the map to see its flood risk details here.")
    else:
        click_lat = clicked["lat"]
        click_lon = clicked["lng"]
        lat_diff = sample["lat"] - click_lat
        lon_diff = sample["lon"] - click_lon
        sample["dist"] = lat_diff ** 2 + lon_diff ** 2
        best_idx = sample["dist"].idxmin()
        point = sample.loc[best_idx]

        risk_label = RISK_LABELS[point["flood_risk"]]
        badge_colour = RISK_COLOURS[point["flood_risk"]]

        coord_text = "Coordinates: " + str(round(point["easting"])) + " E, " + str(round(point["northing"])) + " N"
        st.markdown(coord_text)

        badge_html = "<span style='background:" + badge_colour + "22; color:" + badge_colour + "; padding:4px 12px; border-radius:6px; font-weight:600;'>" + risk_label + "</span>"
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("Feature values at this location")
        feature_cols = ["elevation", "dist_to_water", "dist_to_clyde", "building_count", "road_count", "mean_annual_mm_day", "mean_winter_mm_day", "wet_days_per_year", "max_daily_mm"]
        feature_table = point[feature_cols].to_frame(name="value")
        st.dataframe(feature_table, use_container_width=True)
        st.caption("SHAP explanation panel comes in Step 3.")

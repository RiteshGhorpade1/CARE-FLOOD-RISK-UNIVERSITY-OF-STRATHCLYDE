

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "006_Dissertation" / "figures"

THEME_PRIMARY = '#1E7A8C'
THEME_LIGHT = '#EAF3F5'
THEME_MED = '#7FB3C2'
THEME_TEXT = '#1B2A33'
WARN = '#B5651D'
RISK_COLORS = {0: '#639922', 1: '#EF9F27', 2: '#E24B4A'}

plt.rcParams.update({"font.family": "sans-serif", "text.color": THEME_TEXT})


def draw_box(ax, x, y, w, h, heading, body, facecolor, edgecolor=THEME_PRIMARY,
             heading_size=14, body_size=10.5, textcolor=THEME_TEXT, heading_only=False):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
                          facecolor=facecolor, edgecolor=edgecolor, linewidth=1.8)
    ax.add_patch(box)
    if heading_only:
        ax.text(x + w / 2, y + h / 2, heading, ha='center', va='center',
                fontsize=heading_size, fontweight='bold', color=textcolor, wrap=True)
    else:
        ax.text(x + w / 2, y + h * 0.68, heading, ha='center', va='center',
                fontsize=heading_size, fontweight='bold', color=textcolor, wrap=True)
        ax.text(x + w / 2, y + h * 0.30, body, ha='center', va='center',
                fontsize=body_size, color=textcolor, wrap=True)


def v_arrow(ax, x, y_top, y_bottom, color=THEME_PRIMARY, lw=2.5):
    ax.annotate('', xy=(x, y_bottom), xytext=(x, y_top),
                arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, mutation_scale=20))


def h_arrow(ax, x_left, x_right, y, color=THEME_PRIMARY, lw=2.5):
    ax.annotate('', xy=(x_right, y), xytext=(x_left, y),
                arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, mutation_scale=20))


def vertical_flow(title, stages, save_path, width=11, box_h=1.5, gap=0.5, subtitle=None):
    n = len(stages)
    h = 1.3 + (0.55 if subtitle else 0) + n * (box_h + gap)
    fig, ax = plt.subplots(figsize=(width, h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, h)
    ax.axis('off')
    ax.text(0.2, h - 0.35, title, fontsize=16.5, fontweight='bold', color=THEME_TEXT, ha='left')
    if subtitle:
        ax.text(0.2, h - 0.75, subtitle, fontsize=10.5, color=THEME_TEXT, ha='left', style='italic')

    y = h - (1.15 if subtitle else 0.85)
    for i, (heading, body) in enumerate(stages):
        color = THEME_LIGHT if i % 2 == 0 else THEME_MED
        draw_box(ax, 0.5, y - box_h, 9.0, box_h, heading, body, facecolor=color)
        if i > 0:
            v_arrow(ax, 5.0, y + gap - 0.02, y)
        y -= (box_h + gap)

    plt.tight_layout()
    plt.savefig(save_path, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {save_path}")



# Figure 2.1 — Literature conceptual framework (radial layout)


fig, ax = plt.subplots(figsize=(10, 10))
ax.set_xlim(-6.2, 6.2)
ax.set_ylim(-6.2, 6.2)
ax.axis('off')
ax.set_title("Literature review conceptual framework", fontsize=16.5, fontweight='bold', pad=10)

draw_box(ax, -1.7, -0.75, 3.4, 1.5, "CARE system", "design decisions", facecolor=THEME_PRIMARY,
         textcolor='white', heading_size=14, body_size=10.5)

import numpy as np
themes = [
    ("Flood risk\nprediction (ML)", "§2.2"),
    ("Environmental\ndecision support", "§2.3"),
    ("Geospatial\nanalysis (GIS)", "§2.4"),
    ("Recommendation\nsystems", "§2.5"),
    ("Risk communication\npsychology", "§2.5"),
    ("HCI / usability\nevaluation", "§2.3, §2.5"),
]
radius = 4.6
box_w, box_h = 2.9, 1.5
n = len(themes)
for i, (label, sec) in enumerate(themes):
    angle = np.pi / 2 + i * (2 * np.pi / n)
    cx, cy = radius * np.cos(angle), radius * np.sin(angle)
    color = THEME_LIGHT if i % 2 == 0 else THEME_MED
    draw_box(ax, cx - box_w / 2, cy - box_h / 2, box_w, box_h, label, sec, facecolor=color,
              heading_size=11, body_size=9.5)
    # connecting line from theme box edge to central box edge
    inner_x = (box_w / 2 - 0.15) * np.cos(angle + np.pi)
    inner_y = (box_h / 2 - 0.15) * np.sin(angle + np.pi)
    ax.plot([cx + inner_x * 0, cx * 0.30], [cy + inner_y * 0, cy * 0.30],
            color=THEME_PRIMARY, lw=1.6, alpha=0.7, zorder=0,
            solid_capstyle='round')
    ax.plot([cx, cx * 0.28], [cy, cy * 0.28], color=THEME_PRIMARY, lw=1.6, alpha=0.7, zorder=0)

plt.tight_layout()
plt.savefig(f"{OUT}/figure_2_1_literature_framework.png", dpi=220, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved figure_2_1_literature_framework.png")


# Data integration workflow (§3.2.4)


vertical_flow(
    "Data integration workflow",
    [
        ("Four raw sources, four native formats",
         "SEPA PVA (GeoPackage) · OSM buildings/roads/water (GeoPackage) · NASA SRTM (raster) · HadUK-Grid rainfall (NetCDF)"),
        ("CRS harmonisation",
         "Every source's coordinate system verified explicitly against EPSG:27700 before any join, buffer or distance calculation"),
        ("100m regular study grid",
         "7,843 points generated across the 5km study circle — the fixed unit of analysis for every downstream step"),
        ("Spatial joins",
         "Nearest-neighbour (raster sources) or exact containment (vector sources); every join sample-checked before running at full scale"),
        ("Feature dataset",
         "feature_matrix_with_coords.csv — 7,843 rows × 9 features, zero missing values"),
    ],
    f"{OUT}/figure_3_data_integration_workflow.png",
)


# Feature engineering pipeline, grouped by category 3.3)


fig, ax = plt.subplots(figsize=(11, 8.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8.5)
ax.axis('off')
ax.text(0.2, 8.15, "Feature engineering pipeline", fontsize=16.5, fontweight='bold', ha='left')

groups = [
    ("Terrain", "elevation", THEME_LIGHT),
    ("Hydrology", "dist_to_water\ndist_to_clyde", THEME_MED),
    ("Built\nenvironment", "building_count\nroad_count\n(within 250m)", THEME_LIGHT),
    ("Rainfall /\nclimate (39yr)", "mean_annual_mm_day\nmean_winter_mm_day\nwet_days_per_year\nmax_daily_mm", THEME_MED),
]
box_w = 2.15
gap = 0.15
x = 0.3
for heading, body, color in groups:
    draw_box(ax, x, 5.2, box_w, 2.3, heading, body, facecolor=color, heading_size=11, body_size=8.3)
    x += box_w + gap

for gx in [0.3 + box_w / 2 + i * (box_w + gap) for i in range(4)]:
    v_arrow(ax, gx, 5.15, 4.55, lw=1.8)

draw_box(ax, 1.5, 3.0, 7.0, 1.4, "100m study grid (7,843 points)",
         "each point attached one value per feature above", facecolor=THEME_PRIMARY,
         textcolor='white', heading_size=13)
v_arrow(ax, 5.0, 2.95, 2.35)
draw_box(ax, 1.5, 0.9, 7.0, 1.4, "Feature matrix",
         "7,843 × 9 features → flood_risk label (Section 3.3.4)", facecolor=THEME_LIGHT,
         heading_size=13)

plt.tight_layout()
plt.savefig(f"{OUT}/figure_3_feature_pipeline.png", dpi=220, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved figure_3_feature_pipeline.png")


# Risk-label construction logic — engineered label vs observed outcome (3.3.4)


fig, ax = plt.subplots(figsize=(10.5, 8.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8.5)
ax.axis('off')
ax.text(0.2, 8.15, "Flood-risk label construction", fontsize=16.5, fontweight='bold', ha='left')

draw_box(ax, 1.0, 6.5, 8.0, 1.2, "Inputs",
         "SEPA PVA zone membership (within / outside)  +  NASA SRTM elevation (m)",
         facecolor=THEME_LIGHT, heading_size=12.5, body_size=10)
v_arrow(ax, 5.0, 6.45, 5.85)

rule_y = 4.2
draw_box(ax, 0.3, rule_y, 3.0, 1.5, "Outside any PVA zone\n(any elevation)", "→ Low risk (0)",
         facecolor='#639922', textcolor='white', heading_size=10.5, body_size=10.5)
draw_box(ax, 3.5, rule_y, 3.0, 1.5, "Inside a PVA zone\nelevation ≤ 35m", "→ Medium risk (1)",
         facecolor='#EF9F27', textcolor='white', heading_size=10.5, body_size=10.5)
draw_box(ax, 6.7, rule_y, 3.0, 1.5, "Inside a PVA zone\nelevation ≤ 15m", "→ High risk (2)",
         facecolor='#E24B4A', textcolor='white', heading_size=10.5, body_size=10.5)
for cx in [1.8, 5.0, 8.2]:
    v_arrow(ax, cx, 5.8, rule_y + 1.55, lw=1.6)

banner_y = 1.1
box = FancyBboxPatch((0.3, banner_y), 9.4, 2.3, boxstyle="round,pad=0.03,rounding_size=0.03",
                      facecolor='#FBEFE3', edgecolor=WARN, linewidth=2.2)
ax.add_patch(box)
ax.text(5.0, banner_y + 1.75, "ENGINEERED LABEL", fontsize=14, fontweight='bold', color=WARN, ha='center')
ax.text(5.0, banner_y + 1.2,
        "flood_risk is constructed deterministically from these two rules.",
        fontsize=10.5, color=THEME_TEXT, ha='center')
ax.text(5.0, banner_y + 0.7,
        "It is NOT an independently observed flood outcome — the model in Chapter 4\n"
        "is evaluated against this constructed label, not against historical flood records.",
        fontsize=10.5, color=THEME_TEXT, ha='center')
v_arrow(ax, 5.0, rule_y - 0.05, banner_y + 2.35, lw=1.6)

plt.tight_layout()
plt.savefig(f"{OUT}/figure_3_risk_label_construction.png", dpi=220, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved figure_3_risk_label_construction.png")


# Machine learning pipeline overview (3.4.2)


vertical_flow(
    "Machine learning pipeline",
    [
        ("Feature matrix", "7,843 x 9 features -> flood_risk label (Section 3.3.4)"),
        ("Stratified 80/20 split", "6,274 train / 1,569 test points, random_state=42"),
        ("Random Forest (primary)", "n_estimators=100, random_state=42 -- benchmarked against XGBoost, same split"),
        ("Four evaluation strategies", "held-out test set * random 5-fold CV * spatial-block 5-fold CV (500m tiles) * 3yr-rainfall snapshot re-run"),
        ("Metrics (Chapter 4)", "accuracy, macro F1, per-class precision/recall/F1, confusion matrix, ROC-AUC"),
    ],
    f"{OUT}/figure_3_ml_pipeline.png",
)


# Dashboard (Streamlit app) internal architecture (3.6.1)


vertical_flow(
    "CARE dashboard internal architecture",
    [
        ("Data / API layer",
         "feature_matrix_with_coords.csv (cached via st.cache_data) · postcodes.io API for postcode search"),
        ("Model layer",
         "rf_model_40yr.joblib loaded once (st.cache_resource); predict()/predict_proba() run for all 7,843 points at startup"),
        ("SHAP layer (Version B only)",
         "TreeExplainer (st.cache_resource) computes probability-space SHAP values live, per click, in single-digit ms"),
        ("Recommendation layer",
         "Deterministic rule-based mapping from predicted risk class to source-cited guidance (Section 3.6.3)"),
        ("Frontend",
         "Streamlit + folium/streamlit_folium interactive map, session_state for selection/filter state, blue/teal theme"),
    ],
    f"{OUT}/figure_3_dashboard_architecture.png",
)


# Recommendation engine logic (3.6.3) — three parallel branches


fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.5)
ax.axis('off')
ax.text(0.2, 6.15, "Recommendation engine logic", fontsize=16.5, fontweight='bold', ha='left')

draw_box(ax, 3.0, 4.7, 4.0, 1.1, "Predicted risk class", "(Section 4.2)", facecolor=THEME_PRIMARY,
         textcolor='white', heading_size=12.5, body_size=10)

low_body = "Map-checking framed around business/\nlong-term planning, not immediate risk —\ndeliberately different in kind, not degree"
med_body = "Precautionary version of High-risk\nguidance: check maps, know Floodline"
high_body = "Check SEPA maps · register with Floodline\n· resilience measures (Scottish Flood Forum)\n· insurance incl. Flood Re"

draw_box(ax, 0.2, 2.2, 3.0, 1.85, "Low risk", low_body, facecolor='#639922', textcolor='white',
         heading_size=12.5, body_size=8.8)
draw_box(ax, 3.5, 2.2, 3.0, 1.85, "Medium risk", med_body, facecolor='#EF9F27', textcolor='white',
         heading_size=12.5, body_size=8.8)
draw_box(ax, 6.8, 2.2, 3.0, 1.85, "High risk", high_body, facecolor='#E24B4A', textcolor='white',
         heading_size=12.5, body_size=8.8)

for cx in [1.7, 5.0, 8.3]:
    ax.annotate('', xy=(cx, 4.05), xytext=(5.0, 4.65),
                arrowprops=dict(arrowstyle='-|>', color=THEME_PRIMARY, lw=1.8, mutation_scale=18))

box = FancyBboxPatch((0.2, 0.4), 9.6, 1.35, boxstyle="round,pad=0.03,rounding_size=0.03",
                      facecolor=THEME_LIGHT, edgecolor=THEME_PRIMARY, linewidth=1.8)
ax.add_patch(box)
ax.text(5.0, 1.35, "Every recommendation is source-cited (SEPA / Ready Scotland),", fontsize=10, ha='center')
ax.text(5.0, 0.9, "never presented as the dashboard's own unsupported advice (Section 2.5)", fontsize=10, ha='center')

plt.tight_layout()
plt.savefig(f"{OUT}/figure_3_recommendation_logic.png", dpi=220, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved figure_3_recommendation_logic.png")


# User journey (3.6.4 / new)


vertical_flow(
    "CARE user journey",
    [
        ("1. Enter postcode", "or click directly on the interactive map"),
        ("2. Locate area", "map centres and highlights the nearest 100m grid point"),
        ("3. View risk classification", "Low / Medium / High badge, using the fixed colour convention"),
        ("4. Understand confidence", "predict_proba()-based confidence indicator, always visible alongside the badge"),
        ("5. Understand explanation (Version B)", "\"Why am I seeing this result?\" → SHAP panel naming the top driving features"),
        ("6. Read recommendations", "differentiated, source-cited guidance for that specific risk class"),
        ("7. Take appropriate action", "e.g. check SEPA's official maps, register with Floodline"),
    ],
    f"{OUT}/figure_3_user_journey.png",
    box_h=1.25, gap=0.4,
)


# Chapter 4 — Testing coverage (honest: informal verification, NOT a
# fabricated automated PASS/FAIL suite)


vertical_flow(
    "System verification coverage",
    [
        ("Input validation", "Postcode lookup: invalid/malformed postcodes, network failures and\nout-of-area results each caught and reported with a specific message"),
        ("Data processing", "Path-availability checks for every source file (01_Data_Collection.ipynb);\nzero-missing-values check and CRS verification after every join (Section 3.2.4)"),
        ("Model inference", "Reproducible retraining (fixed random_state=42) cross-checked against\nsaved model output; predictions sanity-checked across the full grid"),
        ("SHAP explanation", "Live per-click computation benchmarked at single-digit ms (Section 3.5.3);\nwaterfall totals checked to sum to the predicted probability"),
        ("Recommendation engine", "Manual check that every risk class maps to distinct, source-cited guidance"),
        ("Dashboard interaction", "Manual interactive testing through each build-history stage\n(step1 → step3 → Version A/B), across the intended user tasks"),
    ],
    f"{OUT}/figure_4_testing_coverage.png",
    subtitle="Informal, manual/notebook-based verification performed during development —\nno automated test suite or logged PASS/FAIL matrix exists for this project (see Section 4.6.1).",
)

print("\nAll conceptual diagrams complete.")

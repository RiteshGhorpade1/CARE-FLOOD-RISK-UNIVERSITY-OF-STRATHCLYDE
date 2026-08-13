

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, GroupKFold, cross_validate
from sklearn.metrics import (classification_report, confusion_matrix, accuracy_score,
                              f1_score, roc_curve, auc)
from sklearn.preprocessing import label_binarize
from xgboost import XGBClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE = PROJECT_ROOT / "002_Dataset"
FEATURE_CSV = BASE / "processed" / "feature_matrix.csv"
FEATURE_CSV_3YR = BASE / "processed" / "feature_matrix_3yr.csv"
FEATURE_CSV_COORDS = BASE / "processed" / "feature_matrix_with_coords.csv"
MODEL_PATH = BASE / "processed" / "rf_model_40yr.joblib"
RAINFALL_PARQUET = BASE / "processed" / "rainfall_daily_1987_2025.parquet"
OUT = BASE / "outputs"
DISS_FIG = PROJECT_ROOT / "006_Dissertation" / "figures"

FEATURE_COLS = ['elevation', 'dist_to_water', 'dist_to_clyde',
                'building_count', 'road_count', 'mean_annual_mm_day',
                'mean_winter_mm_day', 'wet_days_per_year', 'max_daily_mm']
CLASS_NAMES = ['Low risk', 'Medium risk', 'High risk']

# Project-wide visual conventions (see .streamlit/config.toml)
RISK_COLORS = {0: '#639922', 1: '#EF9F27', 2: '#E24B4A'}
RISK_HEX = [RISK_COLORS[0], RISK_COLORS[1], RISK_COLORS[2]]
THEME_PRIMARY = '#1E7A8C'
THEME_LIGHT = '#EAF3F5'
THEME_MED = '#7FB3C2'
THEME_TEXT = '#1B2A33'
WARN = '#B5651D'

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.edgecolor": THEME_TEXT,
    "text.color": THEME_TEXT,
    "axes.labelcolor": THEME_TEXT,
    "xtick.color": THEME_TEXT,
    "ytick.color": THEME_TEXT,
})



# Shared box/arrow diagram helpers (matches figure_1_1 / figure_1_2 style)


def draw_box(ax, x, y, w, h, heading, body, facecolor, edgecolor=THEME_PRIMARY,
             heading_size=15, body_size=11.5, textcolor=THEME_TEXT):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
                          facecolor=facecolor, edgecolor=edgecolor, linewidth=1.8)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.68, heading, ha='center', va='center',
            fontsize=heading_size, fontweight='bold', color=textcolor, wrap=True)
    ax.text(x + w / 2, y + h * 0.32, body, ha='center', va='center',
            fontsize=body_size, color=textcolor, wrap=True)


def draw_vertical_arrow(ax, x, y_top, y_bottom, color=THEME_PRIMARY):
    ax.annotate('', xy=(x, y_bottom), xytext=(x, y_top),
                arrowprops=dict(arrowstyle='-|>', color=color, lw=2.5, mutation_scale=22))


def draw_horizontal_arrow(ax, x_left, x_right, y, color=THEME_PRIMARY):
    ax.annotate('', xy=(x_right, y), xytext=(x_left, y),
                arrowprops=dict(arrowstyle='-|>', color=color, lw=2.5, mutation_scale=22))


def vertical_flow_diagram(title, stages, save_path, figsize=(11, None), box_h=1.55, gap=0.55):
    n = len(stages)
    h = figsize[1] or (1.0 + n * (box_h + gap))
    fig, ax = plt.subplots(figsize=(figsize[0], h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, h)
    ax.axis('off')
    ax.text(0.2, h - 0.35, title, fontsize=17, fontweight='bold', color=THEME_TEXT, ha='left')

    y = h - 1.0
    for i, (heading, body) in enumerate(stages):
        color = THEME_LIGHT if i % 2 == 0 else THEME_MED
        draw_box(ax, 0.5, y - box_h, 9.0, box_h, heading, body, facecolor=color)
        if i > 0:
            draw_vertical_arrow(ax, 5.0, y + gap - 0.02, y)
        y -= (box_h + gap)

    plt.tight_layout()
    plt.savefig(save_path, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {save_path}")



# 1. Load data / retrain models identically to 04_ML_Model.ipynb


print("Loading data and reproducing the notebook's exact train/test split...")
df = pd.read_csv(FEATURE_CSV)
df_coords = pd.read_csv(FEATURE_CSV_COORDS)
assert len(df_coords) == len(df)
assert np.allclose(df_coords['elevation'].values, df['elevation'].values)

X = df[FEATURE_COLS]
y = df['flood_risk']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)

rf_acc = accuracy_score(y_test, y_pred)
rf_f1_macro = f1_score(y_test, y_pred, average='macro')
report = classification_report(y_test, y_pred, target_names=CLASS_NAMES, output_dict=True)
print(f"RF test accuracy {rf_acc:.4f}, macro F1 {rf_f1_macro:.4f} (should match Table 3.1/3.2 in draft)")

xgb = XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1, eval_metric='mlogloss')
xgb.fit(X_train, y_train)
xgb_pred = xgb.predict(X_test)
xgb_acc = accuracy_score(y_test, xgb_pred)
xgb_f1_macro = f1_score(y_test, xgb_pred, average='macro')
print(f"XGBoost test accuracy {xgb_acc:.4f}, macro F1 {xgb_f1_macro:.4f}")


def run_pipeline(csv_path):
    d = pd.read_csv(csv_path)
    Xd, yd = d[FEATURE_COLS], d['flood_risk']
    Xd_tr, Xd_te, yd_tr, yd_te = train_test_split(Xd, yd, test_size=0.2, random_state=42, stratify=yd)
    m = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    m.fit(Xd_tr, yd_tr)
    p = m.predict(Xd_te)
    return accuracy_score(yd_te, p), f1_score(yd_te, p, average='macro')


rf3_acc, rf3_f1 = run_pipeline(FEATURE_CSV_3YR)
print(f"RF (3yr rainfall) test accuracy {rf3_acc:.4f}, macro F1 {rf3_f1:.4f}")


# 2. Figure 4.6 — Model accuracy / macro-F1 comparison (RF vs XGB vs RF-3yr)


fig, ax = plt.subplots(figsize=(8, 5.5))
models = ['Random Forest\n(39yr, primary)', 'XGBoost\n(39yr)', 'Random Forest\n(3yr rainfall)']
acc_vals = [rf_acc, xgb_acc, rf3_acc]
f1_vals = [rf_f1_macro, xgb_f1_macro, rf3_f1]
x = np.arange(3)
w = 0.32
ax.bar(x - w / 2, [v * 100 for v in acc_vals], width=w, label='Accuracy', color=THEME_PRIMARY)
ax.bar(x + w / 2, [v * 100 for v in f1_vals], width=w, label='Macro F1', color=THEME_MED)
for i, v in enumerate(acc_vals):
    ax.text(i - w / 2, v * 100 + 0.08, f"{v*100:.2f}%", ha='center', fontsize=9.5)
for i, v in enumerate(f1_vals):
    ax.text(i + w / 2, v * 100 + 0.08, f"{v*100:.2f}%", ha='center', fontsize=9.5)
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=10.5)
ax.set_ylabel("Score (%)")
ax.set_ylim(98.5, 100.15)
ax.set_title("Model accuracy and macro F1 — Random Forest vs XGBoost vs 3-year-rainfall RF",
             fontsize=12.5, fontweight='bold')
ax.legend(loc='lower right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/model_accuracy_f1_comparison.png", dpi=220, facecolor='white')
plt.close()
print("Saved model_accuracy_f1_comparison.png")


# 3. Figure 4.2 — Validation strategy comparison (test / random CV / spatial CV)


skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
rf_cv = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
random_cv = cross_validate(rf_cv, X, y, cv=skf,
                            scoring={'accuracy': 'accuracy', 'f1_macro': 'f1_macro'}, n_jobs=-1)
random_cv_acc_mean, random_cv_acc_std = random_cv['test_accuracy'].mean(), random_cv['test_accuracy'].std()
random_cv_f1_mean, random_cv_f1_std = random_cv['test_f1_macro'].mean(), random_cv['test_f1_macro'].std()

BLOCK_SIZE_M = 500
block_x = (df_coords['easting'] // BLOCK_SIZE_M).astype(int)
block_y = (df_coords['northing'] // BLOCK_SIZE_M).astype(int)
block_id = (block_x.astype(str) + "_" + block_y.astype(str)).values

gkf = GroupKFold(n_splits=5)
spatial_acc, spatial_f1 = [], []
for train_idx, test_idx in gkf.split(X, y, groups=block_id):
    m = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    m.fit(X.iloc[train_idx], y.iloc[train_idx])
    p = m.predict(X.iloc[test_idx])
    spatial_acc.append(accuracy_score(y.iloc[test_idx], p))
    spatial_f1.append(f1_score(y.iloc[test_idx], p, average='macro'))
spatial_cv_acc_mean, spatial_cv_acc_std = np.mean(spatial_acc), np.std(spatial_acc)
spatial_cv_f1_mean, spatial_cv_f1_std = np.mean(spatial_f1), np.std(spatial_f1)
print(f"Random 5-fold CV acc {random_cv_acc_mean:.4f}+-{random_cv_acc_std:.4f}, "
      f"spatial-block CV acc {spatial_cv_acc_mean:.4f}+-{spatial_cv_acc_std:.4f}")

fig, ax = plt.subplots(figsize=(8, 5.5))
strategies = ['Held-out\ntest set\n(single split)', 'Random\n5-fold CV', 'Spatial-block\n5-fold CV\n(500m tiles)']
means = [rf_acc * 100, random_cv_acc_mean * 100, spatial_cv_acc_mean * 100]
errs = [0, random_cv_acc_std * 100, spatial_cv_acc_std * 100]
bars = ax.bar(strategies, means, yerr=errs, capsize=6, color=[THEME_PRIMARY, THEME_MED, WARN], alpha=0.9)
for i, v in enumerate(means):
    ax.text(i, v + errs[i] + 0.05, f"{v:.2f}%", ha='center', fontsize=10.5, fontweight='bold')
ax.set_ylabel("Accuracy (%)")
ax.set_ylim(98.0, 100.2)
ax.set_title("Validation strategy comparison — does spatial autocorrelation inflate the score?",
             fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/validation_strategy_comparison.png", dpi=220, facecolor='white')
plt.close()
print("Saved validation_strategy_comparison.png")


# 4. Figure 4.4 — Per-class precision/recall/F1 grouped bar chart


fig, ax = plt.subplots(figsize=(8.5, 5.5))
metrics = ['precision', 'recall', 'f1-score']
x = np.arange(len(CLASS_NAMES))
w = 0.25
colors = [THEME_PRIMARY, THEME_MED, WARN]
for i, met in enumerate(metrics):
    vals = [report[c][met] * 100 for c in CLASS_NAMES]
    ax.bar(x + (i - 1) * w, vals, width=w, label=met.capitalize(), color=colors[i])
ax.set_xticks(x)
ax.set_xticklabels(CLASS_NAMES)
ax.set_ylabel("Score (%)")
ax.set_ylim(97, 101)
ax.set_title("Random Forest per-class precision, recall and F1 (held-out test set)",
             fontsize=12.5, fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/per_class_prf1.png", dpi=220, facecolor='white')
plt.close()
print("Saved per_class_prf1.png")


# 5. Figure 4.3 — ROC curves (regenerated + AUC csv for traceability)


y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
fig, ax = plt.subplots(figsize=(7, 6.5))
auc_rows = []
for i, name in enumerate(CLASS_NAMES):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.4f})", color=RISK_HEX[i], lw=2.2)
    auc_rows.append({"class": name, "auc": roc_auc})
ax.plot([0, 1], [0, 1], linestyle='--', color='grey', lw=1)
ax.set_xlabel("False positive rate")
ax.set_ylabel("True positive rate")
ax.set_title("One-vs-rest ROC curves per risk class\n(regenerated from the saved train/test split)",
             fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=9.5)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/roc_curves.png", dpi=220, facecolor='white')
plt.close()
pd.DataFrame(auc_rows).to_csv(f"{OUT}/roc_auc_values.csv", index=False)
print("Saved roc_curves.png + roc_auc_values.csv")


# 6. Figure 4.9 / 4.10 — Spatial risk map & spatial confidence map (full grid)


saved_model = joblib.load(MODEL_PATH)
X_full = df_coords[FEATURE_COLS]
full_pred = saved_model.predict(X_full)
full_proba = saved_model.predict_proba(X_full)
full_conf = full_proba.max(axis=1)

fig, ax = plt.subplots(figsize=(8, 8))
for cls in [0, 1, 2]:
    mask = full_pred == cls
    ax.scatter(df_coords.loc[mask, 'easting'], df_coords.loc[mask, 'northing'],
               s=9, color=RISK_COLORS[cls], label=CLASS_NAMES[cls], alpha=0.85, linewidths=0)
ax.set_aspect('equal')
ax.set_xlabel("Easting (m, EPSG:27700)")
ax.set_ylabel("Northing (m, EPSG:27700)")
ax.set_title(f"Predicted flood-risk class across the {len(df_coords):,}-point study grid",
             fontsize=12.5, fontweight='bold')
ax.legend(loc='upper right', markerscale=2.2, fontsize=10)
plt.tight_layout()
plt.savefig(f"{OUT}/spatial_risk_map.png", dpi=220, facecolor='white')
plt.close()
print("Saved spatial_risk_map.png")

fig, ax = plt.subplots(figsize=(8.5, 8))
sc = ax.scatter(df_coords['easting'], df_coords['northing'], c=full_conf, s=9,
                 cmap='viridis', alpha=0.9, linewidths=0, vmin=0.5, vmax=1.0)
ax.set_aspect('equal')
ax.set_xlabel("Easting (m, EPSG:27700)")
ax.set_ylabel("Northing (m, EPSG:27700)")
ax.set_title("Spatial distribution of model prediction confidence\n(max predicted class probability per point)",
             fontsize=12.5, fontweight='bold')
cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Predicted-class probability")
plt.tight_layout()
plt.savefig(f"{OUT}/spatial_confidence_map.png", dpi=220, facecolor='white')
plt.close()
print(f"Saved spatial_confidence_map.png (mean confidence {full_conf.mean():.4f}, "
      f"min {full_conf.min():.4f})")


# 7. Figure 4.11 — Elevation and distance-to-Clyde by risk class


fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
for ax, col, ylabel in zip(axes, ['elevation', 'dist_to_clyde'],
                           ['Elevation (m)', 'Distance to River Clyde (m)']):
    data = [df.loc[df['flood_risk'] == cls, col].values for cls in [0, 1, 2]]
    bp = ax.boxplot(data, labels=CLASS_NAMES, patch_artist=True, showfliers=False)
    for patch, cls in zip(bp['boxes'], [0, 1, 2]):
        patch.set_facecolor(RISK_COLORS[cls])
        patch.set_alpha(0.75)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', alpha=0.3)
fig.suptitle("Elevation and distance-to-Clyde by risk class (7,843-point study grid)",
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUT}/elevation_distance_vs_risk.png", dpi=220, facecolor='white')
plt.close()
print("Saved elevation_distance_vs_risk.png")


# 8. Figure 4.12 — 39-year rainfall trend (real annual aggregation)


print("Aggregating 39-year daily rainfall parquet (this may take a minute)...")
rain = pd.read_parquet(RAINFALL_PARQUET, columns=['date', 'rainfall_mm'])
rain['date'] = pd.to_datetime(rain['date'])
rain['year'] = rain['date'].dt.year
rain['rainfall_mm'] = rain['rainfall_mm'].astype('float32')

annual_mean = rain.groupby('year')['rainfall_mm'].mean()
rain['wet'] = (rain['rainfall_mm'] >= 1.0)
annual_wet_frac = rain.groupby('year')['wet'].mean()
annual_wet_days = annual_wet_frac * 365
annual_domain_max = rain.groupby('year')['rainfall_mm'].max()
del rain

fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
axes[0].plot(annual_mean.index, annual_mean.values, color=THEME_PRIMARY, marker='o', ms=3)
axes[0].set_ylabel("Mean daily\nrainfall (mm)")
axes[1].plot(annual_wet_days.index, annual_wet_days.values, color=THEME_MED, marker='o', ms=3)
axes[1].set_ylabel("Wet days\n(≥1.0mm) / yr")
axes[2].plot(annual_domain_max.index, annual_domain_max.values, color=WARN, marker='o', ms=3)
axes[2].set_ylabel("Domain-wide max\ndaily rainfall (mm)")
axes[2].set_xlabel("Year")
for ax in axes:
    ax.grid(alpha=0.3)
fig.suptitle("HadUK-Grid rainfall over the Glasgow study area, 1987–2025 (39 years)",
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUT}/rainfall_39yr_trend.png", dpi=220, facecolor='white')
plt.close()
print(f"Saved rainfall_39yr_trend.png (years {annual_mean.index.min()}-{annual_mean.index.max()}, "
      f"mean daily rainfall range {annual_mean.min():.2f}-{annual_mean.max():.2f} mm)")


# 9. Figure 4.13 — 39-year vs 3-year rainfall FEATURE distribution comparison


df_3yr = pd.read_csv(FEATURE_CSV_3YR)
rain_feats = ['mean_annual_mm_day', 'mean_winter_mm_day', 'wet_days_per_year', 'max_daily_mm']
fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))
for ax, feat in zip(axes, rain_feats):
    ax.hist(df[feat], bins=25, alpha=0.6, label='39yr (1987-2025)', color=THEME_PRIMARY, density=True)
    ax.hist(df_3yr[feat], bins=25, alpha=0.6, label='3yr (2023-2025)', color=WARN, density=True)
    ax.set_title(feat, fontsize=10)
    ax.grid(alpha=0.3)
axes[0].legend(fontsize=8)
fig.suptitle("39-year vs 3-year rainfall feature distributions across the study grid",
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUT}/rainfall_39yr_vs_3yr_features.png", dpi=220, facecolor='white')
plt.close()
print("Saved rainfall_39yr_vs_3yr_features.png")

print("\nAll Chapter 4 data-driven figures complete.")

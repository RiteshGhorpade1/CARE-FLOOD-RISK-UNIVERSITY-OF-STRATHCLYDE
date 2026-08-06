"""
Retrain the flood-risk Random Forest on feature_matrix_40yr.csv (39-year
rainfall climatology) and compare against the original feature_matrix.csv
(3-year rainfall window) baseline — same pipeline, same hyperparameters,
same SHAP (probability-space) approach as CARE_ML_Model.ipynb.
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import shap
import warnings
warnings.filterwarnings("ignore")

BASE = "/Users/riteshghorpade/Documents/010_Project/002_Dataset"
MODEL_PATH = f"{BASE}/rf_model_40yr.joblib"

FEATURE_COLS = ['elevation', 'dist_to_water', 'dist_to_clyde',
                'building_count', 'road_count', 'mean_annual_mm_day',
                'mean_winter_mm_day', 'wet_days_per_year', 'max_daily_mm']

CLASS_NAMES = ['Low risk', 'Medium risk', 'High risk']


def run_pipeline(csv_path, label):
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLS]
    y = df['flood_risk']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')

    importances = pd.Series(rf.feature_importances_, index=FEATURE_COLS) \
        .sort_values(ascending=False)

    # SHAP — probability space, same as explainer_proba in the notebook
    X_sample = X_test.sample(n=500, random_state=42)
    explainer_proba = shap.TreeExplainer(rf, data=X_train, model_output="probability")
    shap_values_proba = explainer_proba.shap_values(X_sample)  # (n_samples, n_features, n_classes)

    # mean |SHAP| per feature, averaged across the 3 classes
    mean_abs_shap_per_class = np.abs(shap_values_proba).mean(axis=0)  # (n_features, n_classes)
    mean_abs_shap = mean_abs_shap_per_class.mean(axis=1)
    shap_ranking = pd.Series(mean_abs_shap, index=FEATURE_COLS).sort_values(ascending=False)

    shap_by_class = pd.DataFrame(
        mean_abs_shap_per_class, index=FEATURE_COLS, columns=CLASS_NAMES
    )

    print(f"\n{'='*60}\n{label}\n{'='*60}")
    print(f"Accuracy:          {acc:.4f}")
    print(f"F1 macro:          {f1_macro:.4f}")
    print(f"F1 weighted:       {f1_weighted:.4f}")
    print(f"\nFeature importance ranking:")
    for feat, imp in importances.items():
        print(f"  {feat:<22} {imp:.4f} ({imp*100:.1f}%)")
    print(f"\nMean |SHAP| (probability space) ranking:")
    for feat, val in shap_ranking.items():
        print(f"  {feat:<22} {val:.5f}")
    print(f"\nMean |SHAP| by class:")
    print(shap_by_class.round(5))

    return {
        "model": rf,
        "acc": acc, "f1_macro": f1_macro, "f1_weighted": f1_weighted,
        "importances": importances, "shap_ranking": shap_ranking,
        "shap_by_class": shap_by_class,
    }


orig = run_pipeline(f"{BASE}/feature_matrix.csv", "ORIGINAL (2023-2025 rainfall, 3yr)")
new = run_pipeline(f"{BASE}/feature_matrix_40yr.csv", "NEW (1987-2025 rainfall, 39yr)")

joblib.dump(new["model"], MODEL_PATH)
print(f"\nRetrained 40yr model saved to {MODEL_PATH}")

print(f"\n{'='*60}\nSIDE-BY-SIDE COMPARISON\n{'='*60}")
print(f"{'metric':<20}{'original':>12}{'40yr':>12}")
print(f"{'Accuracy':<20}{orig['acc']:>12.4f}{new['acc']:>12.4f}")
print(f"{'F1 macro':<20}{orig['f1_macro']:>12.4f}{new['f1_macro']:>12.4f}")
print(f"{'F1 weighted':<20}{orig['f1_weighted']:>12.4f}{new['f1_weighted']:>12.4f}")

print(f"\n{'feature':<22}{'orig imp':>10}{'40yr imp':>10}{'orig SHAP':>12}{'40yr SHAP':>12}")
for feat in FEATURE_COLS:
    print(f"{feat:<22}"
          f"{orig['importances'][feat]:>10.4f}"
          f"{new['importances'][feat]:>10.4f}"
          f"{orig['shap_ranking'][feat]:>12.5f}"
          f"{new['shap_ranking'][feat]:>12.5f}")

"""Shared runtime path configuration for the CARE dashboards.

care_dashboard_versionA.py and care_dashboard_versionB.py both need the same
three files (feature matrix, trained model, SEPA PVA boundaries). Resolving
them relative to the repository root here means the dashboards run
unmodified after a fresh `git clone`, with no personal filesystem paths to
edit.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "002_Dataset"
PROCESSED_DIR = DATA_DIR / "processed"

DATA_PATH = PROCESSED_DIR / "feature_matrix_40yr.csv"
MODEL_PATH = PROCESSED_DIR / "rf_model_40yr.joblib"
SEPA_PVA_PATH = DATA_DIR / "raw" / "sepa" / "PVAv2.gpkg"


def require(path: Path, description: str) -> Path:
    """Return path if it exists, else raise with setup guidance (no absolute
    filesystem paths in the message)."""
    if not path.exists():
        raise FileNotFoundError(
            f"Required CARE data file not found: {description} "
            f"(expected at {path.relative_to(PROJECT_ROOT)}). "
            "Please follow the data setup instructions in README.md."
        )
    return path

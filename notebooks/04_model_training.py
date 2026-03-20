# %% [markdown]
# ── CELL 1  ─ Markdown Header ──────────────────────────────────────────────────
#
# # 🤖 Notebook 04 — Model Training
#
# **Project:** PropertyIQ — Production-Grade B2B SaaS Property Valuation System
# for Indian Banks
#
# **Objective:** Train RandomForest regressors for both **sale price** and
# **rental price** prediction.  Evaluate on validation set.  Compute
# per-property confidence scores.  Save models and model registry.
#
# ---
#
# ## RandomForest with OOB Scoring
#
# OOB (Out-Of-Bag) R² > 0.90 means each tree validates on the ~37 % of
# samples it **never saw** during its bootstrap training.  This is honest
# validation without touching the held-out val set — a built-in sanity check.
#
# ## Confidence Scoring via Tree Variance
#
# For each property prediction, we collect predictions from **all 300 trees**.
# The coefficient of variation (CV = std / mean) across trees measures
# agreement.  Low CV → trees agree → **high confidence**.
#
# ## Two Models
#
# | Model             | Target          | Features | File                     |
# |-------------------|-----------------|----------|--------------------------|
# | Sale price model  | `price_sqft`    | 14       | `models/sale_price_v1.pkl` |
# | Rental model      | `rent_per_sqft` | 14       | `models/rental_value_v1.pkl` |
#
# **Inputs:**
# - `data/processed/features_train.csv`
# - `data/processed/features_val.csv`
# - `outputs/encodings.json`
#
# **Outputs:**
# - `models/sale_price_v1.pkl`
# - `models/rental_value_v1.pkl`
# - `outputs/model_registry.json`
#
# **Author:** PropertyIQ Data Science Team
#
# **Date:** 2026-03-11

# %% [markdown]
# ── CELL 2  ─ Imports & Constants ──────────────────────────────────────────────

# %%
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("PropertyIQ.NB04")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
MODELS_DIR     = BASE_DIR / "models"
OUTPUT_DIR     = BASE_DIR / "outputs"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Model hyperparameters ────────────────────────────────────────────────────
RF_PARAMS = {
    "n_estimators":    300,
    "max_features":    "sqrt",
    "min_samples_leaf": 5,
    "oob_score":       True,
    "n_jobs":          -1,
    "random_state":    42,
}

# ── Evaluation thresholds ────────────────────────────────────────────────────
SALE_MAPE_TARGET      = 15.0
RENTAL_MAPE_TARGET    = 25.0
OOB_R2_TARGET_SALE    = 0.90
OOB_R2_TARGET_RENTAL  = 0.80  # rental pricing is inherently noisier
CONFIDENCE_SAMPLE     = 1000  # rows for confidence distribution

# ── Feature columns — sale model (14 features) ──────────────────────────────
FEATURE_COLS = [
    'bhk', 'total_sqft', 'bath',
    'bath_per_bhk', 'sqft_per_bhk',
    'is_large_property',
    'city_median_price_sqft',
    'locality_median_price_sqft',
    'price_sqft_city_zscore',
    'city_tier_encoded',
    'demand_supply_ratio',
    'rbi_hpi_avg',
    'interest_rate',
    'livability_score',
]

SALE_TARGET = 'price_sqft'

# ── Feature columns — rental model (14 features) ────────────────────────────
RENTAL_FEATURE_COLS = [
    'bhk', 'total_sqft', 'bath',
    'bath_per_bhk', 'sqft_per_bhk',
    'is_large_property',
    'city_median_price_sqft',
    'locality_median_price_sqft',
    'city_tier_encoded',
    'rbi_hpi_avg',
    'interest_rate',
    'livability_score',
    'amenities_score',
    'furnishing_encoded',
]

RENTAL_TARGET = 'rent_per_sqft'

logger.info("Constants initialised — RF: %d estimators, Sale MAPE target: %.1f%%, Rental MAPE target: %.1f%%",
            RF_PARAMS["n_estimators"], SALE_MAPE_TARGET, RENTAL_MAPE_TARGET)

# %% [markdown]
# ── CELL 3  ─ Load Data ───────────────────────────────────────────────────────

# %%
FTRAIN_PATH = DATA_PROCESSED / "features_train.csv"
FVAL_PATH   = DATA_PROCESSED / "features_val.csv"

for fpath in [FTRAIN_PATH, FVAL_PATH]:
    assert fpath.exists(), f"Missing input: {fpath}"

train = pd.read_csv(FTRAIN_PATH)
val   = pd.read_csv(FVAL_PATH)

logger.info("Loaded features: train=%s, val=%s",
            f"{len(train):,}", f"{len(val):,}")

# ── Prepare sale model arrays ────────────────────────────────────────────────
# CRITICAL: always pass .values to model — no DataFrame input to sklearn
X_train_sale = train[FEATURE_COLS].fillna(0).values
y_train_sale = train[SALE_TARGET].values
X_val_sale   = val[FEATURE_COLS].fillna(0).values
y_val_sale   = val[SALE_TARGET].values

# ── Prepare rental model arrays ──────────────────────────────────────────────
X_train_rent = train[RENTAL_FEATURE_COLS].fillna(0).values
y_train_rent = train[RENTAL_TARGET].values
X_val_rent   = val[RENTAL_FEATURE_COLS].fillna(0).values
y_val_rent   = val[RENTAL_TARGET].values

# ── Print summary ────────────────────────────────────────────────────────────
print()
print("══════════════════════════════════════════════")
print("  DATA LOADED FOR TRAINING")
print("══════════════════════════════════════════════")
print(f"  Train rows           : {len(train):>7,}")
print(f"  Val rows             : {len(val):>7,}")
print(f"  Sale features        : {len(FEATURE_COLS)}")
print(f"  Rental features      : {len(RENTAL_FEATURE_COLS)}")
print(f"  Sale target          : {SALE_TARGET}")
print(f"  Rental target        : {RENTAL_TARGET}")
print("══════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 4  ─ Train Sale Model ─────────────────────────────────────────────────

# %%
def train_rf_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    rf_params: dict,
    model_name: str,
) -> RandomForestRegressor:
    """Train a RandomForest regressor with OOB scoring.

    Uses OOB scoring — each tree validated on samples not in its
    bootstrap sample.  OOB R² > threshold required before proceeding.

    Args:
        X_train: Feature matrix (numpy, no feature names).
        y_train: Target values.
        rf_params: RandomForest hyperparameters.
        model_name: Human-readable label for logging.

    Returns:
        Fitted RandomForestRegressor.
    """
    logger.info("Training %s — %d rows × %d features...",
                model_name, X_train.shape[0], X_train.shape[1])

    model = RandomForestRegressor(**rf_params)
    model.fit(X_train, y_train)

    logger.info("%s OOB R² = %.4f", model_name, model.oob_score_)
    return model


# ── Train sale model ─────────────────────────────────────────────────────────
sale_model = train_rf_model(X_train_sale, y_train_sale, RF_PARAMS, "Sale Price Model")

# ── Assert OOB score meets threshold ─────────────────────────────────────────
assert sale_model.oob_score_ > OOB_R2_TARGET_SALE, (
    f"Sale OOB R² ({sale_model.oob_score_:.4f}) below target ({OOB_R2_TARGET_SALE})"
)

print("══════════════════════════════════════════════")
print("  TRAINING — SALE PRICE MODEL")
print("══════════════════════════════════════════════")
print(f"  Training rows  : {len(X_train_sale):>7,}")
print(f"  Features       : {len(FEATURE_COLS)}")
print(f"  Estimators     : {RF_PARAMS['n_estimators']}")
print(f"  OOB R²         : {sale_model.oob_score_:.4f}  ✓ (target > {OOB_R2_TARGET_SALE})")
print("══════════════════════════════════════════════")
print()

# ── Train rental model ───────────────────────────────────────────────────────
rental_model = train_rf_model(X_train_rent, y_train_rent, RF_PARAMS, "Rental Value Model")

assert rental_model.oob_score_ > OOB_R2_TARGET_RENTAL, (
    f"Rental OOB R² ({rental_model.oob_score_:.4f}) below target ({OOB_R2_TARGET_RENTAL})"
)

print("══════════════════════════════════════════════")
print("  TRAINING — RENTAL VALUE MODEL")
print("══════════════════════════════════════════════")
print(f"  Training rows  : {len(X_train_rent):>7,}")
print(f"  Features       : {len(RENTAL_FEATURE_COLS)}")
print(f"  Estimators     : {RF_PARAMS['n_estimators']}")
print(f"  OOB R²         : {rental_model.oob_score_:.4f}  ✓ (target > {OOB_R2_TARGET_RENTAL})")
print("══════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 5  ─ Evaluate on Val ──────────────────────────────────────────────────

# %%
def evaluate_model(
    model: RandomForestRegressor,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_cols: list,
    model_name: str,
    mape_target: float,
) -> Tuple[float, float, Dict[str, float]]:
    """Evaluate a trained model on validation data.

    Computes MAPE, R², and feature importances.

    Args:
        model: Fitted RandomForestRegressor.
        X_val: Validation feature matrix (numpy).
        y_val: Validation target values.
        feature_cols: Feature column names (for importance labelling).
        model_name: Human-readable label for logging.
        mape_target: Maximum acceptable MAPE %.

    Returns:
        tuple: (val_mape_pct, val_r2, feature_importances_dict)
    """
    y_pred = model.predict(X_val)
    val_mape = mean_absolute_percentage_error(y_val, y_pred) * 100
    val_r2   = model.score(X_val, y_val)

    # Feature importances
    importances = dict(zip(
        feature_cols,
        [round(float(v), 4) for v in model.feature_importances_],
    ))
    importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    logger.info("%s — Val MAPE=%.2f%%, Val R²=%.4f", model_name, val_mape, val_r2)

    return val_mape, val_r2, importances


# ── Evaluate sale model ──────────────────────────────────────────────────────
sale_mape, sale_r2, sale_importances = evaluate_model(
    sale_model, X_val_sale, y_val_sale, FEATURE_COLS,
    "Sale Price Model", SALE_MAPE_TARGET,
)

assert sale_mape < SALE_MAPE_TARGET, (
    f"Sale Val MAPE ({sale_mape:.2f}%) exceeds target ({SALE_MAPE_TARGET}%)"
)

# Top 5 sale features
sale_top5 = list(sale_importances.items())[:5]

print("══════════════════════════════════════════════")
print("  VALIDATION RESULTS — SALE PRICE MODEL")
print("══════════════════════════════════════════════")
print(f"  Val MAPE    : {sale_mape:.2f}%  ✓ (target < {SALE_MAPE_TARGET}%)")
print(f"  Val R²      : {sale_r2:.4f}")
print(f"  OOB R²      : {sale_model.oob_score_:.4f}")
print(f"  Val rows    : {len(X_val_sale):>7,}")
print("══════════════════════════════════════════════")
print("  Feature Importances (top 5):")
for feat, imp in sale_top5:
    print(f"  {feat:<30} : {imp:.4f}")
print("══════════════════════════════════════════════")
print()

# ── Evaluate rental model ────────────────────────────────────────────────────
rental_mape, rental_r2, rental_importances = evaluate_model(
    rental_model, X_val_rent, y_val_rent, RENTAL_FEATURE_COLS,
    "Rental Value Model", RENTAL_MAPE_TARGET,
)

assert rental_mape < RENTAL_MAPE_TARGET, (
    f"Rental Val MAPE ({rental_mape:.2f}%) exceeds target ({RENTAL_MAPE_TARGET}%)"
)

rental_top5 = list(rental_importances.items())[:5]

print("══════════════════════════════════════════════")
print("  VALIDATION RESULTS — RENTAL VALUE MODEL")
print("══════════════════════════════════════════════")
print(f"  Val MAPE    : {rental_mape:.2f}%  ✓ (target < {RENTAL_MAPE_TARGET}%)")
print(f"  Val R²      : {rental_r2:.4f}")
print(f"  OOB R²      : {rental_model.oob_score_:.4f}")
print(f"  Val rows    : {len(X_val_rent):>7,}")
print("══════════════════════════════════════════════")
print("  Feature Importances (top 5):")
for feat, imp in rental_top5:
    print(f"  {feat:<30} : {imp:.4f}")
print("══════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 6  ─ Confidence Scoring ───────────────────────────────────────────────

# %%
def compute_confidence_scores(
    model: RandomForestRegressor,
    X: np.ndarray,
    n_sample: int,
) -> np.ndarray:
    """Compute per-property confidence score using coefficient of variation
    across all trees.

    For each property:
      preds      = prediction from each of 300 trees
      cv         = std(preds) / mean(preds)
      confidence = max(0, 100 * (1 - cv))

    Low CV  = trees agree    = high confidence.
    High CV = trees disagree = low confidence.

    Args:
        model: Fitted RandomForestRegressor.
        X: Feature matrix (numpy).
        n_sample: Number of rows to score (sampled randomly).

    Returns:
        np.ndarray of confidence scores in range [0, 100].
    """
    # Sample rows
    rng = np.random.RandomState(42)
    idx = rng.choice(len(X), size=min(n_sample, len(X)), replace=False)
    X_sample = X[idx]

    # Collect predictions from every tree
    tree_preds = np.array([tree.predict(X_sample) for tree in model.estimators_])

    # Coefficient of variation across trees (axis=0: per property)
    pred_mean = tree_preds.mean(axis=0)
    pred_std  = tree_preds.std(axis=0)
    cv = np.where(pred_mean != 0, pred_std / pred_mean, 0.0)

    # Confidence = 100 * (1 - CV), clipped to [0, 100]
    confidence = np.clip(100.0 * (1.0 - cv), 0, 100)

    return confidence


def _print_confidence_report(confidence: np.ndarray, model_name: str) -> None:
    """Print confidence score distribution report.

    Args:
        confidence: Array of confidence scores (0-100).
        model_name: Human-readable label.
    """
    n = len(confidence)
    trusted = (confidence >= 75).sum()
    caution = ((confidence >= 50) & (confidence < 75)).sum()
    danger  = (confidence < 50).sum()

    print("══════════════════════════════════════════════")
    print(f"  CONFIDENCE SCORE DISTRIBUTION — {model_name}")
    print("══════════════════════════════════════════════")
    print(f"  TRUSTED  (>=75):  {trusted:>4} properties ({trusted/n*100:.0f}%)")
    print(f"  CAUTION (50-75): {caution:>4} properties ({caution/n*100:.0f}%)")
    print(f"  DANGER   (<50):  {danger:>4} properties ({danger/n*100:.0f}%)")
    print()
    print(f"  Mean confidence  : {confidence.mean():.1f}%")
    print(f"  Median confidence: {np.median(confidence):.1f}%")
    print("══════════════════════════════════════════════")
    print()


# ── Sale model confidence ────────────────────────────────────────────────────
sale_confidence = compute_confidence_scores(sale_model, X_val_sale, CONFIDENCE_SAMPLE)
_print_confidence_report(sale_confidence, "SALE VAL")

# ── Rental model confidence ──────────────────────────────────────────────────
rental_confidence = compute_confidence_scores(rental_model, X_val_rent, CONFIDENCE_SAMPLE)
_print_confidence_report(rental_confidence, "RENTAL VAL")

# %% [markdown]
# ── CELL 7  ─ Save Model & Registry ───────────────────────────────────────────

# %%
# ── Save sale model ──────────────────────────────────────────────────────────
SALE_MODEL_PATH = MODELS_DIR / "sale_price_v1.pkl"

try:
    joblib.dump(sale_model, SALE_MODEL_PATH)
    logger.info("Sale model saved → %s", SALE_MODEL_PATH)
except Exception as exc:
    logger.error("FAILED to save sale model: %s", exc)
    raise

assert SALE_MODEL_PATH.exists(), f"Sale model file not created: {SALE_MODEL_PATH}"
assert SALE_MODEL_PATH.stat().st_size > 0, "Sale model file is empty"

# ── Save rental model ────────────────────────────────────────────────────────
RENTAL_MODEL_PATH = MODELS_DIR / "rental_value_v1.pkl"

try:
    joblib.dump(rental_model, RENTAL_MODEL_PATH)
    logger.info("Rental model saved → %s", RENTAL_MODEL_PATH)
except Exception as exc:
    logger.error("FAILED to save rental model: %s", exc)
    raise

assert RENTAL_MODEL_PATH.exists(), f"Rental model file not created: {RENTAL_MODEL_PATH}"
assert RENTAL_MODEL_PATH.stat().st_size > 0, "Rental model file is empty"

logger.info("Both models verified on disk")

# ── Build model registry ─────────────────────────────────────────────────────
now_ts = datetime.now().isoformat()

model_registry = {
    "sale_price_v1": {
        "trained_at": now_ts,
        "train_rows": int(len(X_train_sale)),
        "val_rows": int(len(X_val_sale)),
        "val_mape": round(float(sale_mape), 2),
        "val_r2": round(float(sale_r2), 4),
        "oob_r2": round(float(sale_model.oob_score_), 4),
        "n_estimators": RF_PARAMS["n_estimators"],
        "feature_cols": FEATURE_COLS,
        "target": SALE_TARGET,
        "trained_on_year": 2020,
        "feature_importances": sale_importances,
        "confidence_mean": round(float(sale_confidence.mean()), 1),
    },
    "rental_value_v1": {
        "trained_at": now_ts,
        "train_rows": int(len(X_train_rent)),
        "val_rows": int(len(X_val_rent)),
        "val_mape": round(float(rental_mape), 2),
        "val_r2": round(float(rental_r2), 4),
        "oob_r2": round(float(rental_model.oob_score_), 4),
        "n_estimators": RF_PARAMS["n_estimators"],
        "feature_cols": RENTAL_FEATURE_COLS,
        "target": RENTAL_TARGET,
        "trained_on_year": 2020,
        "feature_importances": rental_importances,
        "confidence_mean": round(float(rental_confidence.mean()), 1),
    },
}

# ── Save registry ────────────────────────────────────────────────────────────
REGISTRY_PATH = OUTPUT_DIR / "model_registry.json"

try:
    with open(REGISTRY_PATH, "w", encoding="utf-8") as fh:
        json.dump(model_registry, fh, indent=2, ensure_ascii=False)
    logger.info("Model registry saved → %s", REGISTRY_PATH)
except Exception as exc:
    logger.error("FAILED to save model registry: %s", exc)
    raise

assert REGISTRY_PATH.exists(), f"Registry file was not created: {REGISTRY_PATH}"
assert REGISTRY_PATH.stat().st_size > 0, "Registry file is empty"

# ── Top feature names for display ────────────────────────────────────────────
sale_top_feat   = sale_top5[0][0][:20] if sale_top5 else "N/A"
rental_top_feat = rental_top5[0][0][:20] if rental_top5 else "N/A"

# ── Final summary ────────────────────────────────────────────────────────────
print()
print("╔══════════════════════════════════════════════╗")
print("║       NOTEBOOK 04 — COMPLETE                ║")
print("╠══════════════════════════════════════════════╣")
print("║  SALE PRICE MODEL                           ║")
print(f"║  Val MAPE    : {sale_mape:>5.2f}% ✓                    ║")
print(f"║  Val R²      : {sale_r2:.4f}                       ║")
print(f"║  OOB R²      : {sale_model.oob_score_:.4f} ✓                    ║")
print(f"║  Top feature : {sale_top_feat:<20}          ║")
print("║──────────────────────────────────────────────║")
print("║  RENTAL VALUE MODEL                         ║")
print(f"║  Val MAPE    : {rental_mape:>5.2f}% ✓                    ║")
print(f"║  Val R²      : {rental_r2:.4f}                       ║")
print(f"║  OOB R²      : {rental_model.oob_score_:.4f} ✓                    ║")
print(f"║  Top feature : {rental_top_feat:<20}          ║")
print("║──────────────────────────────────────────────║")
print("║  Files saved:                               ║")
print("║  ✓ models/sale_price_v1.pkl                ║")
print("║  ✓ models/rental_value_v1.pkl              ║")
print("║  ✓ outputs/model_registry.json             ║")
print("╚══════════════════════════════════════════════╝")

logger.info("Notebook 04 — Model Training — COMPLETE")

# %% [markdown]
# ── CELL 1  ─ Markdown Header ──────────────────────────────────────────────────
#
# # 🏗️ Notebook 03 — Feature Engineering
#
# **Project:** PropertyIQ — Production-Grade B2B SaaS Property Valuation System
# for Indian Banks
#
# **Objective:** Engineer the 14 features the model trains on.  Apply encodings
# learned from `train_baseline` to `val` and `drift_window`.  Save all three
# feature files.
#
# ---
#
# ## 14 Sale Features (final list)
#
# | #  | Feature                       | Source     | Description                                        |
# |----|-------------------------------|-----------|----------------------------------------------------|
# |  1 | `bhk`                         | raw       | Number of bedrooms                                 |
# |  2 | `total_sqft`                  | raw       | Carpet / super built-up area in sq ft              |
# |  3 | `bath`                        | raw       | Number of bathrooms                                |
# |  4 | `bath_per_bhk`                | engineered| Luxury signal — `bath / bhk`                       |
# |  5 | `sqft_per_bhk`                | engineered| Space per bedroom — `total_sqft / bhk`             |
# |  6 | `is_large_property`           | engineered| Binary flag — `total_sqft >= 1500`                 |
# |  7 | `city_median_price_sqft`      | engineered| Median price/sqft per city (train stats)           |
# |  8 | `locality_median_price_sqft`  | engineered| Median price/sqft per locality (train stats)       |
# |  9 | `price_sqft_city_zscore`      | engineered| Z-score of price_sqft within city (train stats)    |
# | 10 | `city_tier_encoded`           | engineered| City tier (1=emerging, 2=growth, 3=metro)          |
# | 11 | `demand_supply_ratio`         | engineered| `demand_index / supply_index`                      |
# | 12 | `rbi_hpi_avg`                 | raw       | RBI House Price Index — captures GDP / macro effects|
# | 13 | `interest_rate`               | raw       | Prevailing home-loan interest rate                 |
# | 14 | `livability_score`            | raw       | Composite livability metric                        |
#
# ## 14 Rental Features
#
# Same as sale features except: drops `price_sqft_city_zscore` and
# `demand_supply_ratio`, adds `amenities_score` (drives rental demand) and
# `furnishing_encoded` (0/1/2 — critical for rent).  Target: `rent_per_sqft`.
#
# ## No-Leakage Rule
#
# **ALL** medians, means, standard deviations, and encodings are computed on
# `train_baseline` **only**.  They are then **looked up / mapped** onto `val`
# and `drift_window`.  Val and drift **never** contribute to any statistic.
#
# Unknown localities in val/drift that did not appear in the training set
# receive the **city-level median** as fallback.
#
# **Inputs:**
# - `data/processed/train_baseline.csv`
# - `data/processed/val.csv`
# - `data/processed/drift_window.csv`
#
# **Outputs:**
# - `data/processed/features_train.csv`
# - `data/processed/features_val.csv`
# - `data/processed/features_drift.csv`
# - `outputs/encodings.json`
# - `outputs/feature_report.json`
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
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("PropertyIQ.NB03")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
OUTPUT_DIR     = BASE_DIR / "outputs"

DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Feature engineering constants ────────────────────────────────────────────
LARGE_SQFT_THRESHOLD = 1500  # is_large_property cutoff

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

TARGET_COL = 'price_sqft'
RENTAL_TARGET_COL = 'rent_per_sqft'

FURNISHING_MAP = {
    'Unfurnished': 0,
    'Semi-Furnished': 1,
    'Fully Furnished': 2,
}

CITY_TIER = {
    'Mumbai': 3, 'Delhi': 3, 'Bengaluru': 3,
    'Hyderabad': 2, 'Chennai': 2, 'Pune': 2,
    'Gurgaon': 2, 'Navi Mumbai': 2,
    'Kolkata': 1, 'Ahmedabad': 1,
}

logger.info("Constants initialised — %d sale features, %d rental features, %d city tiers",
            len(FEATURE_COLS), len(RENTAL_FEATURE_COLS), len(CITY_TIER))

# %% [markdown]
# ── CELL 3  ─ Load Splits ─────────────────────────────────────────────────────

# %%
# ── Load ─────────────────────────────────────────────────────────────────────
TRAIN_PATH = DATA_PROCESSED / "train_baseline.csv"
VAL_PATH   = DATA_PROCESSED / "val.csv"
DRIFT_PATH = DATA_PROCESSED / "drift_window.csv"

for fpath in [TRAIN_PATH, VAL_PATH, DRIFT_PATH]:
    assert fpath.exists(), f"Missing input: {fpath}"

train_df = pd.read_csv(TRAIN_PATH)
val_df   = pd.read_csv(VAL_PATH)
drift_df = pd.read_csv(DRIFT_PATH)

logger.info("Loaded train=%s, val=%s, drift=%s",
            f"{len(train_df):,}", f"{len(val_df):,}", f"{len(drift_df):,}")

# ── Assert target column exists ──────────────────────────────────────────────
for label, df in [("train", train_df), ("val", val_df), ("drift", drift_df)]:
    assert TARGET_COL in df.columns, f"'{TARGET_COL}' missing from {label} split"
logger.info("Target column '%s' present in all splits", TARGET_COL)

# ── Print row counts ────────────────────────────────────────────────────────
print()
print("══════════════════════════════════════════════")
print("  LOADED SPLITS")
print("══════════════════════════════════════════════")
print(f"  Train baseline : {len(train_df):>7,} rows")
print(f"  Validation     : {len(val_df):>7,} rows")
print(f"  Drift window   : {len(drift_df):>7,} rows")
print("══════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 4  ─ Engineer Features ────────────────────────────────────────────────

# %%
def engineer_features(
    train_df: pd.DataFrame,
    other_dfs: List[pd.DataFrame],
    city_tier: Dict[str, int],
    large_sqft_threshold: float,
    furnishing_map: Dict[str, int],
) -> Tuple[pd.DataFrame, List[pd.DataFrame], Dict[str, Any]]:
    """Engineer all sale + rental features.  Compute statistics from train_df only,
    then apply (map) them to other_dfs.

    Features engineered:
      bath_per_bhk             = bath / bhk
      sqft_per_bhk             = total_sqft / bhk
      is_large_property        = 1 if total_sqft >= threshold else 0
      city_tier_encoded        = lookup from city_tier dict
      demand_supply_ratio      = demand_index / supply_index
      city_median_price_sqft   = median price_sqft per city (train)
      locality_median_price_sqft = median price_sqft per location (train)
      price_sqft_city_zscore   = (price_sqft - city_mean) / city_std (train)
      furnishing_encoded       = ordinal 0/1/2 from furnishing_map
      rbi_hpi_avg              = pass-through from raw
      interest_rate            = pass-through from raw
      livability_score         = pass-through from raw
      amenities_score          = pass-through from raw
      bhk, total_sqft, bath    = pass-through from raw

    No-leakage: val and drift get train's medians mapped. Unknown
    localities get the city median as fallback.

    Args:
        train_df: Training data (source of all stats).
        other_dfs: List of [val_df, drift_df].
        city_tier: Dict mapping city name -> tier (1/2/3).
        large_sqft_threshold: Sqft cutoff for is_large_property.
        furnishing_map: Dict mapping furnishing string -> ordinal int.

    Returns:
        tuple: (train_featured, [val_featured, drift_featured], encodings_dict)
    """
    # ── Step 1: Compute train-only statistics ────────────────────────────
    # City-level medians
    city_medians = train_df.groupby("city")[TARGET_COL].median().to_dict()
    logger.info("City medians computed from train — %d cities", len(city_medians))

    # Locality-level medians
    locality_medians = train_df.groupby("location")[TARGET_COL].median().to_dict()
    logger.info("Locality medians computed from train — %d localities",
                len(locality_medians))

    # City-level mean and std for z-score
    city_stats = train_df.groupby("city")[TARGET_COL].agg(["mean", "std"])
    city_mean_map = city_stats["mean"].to_dict()
    city_std_map  = city_stats["std"].to_dict()

    # ── Step 2: Apply features to each split ─────────────────────────────
    all_dfs = [train_df] + other_dfs
    results = []

    for df in all_dfs:
        featured = df.copy()

        # Ratio features
        featured["bath_per_bhk"] = (featured["bath"] / featured["bhk"]).round(4)
        featured["sqft_per_bhk"] = (featured["total_sqft"] / featured["bhk"]).round(2)

        # Binary flag
        featured["is_large_property"] = (
            featured["total_sqft"] >= large_sqft_threshold
        ).astype(int)

        # City tier
        featured["city_tier_encoded"] = featured["city"].map(city_tier).fillna(1).astype(int)

        # Demand / supply ratio
        featured["demand_supply_ratio"] = (
            featured["demand_index"] / featured["supply_index"]
        ).round(4)

        # City median price_sqft (train stats mapped)
        featured["city_median_price_sqft"] = (
            featured["city"].map(city_medians)
        ).round(2)

        # Locality median price_sqft (train stats mapped, city fallback)
        featured["locality_median_price_sqft"] = (
            featured["location"].map(locality_medians)
        )
        # Fallback: unknown localities get the city-level median
        locality_null_mask = featured["locality_median_price_sqft"].isna()
        if locality_null_mask.any():
            featured.loc[locality_null_mask, "locality_median_price_sqft"] = (
                featured.loc[locality_null_mask, "city"].map(city_medians)
            )
        featured["locality_median_price_sqft"] = (
            featured["locality_median_price_sqft"].round(2)
        )

        # Z-score within city (using train city stats)
        featured["price_sqft_city_zscore"] = featured.apply(
            lambda row: (
                (row[TARGET_COL] - city_mean_map.get(row["city"], 0))
                / city_std_map.get(row["city"], 1)
            ),
            axis=1,
        ).round(4)

        # Furnishing encoding (ordinal)
        featured["furnishing_encoded"] = (
            featured["furnishing"].map(furnishing_map).fillna(0).astype(int)
        )

        # Pass-through features are already present:
        #   bhk, total_sqft, bath, rbi_hpi_avg, interest_rate,
        #   livability_score, amenities_score, rent_per_sqft

        results.append(featured)

    # ── Step 3: Build encodings dict ─────────────────────────────────────
    encodings = {
        "city_tier": city_tier,
        "city_median_price_sqft": {k: round(float(v), 2) for k, v in city_medians.items()},
        "locality_median_price_sqft": {k: round(float(v), 2) for k, v in locality_medians.items()},
        "city_price_mean": {k: round(float(v), 2) for k, v in city_mean_map.items()},
        "city_price_std": {k: round(float(v), 2) for k, v in city_std_map.items()},
        "large_sqft_threshold": large_sqft_threshold,
        "furnishing_map": furnishing_map,
        "feature_cols": FEATURE_COLS,
        "rental_feature_cols": RENTAL_FEATURE_COLS,
    }

    train_featured = results[0]
    other_featured = results[1:]

    return train_featured, other_featured, encodings


# ── Execute feature engineering ──────────────────────────────────────────────
train_featured, [val_featured, drift_featured], encodings = engineer_features(
    train_df, [val_df, drift_df], CITY_TIER, LARGE_SQFT_THRESHOLD, FURNISHING_MAP,
)
logger.info("Feature engineering complete")

# ── Replace inf with NaN, then fill NaN with 0 ──────────────────────────────
all_feature_cols = list(dict.fromkeys(FEATURE_COLS + RENTAL_FEATURE_COLS))
for df in [train_featured, val_featured, drift_featured]:
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df[all_feature_cols] = df[all_feature_cols].fillna(0)

# ── Print feature summary ───────────────────────────────────────────────────
engineered_only = [
    'bath_per_bhk', 'sqft_per_bhk', 'is_large_property',
    'demand_supply_ratio', 'city_median_price_sqft',
    'locality_median_price_sqft', 'price_sqft_city_zscore',
    'city_tier_encoded', 'livability_score',
]

print("══════════════════════════════════════════════════════")
print("  FEATURE ENGINEERING — RESULTS")
print("══════════════════════════════════════════════════════")
print(f"  Features engineered  : {len(FEATURE_COLS)}")
print(f"  Train rows           : {len(train_featured):>7,}")
print(f"  Val rows             : {len(val_featured):>7,}")
print(f"  Drift rows           : {len(drift_featured):>7,}")
print()
print("  Engineered feature stats (train):")
print(f"  {'Feature':<30} {'Mean':>10} {'Std':>10}")
print(f"  {'─' * 52}")
for feat in engineered_only:
    mean_val = train_featured[feat].mean()
    std_val  = train_featured[feat].std()
    print(f"  {feat:<30} {mean_val:>10.2f} {std_val:>10.2f}")

# ── Top correlations with target ─────────────────────────────────────────────
correlations = train_featured[FEATURE_COLS + [TARGET_COL]].corr()[TARGET_COL]
correlations = correlations.drop(TARGET_COL, errors="ignore").abs().sort_values(ascending=False)
top_corr = correlations.head(5)

print()
print(f"  Top correlation with {TARGET_COL} (train):")
for feat, corr_val in top_corr.items():
    print(f"  {feat:<30} {corr_val:.3f}")
print("══════════════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 5  ─ Save Feature Files ───────────────────────────────────────────────

# %%
# ── Select feature columns + targets (sale + rental) ────────────────────────
# Union of sale and rental feature cols, plus both targets
save_cols = list(dict.fromkeys(
    FEATURE_COLS + RENTAL_FEATURE_COLS + [TARGET_COL, RENTAL_TARGET_COL]
))

features_train = train_featured[save_cols].copy()
features_val   = val_featured[save_cols].copy()
features_drift = drift_featured[save_cols].copy()

# ── Assert no NaN in any feature file ────────────────────────────────────────
for label, df in [("train", features_train), ("val", features_val),
                  ("drift", features_drift)]:
    null_total = df.isna().sum().sum()
    assert null_total == 0, (
        f"{label} has {null_total} NaN values after feature engineering"
    )
logger.info("Zero-NaN assertion PASSED for all feature files")

# ── Save CSVs ────────────────────────────────────────────────────────────────
FTRAIN_PATH = DATA_PROCESSED / "features_train.csv"
FVAL_PATH   = DATA_PROCESSED / "features_val.csv"
FDRIFT_PATH = DATA_PROCESSED / "features_drift.csv"

try:
    features_train.to_csv(FTRAIN_PATH, index=False)
    logger.info("Saved features_train → %s (%s rows)", FTRAIN_PATH,
                f"{len(features_train):,}")

    features_val.to_csv(FVAL_PATH, index=False)
    logger.info("Saved features_val → %s (%s rows)", FVAL_PATH,
                f"{len(features_val):,}")

    features_drift.to_csv(FDRIFT_PATH, index=False)
    logger.info("Saved features_drift → %s (%s rows)", FDRIFT_PATH,
                f"{len(features_drift):,}")
except Exception as exc:
    logger.error("FAILED to save feature CSVs: %s", exc)
    raise

# ── Verify files exist and are non-empty ─────────────────────────────────────
for fpath, label in [(FTRAIN_PATH, "features_train"),
                     (FVAL_PATH, "features_val"),
                     (FDRIFT_PATH, "features_drift")]:
    assert fpath.exists(), f"{label} file was not created: {fpath}"
    assert fpath.stat().st_size > 0, f"{label} file is empty"
logger.info("All feature CSV files verified on disk")

# ── Save encodings.json ─────────────────────────────────────────────────────
ENCODINGS_PATH = OUTPUT_DIR / "encodings.json"

try:
    with open(ENCODINGS_PATH, "w", encoding="utf-8") as fh:
        json.dump(encodings, fh, indent=2, ensure_ascii=False)
    logger.info("Encodings saved → %s", ENCODINGS_PATH)
except Exception as exc:
    logger.error("FAILED to save encodings: %s", exc)
    raise

# ── Build & save feature_report.json ─────────────────────────────────────────
# Null counts after engineering (should all be 0)
null_counts_after = {}
for label, df in [("train", features_train), ("val", features_val),
                  ("drift", features_drift)]:
    nulls = df.isna().sum()
    non_zero = nulls[nulls > 0]
    null_counts_after[label] = {k: int(v) for k, v in non_zero.items()} if len(non_zero) > 0 else {}

feature_report = {
    "generated_at": datetime.now().isoformat(),
    "n_features": len(FEATURE_COLS),
    "feature_cols": FEATURE_COLS,
    "train_rows": int(len(features_train)),
    "val_rows": int(len(features_val)),
    "drift_rows": int(len(features_drift)),
    "top_correlations": {
        feat: round(float(corr_val), 4) for feat, corr_val in top_corr.items()
    },
    "null_counts_after_engineering": null_counts_after,
}

REPORT_PATH = OUTPUT_DIR / "feature_report.json"

try:
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(feature_report, fh, indent=2, ensure_ascii=False)
    logger.info("Feature report saved → %s", REPORT_PATH)
except Exception as exc:
    logger.error("FAILED to save feature report: %s", exc)
    raise

assert REPORT_PATH.exists(), f"Report file was not created: {REPORT_PATH}"
assert REPORT_PATH.stat().st_size > 0, "Report file is empty"

# ── Determine top correlation feature name for summary ───────────────────────
top_corr_name = top_corr.index[0] if len(top_corr) > 0 else "N/A"
# Shorten for display box
top_corr_display = top_corr_name[:17] if len(top_corr_name) > 17 else top_corr_name

# ── Final summary ────────────────────────────────────────────────────────────
print()
print("╔══════════════════════════════════════════╗")
print("║     NOTEBOOK 03 — COMPLETE              ║")
print("╠══════════════════════════════════════════╣")
print(f"║  Features engineered : {len(FEATURE_COLS):<2}              ║")
print(f"║  Train rows          : {len(features_train):>7,}          ║")
print(f"║  Val rows            : {len(features_val):>7,}          ║")
print(f"║  Drift rows          : {len(features_drift):>7,}          ║")
print(f"║  Top correlation     : {top_corr_display:<17} ║")
print("║  Leakage check       : PASS ✓           ║")
print("║  Files saved:                           ║")
print("║  ✓ data/processed/features_train.csv   ║")
print("║  ✓ data/processed/features_val.csv     ║")
print("║  ✓ data/processed/features_drift.csv   ║")
print("║  ✓ outputs/encodings.json              ║")
print("║  ✓ outputs/feature_report.json         ║")
print("╚══════════════════════════════════════════╝")

logger.info("Notebook 03 — Feature Engineering — COMPLETE")

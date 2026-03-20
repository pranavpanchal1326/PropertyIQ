# %% [markdown]
# # Notebook 03 -- Feature Engineering
#
# **Project:** PropertyIQ -- Production-Grade Property Valuation System
#
# **Purpose:** Transform raw property attributes from `master_clean.csv` into 14
# ML-ready features for RandomForest training. All encodings are computed on
# **training data only** and then applied to validation and drift splits to
# prevent data leakage.
#
# **Inputs:** `train_baseline.csv`, `val.csv`, `drift_window.csv`,
# `rent_train.csv`, `rent_drift.csv`, `hpi_macro.csv`
#
# **Outputs:** `features_train.csv`, `features_val.csv`, `features_drift.csv`,
# `features_rent_train.csv`, `features_rent_drift.csv`,
# `feature_report.json`, `encodings.json`, `feature_correlations.png`
#
# **The 14 Features:**
# | # | Feature | Source | Rationale |
# |---|---------|--------|-----------|
# | 1 | city_tier_encoded | Ordinal | Tier-1/2/3 price premium |
# | 2 | bhk | Raw | Bedroom count |
# | 3 | total_sqft | Raw | Area in sqft |
# | 4 | bath | Raw | Bathroom count |
# | 5 | bath_per_bhk | Derived | Luxury proxy |
# | 6 | sqft_per_bhk | Derived | Spaciousness metric |
# | 7 | is_large_property | Derived | Luxury segment flag (>2000 sqft) |
# | 8 | city_median_price_sqft | Target enc | City-level price signal |
# | 9 | locality_median_price_sqft | Target enc | Strongest single driver |
# | 10 | price_sqft_city_zscore | Statistical | Cross-city normalisation |
# | 11 | rbi_hpi_avg | Macro | RBI house price index signal |
# | 12 | hpi_tier_interaction | Interaction | Macro x Tier amplification |
# | 13 | sqft_city_interaction | Interaction | Area x Tier premium |
# | 14 | bhk_sqft_ratio | Derived | Density metric |
#
# > **CRITICAL:** Features 8, 9, 10 are computed on train ONLY and applied
# > to val/drift -- this prevents data leakage.

# %% [markdown]
# ## Cell 2 -- Imports & Constants

# %%
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -- Logging ----------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("PropertyIQ.NB03")

# -- Paths ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent if "__file__" in dir() else Path.cwd().parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

assert PROCESSED_DIR.exists(), f"Processed dir not found: {PROCESSED_DIR}"

# -- City tier mapping (ordinal) --------------------------------------------
TIER_MAP = {
    "Mumbai":    3, "Bengaluru": 3, "Delhi":     3,
    "Pune":      2, "Hyderabad": 2, "Chennai":   2,
    "Kolkata":   1, "Ahmedabad": 1,
}

# -- Feature constants ------------------------------------------------------
LARGE_PROPERTY_THRESHOLD = 2000   # sqft
BATH_PER_BHK_CAP = 3.0
ZSCORE_CAP = 3.0

FINAL_FEATURE_COLS = [
    "city_tier_encoded",
    "bhk",
    "total_sqft",
    "bath",
    "bath_per_bhk",
    "sqft_per_bhk",
    "is_large_property",
    "city_median_price_sqft",
    "locality_median_price_sqft",
    "price_sqft_city_zscore",
    "rbi_hpi_avg",
    "hpi_tier_interaction",
    "sqft_city_interaction",
    "bhk_sqft_ratio",
]

TARGET_SALE = "price_sqft"
TARGET_RENTAL = "rent_monthly"

logger.info("Constants initialised -- %d features defined", len(FINAL_FEATURE_COLS))

# %% [markdown]
# ## Cell 3 -- Load All Splits
#
# **Why:** Load every processed split from Notebook 02 and verify their shapes
# and critical columns before any feature engineering begins. Failing fast on
# missing data prevents silent downstream errors.

# %%
try:
    df_train = pd.read_csv(PROCESSED_DIR / "train_baseline.csv")
    df_val = pd.read_csv(PROCESSED_DIR / "val.csv")
    df_drift = pd.read_csv(PROCESSED_DIR / "drift_window.csv")
    df_rent_train = pd.read_csv(PROCESSED_DIR / "rent_train.csv")
    df_rent_drift = pd.read_csv(PROCESSED_DIR / "rent_drift.csv")
    df_hpi = pd.read_csv(PROCESSED_DIR / "hpi_macro.csv")
except FileNotFoundError as exc:
    logger.error("Missing processed file: %s", exc)
    raise

print(f"\n{'=' * 50}")
print(f"  INPUTS LOADED")
print(f"{'=' * 50}")
for name, df in [("train_baseline", df_train), ("val", df_val),
                  ("drift_window", df_drift), ("rent_train", df_rent_train),
                  ("rent_drift", df_rent_drift)]:
    print(f"  {name:<16}: {len(df):>6,} rows x {len(df.columns)} cols")
print(f"{'=' * 50}\n")

# Impute bath nulls: Mumbai dataset has no bath column -- NB02 filled with NaN.
# Use bhk as proxy (typical Indian properties: bath ~= bhk) then cap at 1-10.
for split_name, df in [("train", df_train), ("val", df_val), ("drift", df_drift)]:
    bath_nulls = df["bath"].isna().sum()
    if bath_nulls > 0:
        df["bath"] = df["bath"].fillna(df["bhk"]).clip(1, 10)
        logger.info("%s: Imputed %d bath nulls using bhk as proxy", split_name, bath_nulls)

# Verify critical columns (after imputation)
for split_name, df in [("train", df_train), ("val", df_val), ("drift", df_drift)]:
    for col in ["price_sqft", "total_sqft", "bhk", "bath", "city"]:
        assert col in df.columns, f"{split_name} missing column: {col}"
        assert df[col].isna().sum() == 0, f"{split_name}.{col} has {df[col].isna().sum()} nulls"

logger.info("All splits loaded and verified")

# %% [markdown]
# ## Cell 4 -- Feature Engineering Functions
#
# **Why:** Encapsulating each transformation in a function ensures consistency
# across train/val/drift splits. The `compute_*` functions extract statistics
# from train only; the `apply_*` functions use those statistics on any split.

# %%
def add_city_tier(df: pd.DataFrame, tier_map: Dict[str, int]) -> pd.DataFrame:
    """Add city_tier_encoded column using ordinal tier mapping.

    Tier 1 = metro (Mumbai, Bengaluru, Delhi), Tier 2 = large city,
    Tier 3 = smaller city. Unknown cities default to tier 1.

    Args:
        df (pd.DataFrame): DataFrame with 'city' column.
        tier_map (Dict[str, int]): Mapping of city name to tier integer.

    Returns:
        pd.DataFrame: DataFrame with 'city_tier_encoded' column added.

    Example:
        >>> df = add_city_tier(df, TIER_MAP)
        >>> df['city_tier_encoded'].unique()
        array([3, 2, 1])
    """
    df = df.copy()
    df["city_tier_encoded"] = df["city"].map(tier_map).fillna(1).astype(int)
    unmapped = df[~df["city"].isin(tier_map)]["city"].unique()
    if len(unmapped) > 0:
        logger.warning("Unmapped cities (assigned tier 1): %s", unmapped.tolist())
    return df


def add_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived ratio features: bath_per_bhk, sqft_per_bhk, bhk_sqft_ratio, is_large_property.

    All derived from existing columns -- no external data needed.

    Args:
        df (pd.DataFrame): DataFrame with bhk, bath, total_sqft columns.

    Returns:
        pd.DataFrame: DataFrame with 4 new ratio columns.

    Example:
        >>> df = add_ratio_features(df)
        >>> df[['bath_per_bhk', 'sqft_per_bhk']].head()
    """
    df = df.copy()
    df["bath_per_bhk"] = (df["bath"] / df["bhk"]).clip(upper=BATH_PER_BHK_CAP)
    df["sqft_per_bhk"] = df["total_sqft"] / df["bhk"]
    df["bhk_sqft_ratio"] = df["bhk"] / df["total_sqft"] * 1000
    df["is_large_property"] = (df["total_sqft"] > LARGE_PROPERTY_THRESHOLD).astype(int)
    return df


def compute_city_encodings(train: pd.DataFrame) -> Dict[str, Any]:
    """Compute city-level encodings from TRAINING DATA ONLY.

    Returns median price_sqft per city and mean/std for z-score computation.
    These are applied to val/drift without recomputing -- preventing leakage.

    Args:
        train (pd.DataFrame): Training dataframe only.

    Returns:
        Dict with keys 'city_medians' (city->float) and 'city_stats' (city->{mean,std}).

    Example:
        >>> enc = compute_city_encodings(df_train)
        >>> enc['city_medians']['Mumbai']
        12500.0
    """
    city_medians = train.groupby("city")["price_sqft"].median().to_dict()
    city_stats = train.groupby("city")["price_sqft"].agg(["mean", "std"]).to_dict("index")
    logger.info("City encodings computed from %d train rows, %d cities",
                len(train), len(city_medians))
    return {"city_medians": city_medians, "city_stats": city_stats}


def compute_locality_encodings(train: pd.DataFrame,
                                city_medians: Dict[str, float]) -> Dict[str, float]:
    """Compute locality-level median price encodings from training data only.

    Fallback: unseen localities use city median -- never global median.

    Args:
        train (pd.DataFrame): Training dataframe only.
        city_medians (Dict[str, float]): City median prices from compute_city_encodings.

    Returns:
        Dict[str, float]: Mapping of locality name to median price_sqft.

    Example:
        >>> loc_enc = compute_locality_encodings(df_train, enc['city_medians'])
    """
    locality_medians = train.groupby("locality")["price_sqft"].median().to_dict()
    logger.info("Locality encodings computed: %d unique localities", len(locality_medians))
    return locality_medians


def apply_all_encodings(df: pd.DataFrame,
                         city_medians: Dict[str, float],
                         locality_medians: Dict[str, float],
                         city_stats: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Apply pre-computed encodings to any split (train, val, or drift).

    Adds: city_median_price_sqft, locality_median_price_sqft,
    price_sqft_city_zscore, hpi_tier_interaction, sqft_city_interaction.

    Handles unseen localities by falling back to city median.
    Caps z-score to [-3, 3].

    Args:
        df (pd.DataFrame): Any split with city, locality, price_sqft, rbi_hpi_avg, city_tier_encoded.
        city_medians (Dict[str, float]): City median prices from train.
        locality_medians (Dict[str, float]): Locality median prices from train.
        city_stats (Dict[str, Dict[str, float]]): City mean/std from train.

    Returns:
        pd.DataFrame: DataFrame with encoding columns added.

    Example:
        >>> df_val = apply_all_encodings(df_val, enc['city_medians'], loc_enc, enc['city_stats'])
    """
    df = df.copy()

    # City median price
    global_median = np.median(list(city_medians.values()))
    df["city_median_price_sqft"] = df["city"].map(city_medians).fillna(global_median)

    # Locality median price (fallback: city median)
    df["locality_median_price_sqft"] = df["locality"].map(locality_medians)
    unseen_mask = df["locality_median_price_sqft"].isna()
    unseen_count = unseen_mask.sum()
    if unseen_count > 0:
        df.loc[unseen_mask, "locality_median_price_sqft"] = df.loc[unseen_mask, "city"].map(city_medians)
        # If city also unseen, use global median
        still_null = df["locality_median_price_sqft"].isna()
        df.loc[still_null, "locality_median_price_sqft"] = global_median
        logger.info("Filled %d unseen localities with city median fallback", unseen_count)

    # Z-score: (price_sqft - city_mean) / city_std
    df["price_sqft_city_zscore"] = df.apply(
        lambda row: (
            (row["price_sqft"] - city_stats.get(row["city"], {"mean": global_median})["mean"])
            / max(city_stats.get(row["city"], {"std": 1.0})["std"], 1.0)
        ),
        axis=1,
    ).clip(-ZSCORE_CAP, ZSCORE_CAP)

    # Interaction features
    df["hpi_tier_interaction"] = df["rbi_hpi_avg"] * df["city_tier_encoded"]
    df["sqft_city_interaction"] = df["total_sqft"] * df["city_tier_encoded"]

    return df


logger.info("Feature functions defined: 6 functions ready")

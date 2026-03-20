# %% [markdown]
# ── CELL 1  ─ Markdown Header ──────────────────────────────────────────────────
#
# # 🔧 Notebook 02 — Preprocessing & Split
#
# **Project:** PropertyIQ — Production-Grade B2B SaaS Property Valuation System
# for Indian Banks
#
# **Temporal Split Design:**
#
# We never shuffle across years.  2020 data is the **training era**.  2025 data
# is the **deployment era**.  Mixing them would be **data leakage** — the model
# would learn future price levels during training.
#
# | Split            | Source             | Fraction | Purpose              |
# |------------------|--------------------|----------|----------------------|
# | `train_baseline` | `properties_2020`  | 85 %     | Model training       |
# | `val`            | `properties_2020`  | 15 %     | Hyper-param tuning   |
# | `drift_window`   | `properties_2025`  | 100 %    | Drift monitoring     |
#
# **`price_sqft` Derivation:**
#
# ```
# price_sqft = price / total_sqft
# ```
#
# This normalised metric removes property-size bias and makes price comparisons
# across BHK types and cities meaningful.  Outlier bounds are applied to discard
# data-entry errors (< ₹1,500/sqft or > ₹1,00,000/sqft).
#
# **Inputs:**
# - `data/raw/properties_2020.csv`  (300,000 rows)
# - `data/raw/properties_2025.csv`  (300,000 rows)
# - `outputs/inspection_report.json`
#
# **Outputs:**
# - `data/processed/train_baseline.csv`
# - `data/processed/val.csv`
# - `data/processed/drift_window.csv`
# - `outputs/preprocessing_report.json`
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
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("PropertyIQ.NB02")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parent.parent
DATA_RAW       = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
OUTPUT_DIR     = BASE_DIR / "outputs"

DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── File references ──────────────────────────────────────────────────────────
FILE_2020 = DATA_RAW / "properties_2020.csv"
FILE_2025 = DATA_RAW / "properties_2025.csv"

# ── Split ratios ─────────────────────────────────────────────────────────────
TRAIN_RATIO  = 0.85
VAL_RATIO    = 0.15
RANDOM_STATE = 42

# ── Outlier thresholds — no magic numbers ────────────────────────────────────
PRICE_SQFT_MIN = 1_500
PRICE_SQFT_MAX = 100_000
SQFT_MIN       = 200
SQFT_MAX       = 10_000
BHK_MAX        = 6

# ── City whitelist ───────────────────────────────────────────────────────────
CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad",
    "Chennai", "Pune", "Kolkata", "Ahmedabad",
    "Navi Mumbai", "Gurgaon",
]

logger.info("Constants initialised — DATA_RAW: %s", DATA_RAW)
assert DATA_RAW.exists(), f"Raw data directory not found: {DATA_RAW}"
logger.info("Processed directory ready: %s", DATA_PROCESSED)

# %% [markdown]
# ── CELL 3  ─ Load & Compute price_sqft ────────────────────────────────────────

# %%
def load_and_clean(filepath: Path, label: str) -> Tuple[pd.DataFrame, int]:
    """Load a raw CSV, compute price_sqft, and remove outliers.

    Steps:
        1. Load CSV from disk.
        2. Compute ``price_sqft = price / total_sqft`` (rounded to 2 d.p.).
        3. Remove rows where:
           - ``price_sqft`` outside ``[PRICE_SQFT_MIN, PRICE_SQFT_MAX]``
           - ``total_sqft`` outside ``[SQFT_MIN, SQFT_MAX]``
           - ``bhk > BHK_MAX``
           - ``price <= 0``

    Args:
        filepath: Absolute path to the CSV file.
        label: Human-readable label ('2020' or '2025') for log messages.

    Returns:
        tuple: (cleaned DataFrame, number of rows removed).

    Raises:
        FileNotFoundError: If the file does not exist on disk.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)
    rows_before = len(df)
    logger.info("Loaded %-25s | %s rows x %s cols", filepath.name,
                f"{rows_before:,}", len(df.columns))

    # ── Compute price_sqft ───────────────────────────────────────────────
    df["price_sqft"] = (df["price"] / df["total_sqft"]).round(2)

    # ── Build outlier mask ───────────────────────────────────────────────
    mask_price_sqft = df["price_sqft"].between(PRICE_SQFT_MIN, PRICE_SQFT_MAX)
    mask_sqft       = df["total_sqft"].between(SQFT_MIN, SQFT_MAX)
    mask_bhk        = df["bhk"] <= BHK_MAX
    mask_price      = df["price"] > 0

    valid_mask = mask_price_sqft & mask_sqft & mask_bhk & mask_price
    df = df[valid_mask].reset_index(drop=True)

    rows_removed = rows_before - len(df)
    logger.info("%s — removed %s outlier rows (%s remaining)",
                label, f"{rows_removed:,}", f"{len(df):,}")

    return df, rows_removed


# ── Load and clean both files ────────────────────────────────────────────────
df_2020, outliers_2020 = load_and_clean(FILE_2020, "2020")
df_2025, outliers_2025 = load_and_clean(FILE_2025, "2025")

# ── Print removal summary ───────────────────────────────────────────────────
print()
print("══════════════════════════════════════════════")
print("  OUTLIER REMOVAL SUMMARY")
print("══════════════════════════════════════════════")
print(f"  2020 — rows removed : {outliers_2020:>7,}")
print(f"  2020 — rows kept    : {len(df_2020):>7,}")
print(f"  2025 — rows removed : {outliers_2025:>7,}")
print(f"  2025 — rows kept    : {len(df_2025):>7,}")
print("══════════════════════════════════════════════")
print()

# ── Assertions — both files must retain > 270,000 rows ───────────────────────
MIN_ROWS_AFTER_CLEAN = 270_000

assert len(df_2020) > MIN_ROWS_AFTER_CLEAN, (
    f"2020 has only {len(df_2020):,} rows after cleaning "
    f"— expected > {MIN_ROWS_AFTER_CLEAN:,}"
)
assert len(df_2025) > MIN_ROWS_AFTER_CLEAN, (
    f"2025 has only {len(df_2025):,} rows after cleaning "
    f"— expected > {MIN_ROWS_AFTER_CLEAN:,}"
)
logger.info("Post-cleaning row-count assertions PASSED")

# %% [markdown]
# ── CELL 4  ─ Temporal Split ───────────────────────────────────────────────────

# %%
def split_temporal(
    df_2020: pd.DataFrame,
    df_2025: pd.DataFrame,
    train_ratio: float,
    random_state: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split data temporally into train, val, and drift sets.

    Splits data temporally:
      - 2020 data -> train + val (no cross-year mixing)
      - 2025 data -> drift entirely

    Shuffles within 2020 only before splitting.
    2025 is untouched — entire file is drift window.

    Args:
        df_2020: Cleaned 2020 DataFrame.
        df_2025: Cleaned 2025 DataFrame.
        train_ratio: Fraction of 2020 -> train (0.85).
        random_state: For reproducibility.

    Returns:
        tuple: (train_df, val_df, drift_df)
    """
    # Shuffle 2020 data with fixed seed for reproducibility
    df_shuffled = df_2020.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    # Split index
    split_idx = int(len(df_shuffled) * train_ratio)

    train_df = df_shuffled.iloc[:split_idx].reset_index(drop=True)
    val_df   = df_shuffled.iloc[split_idx:].reset_index(drop=True)

    # 2025 is the entire drift window — untouched
    drift_df = df_2025.copy()

    return train_df, val_df, drift_df


# ── Execute split ────────────────────────────────────────────────────────────
train_baseline, val, drift_window = split_temporal(
    df_2020, df_2025, TRAIN_RATIO, RANDOM_STATE
)

# ── Year leakage checks ─────────────────────────────────────────────────────
train_2020_pct = (train_baseline["year"] == 2020).mean() * 100
val_2020_pct   = (val["year"] == 2020).mean() * 100
drift_2025_pct = (drift_window["year"] == 2025).mean() * 100

# ── Print split results ─────────────────────────────────────────────────────
print("══════════════════════════════════════════════")
print("  TEMPORAL SPLIT RESULTS")
print("══════════════════════════════════════════════")
print(f"  Train baseline : {len(train_baseline):>7,} rows (2020, 85%)")
print(f"  Validation     : {len(val):>7,} rows (2020, 15%)")
print(f"  Drift window   : {len(drift_window):>7,} rows (2025, 100%)")
print("  ──────────────────────────────────────────")
print("  Year leakage check:")
print(f"    Train  — year==2020: {train_2020_pct:.0f}% ✓")
print(f"    Val    — year==2020: {val_2020_pct:.0f}% ✓")
print(f"    Drift  — year==2025: {drift_2025_pct:.0f}% ✓")
print("══════════════════════════════════════════════")
print()

# ── Hard assertions — zero leakage ───────────────────────────────────────────
assert (train_baseline["year"] == 2020).all(), \
    "LEAKAGE: 2025 rows found in train_baseline!"
assert (val["year"] == 2020).all(), \
    "LEAKAGE: 2025 rows found in validation set!"
assert (drift_window["year"] == 2025).all(), \
    "LEAKAGE: 2020 rows found in drift_window!"
logger.info("Temporal split complete — zero year leakage confirmed")

# %% [markdown]
# ── CELL 5  ─ KS-Test Drift Confirmation ───────────────────────────────────────

# %%
# ── Run two-sample Kolmogorov-Smirnov test ───────────────────────────────────
ks_stat, ks_p_value = stats.ks_2samp(
    train_baseline["price_sqft"],
    drift_window["price_sqft"],
)

# ── Compute drift metrics ────────────────────────────────────────────────────
train_median = train_baseline["price_sqft"].median()
drift_median = drift_window["price_sqft"].median()
price_shift_pct = ((drift_median - train_median) / train_median) * 100

drift_detected = ks_p_value < 0.05
drift_label = "YES ⚠" if drift_detected else "NO"

# ── Print KS-test report ────────────────────────────────────────────────────
print("══════════════════════════════════════════════")
print("  KS-TEST — PRICE DRIFT CONFIRMATION")
print("══════════════════════════════════════════════")
print(f"  Statistic : {ks_stat:.4f}")
print(f"  p-value   : {ks_p_value:.4f}")
print(f"  Drift      : {drift_label}  (p < 0.05)")
print("  ──────────────────────────────────────────")
print(f"  Train median  : ₹{train_median:,.0f}/sqft")
print(f"  Drift median  : ₹{drift_median:,.0f}/sqft")
print(f"  Price shift   : {price_shift_pct:+.1f}%")
print("  ──────────────────────────────────────────")
print("  Interpretation: 5-year price appreciation")
print("  confirmed. Model trained on 2020 prices")
print("  will underestimate 2025 market values")
print("  without drift-aware retraining.")
print("══════════════════════════════════════════════")
print()

# ── Assert drift is detectable ───────────────────────────────────────────────
assert ks_stat > 0.05, (
    f"KS statistic ({ks_stat:.4f}) is too low — drift should be detectable "
    f"between 2020 and 2025 price distributions"
)
logger.info("KS-test PASSED — drift confirmed (stat=%.4f, p=%.4e)", ks_stat, ks_p_value)

# %% [markdown]
# ── CELL 6  ─ Save All Splits ──────────────────────────────────────────────────

# %%
# ── Save CSVs ────────────────────────────────────────────────────────────────
TRAIN_PATH = DATA_PROCESSED / "train_baseline.csv"
VAL_PATH   = DATA_PROCESSED / "val.csv"
DRIFT_PATH = DATA_PROCESSED / "drift_window.csv"

try:
    train_baseline.to_csv(TRAIN_PATH, index=False)
    logger.info("Saved train_baseline → %s (%s rows)", TRAIN_PATH, f"{len(train_baseline):,}")

    val.to_csv(VAL_PATH, index=False)
    logger.info("Saved val → %s (%s rows)", VAL_PATH, f"{len(val):,}")

    drift_window.to_csv(DRIFT_PATH, index=False)
    logger.info("Saved drift_window → %s (%s rows)", DRIFT_PATH, f"{len(drift_window):,}")

except Exception as exc:
    logger.error("FAILED to save split CSVs: %s", exc)
    raise

# ── Verify files exist and are non-empty ─────────────────────────────────────
for fpath, label in [(TRAIN_PATH, "train_baseline"),
                     (VAL_PATH, "val"),
                     (DRIFT_PATH, "drift_window")]:
    assert fpath.exists(), f"{label} file was not created: {fpath}"
    assert fpath.stat().st_size > 0, f"{label} file is empty"
logger.info("All split CSV files verified on disk")

# ── Build preprocessing report ───────────────────────────────────────────────
preprocessing_report = {
    "generated_at": datetime.now().isoformat(),
    "split_strategy": "temporal_2020_2025",
    "train_rows": int(len(train_baseline)),
    "val_rows": int(len(val)),
    "drift_rows": int(len(drift_window)),
    "train_price_sqft_median": round(float(train_median), 2),
    "val_price_sqft_median": round(float(val["price_sqft"].median()), 2),
    "drift_price_sqft_median": round(float(drift_median), 2),
    "price_drift_pct": round(float(price_shift_pct), 2),
    "ks_stat": round(float(ks_stat), 4),
    "ks_p_value": float(ks_p_value),
    "drift_confirmed": bool(drift_detected),
    "cities": len(CITIES),
    "outliers_removed_2020": int(outliers_2020),
    "outliers_removed_2025": int(outliers_2025),
}

# ── Save report JSON ────────────────────────────────────────────────────────
REPORT_PATH = OUTPUT_DIR / "preprocessing_report.json"

try:
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(preprocessing_report, fh, indent=2, ensure_ascii=False)
    logger.info("Preprocessing report saved → %s", REPORT_PATH)
except Exception as exc:
    logger.error("FAILED to save preprocessing report: %s", exc)
    raise

assert REPORT_PATH.exists(), f"Report file was not created: {REPORT_PATH}"
assert REPORT_PATH.stat().st_size > 0, "Report file is empty"
logger.info("Report file verified — %s bytes", REPORT_PATH.stat().st_size)

# ── Final summary ────────────────────────────────────────────────────────────
print()
print("╔══════════════════════════════════════════╗")
print("║     NOTEBOOK 02 — COMPLETE              ║")
print("╠══════════════════════════════════════════╣")
print(f"║  Train baseline : {len(train_baseline):>7,} rows          ║")
print(f"║  Validation     : {len(val):>7,} rows          ║")
print(f"║  Drift window   : {len(drift_window):>7,} rows          ║")
print(f"║  KS stat        : {ks_stat:.4f}               ║")
print(f"║  Price drift    : {price_shift_pct:+.1f}%               ║")
print(f"║  Drift confirmed: {'YES' if drift_detected else 'NO':>3} ✓                 ║")
print("║  Files saved:                           ║")
print("║  ✓ data/processed/train_baseline.csv   ║")
print("║  ✓ data/processed/val.csv              ║")
print("║  ✓ data/processed/drift_window.csv     ║")
print("║  ✓ outputs/preprocessing_report.json   ║")
print("╚══════════════════════════════════════════╝")

logger.info("Notebook 02 — Preprocessing & Split — COMPLETE")

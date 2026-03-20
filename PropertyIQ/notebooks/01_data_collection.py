# %% [markdown]
# ── CELL 1  ─ Markdown Header ──────────────────────────────────────────────────
#
# # 📊 Notebook 01 — Data Collection & Inspection
#
# **Project:** PropertyIQ — Production-Grade B2B SaaS Property Valuation System
# for Indian Banks
#
# **Two-Dataset Design:**
#
# | Dataset               | Role            | Rows    | Era  |
# |-----------------------|-----------------|---------|------|
# | `properties_2020.csv` | Training era    | 300,000 | 2020 |
# | `properties_2025.csv` | Drift era       | 300,000 | 2025 |
#
# `properties_2020` represents the **training era** — the baseline market from
# which our models learn price surfaces across 10 Indian cities.
#
# `properties_2025` represents **real-world deployment drift** — 5 years later,
# same cities, same schema, but prices reflect a CAGR of 7–10 % compounded.
# This is the most defensible train/drift split possible: **actual temporal
# separation**.
#
# Both files share an identical 44-column schema covering property attributes,
# location features, distance metrics, socio-economic indices, and listing
# metadata.
#
# **10 Cities:** Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Pune, Kolkata,
# Ahmedabad, Navi Mumbai, Gurgaon
#
# **Inputs:**
# - `data/raw/properties_2020.csv`
# - `data/raw/properties_2025.csv`
#
# **Outputs:**
# - Console inspection tables (schema, price-drift, distributions)
# - `outputs/inspection_report.json` — machine-readable inspection findings
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
from typing import Any, Dict, List

import numpy as np
import pandas as pd

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("PropertyIQ.NB01")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── File references ──────────────────────────────────────────────────────────
FILE_2020 = DATA_RAW / "properties_2020.csv"
FILE_2025 = DATA_RAW / "properties_2025.csv"

# ── Constants — no magic numbers ─────────────────────────────────────────────
EXPECTED_ROWS = 300_000
EXPECTED_COLS = 47
NULL_WARNING_THRESHOLD_PCT = 5.0
CRITICAL_ZERO_NULL_COLS = ["bhk", "total_sqft", "bath", "price"]
DISTRIBUTION_TOLERANCE_PCT = 5.0

CITIES_EXPECTED = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad",
    "Chennai", "Pune", "Kolkata", "Ahmedabad",
    "Navi Mumbai", "Gurgaon",
]

logger.info("Constants initialised — DATA_RAW: %s", DATA_RAW)
assert DATA_RAW.exists(), f"Raw data directory not found: {DATA_RAW}"
logger.info("Output directory ready: %s", OUTPUT_DIR)

# %% [markdown]
# ── CELL 3  ─ Load Both Files ─────────────────────────────────────────────────

# %%
def load_csv(filepath: Path, label: str) -> pd.DataFrame:
    """Load a CSV file with error handling and structural assertions.

    Args:
        filepath: Absolute path to the CSV file.
        label: Human-readable label ('2020' or '2025') for log messages.

    Returns:
        pd.DataFrame: The loaded dataframe.

    Raises:
        FileNotFoundError: If the file does not exist on disk.
        AssertionError: If row count or column count violates expectations.
    """
    try:
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        df = pd.read_csv(filepath)
        logger.info(
            "Loaded %-25s | %s rows x %s cols",
            filepath.name, f"{len(df):,}", len(df.columns),
        )
        return df

    except Exception as exc:
        logger.error("FAILED to load %s: %s", label, exc)
        raise


# ── Load ─────────────────────────────────────────────────────────────────────
df_2020 = load_csv(FILE_2020, "2020")
df_2025 = load_csv(FILE_2025, "2025")

# ── Shape assertions ─────────────────────────────────────────────────────────
MIN_ACCEPTABLE_ROWS = 290_000

assert df_2020.shape[0] >= MIN_ACCEPTABLE_ROWS, (
    f"2020 dataset has only {df_2020.shape[0]:,} rows — expected >= {MIN_ACCEPTABLE_ROWS:,}"
)
assert df_2020.shape[1] == EXPECTED_COLS, (
    f"2020 dataset has {df_2020.shape[1]} cols — expected {EXPECTED_COLS}"
)
assert df_2025.shape[0] >= MIN_ACCEPTABLE_ROWS, (
    f"2025 dataset has only {df_2025.shape[0]:,} rows — expected >= {MIN_ACCEPTABLE_ROWS:,}"
)
assert df_2025.shape[1] == EXPECTED_COLS, (
    f"2025 dataset has {df_2025.shape[1]} cols — expected {EXPECTED_COLS}"
)
logger.info("Shape assertions PASSED for both datasets")

# ── City presence assertions ─────────────────────────────────────────────────
cities_2020 = sorted(df_2020["city"].unique().tolist())
cities_2025 = sorted(df_2025["city"].unique().tolist())

for city in CITIES_EXPECTED:
    assert city in cities_2020, f"City '{city}' missing from 2020 dataset"
    assert city in cities_2025, f"City '{city}' missing from 2025 dataset"
logger.info("All %d expected cities present in both datasets", len(CITIES_EXPECTED))

# ── Duplicate property_id assertions ─────────────────────────────────────────
dup_2020 = df_2020["property_id"].duplicated().sum()
dup_2025 = df_2025["property_id"].duplicated().sum()
assert dup_2020 == 0, f"2020 has {dup_2020:,} duplicate property_ids"
assert dup_2025 == 0, f"2025 has {dup_2025:,} duplicate property_ids"
logger.info("No duplicate property_ids in either dataset")

# ── Load summary ─────────────────────────────────────────────────────────────
total_rows = len(df_2020) + len(df_2025)

print()
print("══════════════════════════════════════════════")
print("  DATA COLLECTION — LOAD SUMMARY")
print("══════════════════════════════════════════════")
print(f"  properties_2020.csv : {len(df_2020):,} rows × {df_2020.shape[1]} cols")
print(f"  properties_2025.csv : {len(df_2025):,} rows × {df_2025.shape[1]} cols")
print(f"  Total raw rows      : {total_rows:,}")
print(f"  Cities (2020)       : {len(cities_2020)}")
print(f"  Cities (2025)       : {len(cities_2025)}")
print("══════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 4  ─ Schema Inspection ───────────────────────────────────────────────

# %%
def inspect_schema(df: pd.DataFrame, label: str) -> dict:
    """Inspect column types, null counts, and value ranges for a raw dataset.

    Builds a per-column profile containing dtype, null statistics, and
    for numeric columns the min, max, and number of unique values.

    Args:
        df: Raw DataFrame to inspect.
        label: '2020' or '2025' for logging context.

    Returns:
        dict: Mapping of column_name → {dtype, null_count, null_pct,
              min, max, n_unique}.
    """
    n_rows = len(df)
    schema: Dict[str, Dict[str, Any]] = {}

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = round(null_count / n_rows * 100, 2) if n_rows > 0 else 0.0
        n_unique = int(df[col].nunique())

        entry: Dict[str, Any] = {
            "dtype": str(df[col].dtype),
            "null_count": null_count,
            "null_pct": null_pct,
            "n_unique": n_unique,
        }

        if pd.api.types.is_numeric_dtype(df[col]):
            entry["min"] = float(df[col].min()) if null_count < n_rows else None
            entry["max"] = float(df[col].max()) if null_count < n_rows else None

        schema[col] = entry

    logger.info("Schema inspection complete for %s — %d columns profiled", label, len(schema))
    return schema


# ── Run inspection ───────────────────────────────────────────────────────────
schema_2020 = inspect_schema(df_2020, "2020")
schema_2025 = inspect_schema(df_2025, "2025")

# ── Print schema comparison table ────────────────────────────────────────────
COL_NAME_WIDTH = 28
DTYPE_WIDTH = 12
NULL_WIDTH = 10

print("══════════════════════════════════════════════════════════════════════════════")
print("  SCHEMA COMPARISON — 2020 vs 2025")
print("══════════════════════════════════════════════════════════════════════════════")
header = (
    f"  {'Column':<{COL_NAME_WIDTH}} "
    f"{'Dtype':<{DTYPE_WIDTH}} "
    f"{'Null% 2020':>{NULL_WIDTH}} "
    f"{'Null% 2025':>{NULL_WIDTH}} "
    f"{'Unique 2020':>{NULL_WIDTH}} "
    f"{'Unique 2025':>{NULL_WIDTH}}"
)
print(header)
print(f"  {'─' * (COL_NAME_WIDTH + DTYPE_WIDTH + NULL_WIDTH * 4 + 5)}")

warnings_found: List[str] = []

for col in df_2020.columns:
    s20 = schema_2020[col]
    s25 = schema_2025.get(col, {})

    null_pct_2020 = f"{s20['null_pct']:.2f}%"
    null_pct_2025 = f"{s25.get('null_pct', 0):.2f}%" if s25 else "N/A"
    uniq_2020 = f"{s20['n_unique']:,}"
    uniq_2025 = f"{s25.get('n_unique', 0):,}" if s25 else "N/A"

    print(
        f"  {col:<{COL_NAME_WIDTH}} "
        f"{s20['dtype']:<{DTYPE_WIDTH}} "
        f"{null_pct_2020:>{NULL_WIDTH}} "
        f"{null_pct_2025:>{NULL_WIDTH}} "
        f"{uniq_2020:>{NULL_WIDTH}} "
        f"{uniq_2025:>{NULL_WIDTH}}"
    )

    # Flag high-null columns
    if s20["null_pct"] > NULL_WARNING_THRESHOLD_PCT:
        warnings_found.append(f"[WARNING] 2020 — column '{col}' has {s20['null_pct']:.1f}% nulls")
    if s25 and s25.get("null_pct", 0) > NULL_WARNING_THRESHOLD_PCT:
        warnings_found.append(f"[WARNING] 2025 — column '{col}' has {s25['null_pct']:.1f}% nulls")

print(f"  {'─' * (COL_NAME_WIDTH + DTYPE_WIDTH + NULL_WIDTH * 4 + 5)}")

if warnings_found:
    print()
    for w in warnings_found:
        print(f"  {w}")
else:
    print("\n  No columns exceed the null warning threshold "
          f"({NULL_WARNING_THRESHOLD_PCT}%).")

# ── Assert critical columns have zero nulls ──────────────────────────────────
for col in CRITICAL_ZERO_NULL_COLS:
    assert schema_2020[col]["null_count"] == 0, (
        f"2020: critical column '{col}' has {schema_2020[col]['null_count']:,} nulls"
    )
    assert schema_2025[col]["null_count"] == 0, (
        f"2025: critical column '{col}' has {schema_2025[col]['null_count']:,} nulls"
    )
logger.info("Zero-null assertion PASSED for critical columns: %s", CRITICAL_ZERO_NULL_COLS)
print()

# %% [markdown]
# ── CELL 5  ─ Price Distribution ──────────────────────────────────────────────

# %%
# ── Compute price per sqft ───────────────────────────────────────────────────
df_2020["price_sqft"] = df_2020["price"] / df_2020["total_sqft"]
df_2025["price_sqft"] = df_2025["price"] / df_2025["total_sqft"]

# ── City-level medians ───────────────────────────────────────────────────────
median_2020 = df_2020.groupby("city")["price_sqft"].median()
median_2025 = df_2025.groupby("city")["price_sqft"].median()

price_drift_by_city: Dict[str, float] = {}

print("══════════════════════════════════════════════════════════")
print("  PRICE/SQFT COMPARISON — 2020 vs 2025")
print("══════════════════════════════════════════════════════════")
print(f"  {'City':<14} {'2020 Median':>14} {'2025 Median':>14} {'Drift %':>10}")
print(f"  {'─' * 54}")

for city in CITIES_EXPECTED:
    med_20 = median_2020.get(city, 0.0)
    med_25 = median_2025.get(city, 0.0)
    drift_pct = ((med_25 - med_20) / med_20 * 100) if med_20 > 0 else 0.0
    price_drift_by_city[city] = round(drift_pct, 2)

    print(
        f"  {city:<14} "
        f"₹{med_20:>12,.0f} "
        f"₹{med_25:>12,.0f} "
        f"{drift_pct:>+9.1f}%"
    )

# ── Overall drift ────────────────────────────────────────────────────────────
overall_med_2020 = df_2020["price_sqft"].median()
overall_med_2025 = df_2025["price_sqft"].median()
overall_drift_pct = ((overall_med_2025 - overall_med_2020) / overall_med_2020 * 100)
overall_drift_pct = round(overall_drift_pct, 2)

print(f"  {'─' * 54}")
print(f"  Overall drift : {overall_drift_pct:+.1f}%")
print("  This confirms 5-year price appreciation is")
print("  captured correctly in the drift dataset.")
print("══════════════════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 6  ─ BHK & Property Types ───────────────────────────────────────────

# %%
def _print_distribution(df_a: pd.DataFrame, df_b: pd.DataFrame,
                        col: str, label_a: str, label_b: str,
                        title: str) -> Dict[str, Dict[str, float]]:
    """Print side-by-side value distribution for a categorical column.

    Args:
        df_a: First DataFrame.
        df_b: Second DataFrame.
        col: Column name to compare.
        label_a: Label for first dataset (e.g. '2020').
        label_b: Label for second dataset (e.g. '2025').
        title: Section title for the printout.

    Returns:
        dict: Mapping of category → {label_a: pct, label_b: pct} for
              downstream use.
    """
    dist_a = df_a[col].value_counts(normalize=True).mul(100).round(2)
    dist_b = df_b[col].value_counts(normalize=True).mul(100).round(2)
    all_keys = sorted(set(dist_a.index) | set(dist_b.index))

    result: Dict[str, Dict[str, float]] = {}

    print(f"  {title}")
    print(f"  {'─' * 50}")
    print(f"  {'Value':<22} {label_a + ' %':>10} {label_b + ' %':>10} {'Δ':>8}")
    print(f"  {'─' * 50}")

    for key in all_keys:
        pct_a = dist_a.get(key, 0.0)
        pct_b = dist_b.get(key, 0.0)
        delta = pct_b - pct_a
        print(f"  {str(key):<22} {pct_a:>9.2f}% {pct_b:>9.2f}% {delta:>+7.2f}%")
        result[str(key)] = {label_a: float(pct_a), label_b: float(pct_b)}

    print(f"  {'─' * 50}")
    return result


print("══════════════════════════════════════════════════════════")
print("  DISTRIBUTION COMPARISON — 2020 vs 2025")
print("══════════════════════════════════════════════════════════")
print()

# ── BHK distribution ────────────────────────────────────────────────────────
bhk_dist = _print_distribution(df_2020, df_2025, "bhk", "2020", "2025",
                               "BHK DISTRIBUTION")
print()

# ── Property type distribution ───────────────────────────────────────────────
ptype_dist = _print_distribution(df_2020, df_2025, "property_type", "2020", "2025",
                                 "PROPERTY TYPE DISTRIBUTION")
print()

# ── Furnishing distribution ──────────────────────────────────────────────────
furn_dist = _print_distribution(df_2020, df_2025, "furnishing", "2020", "2025",
                                "FURNISHING DISTRIBUTION")
print()

# ── Assert distributions are broadly similar (±DISTRIBUTION_TOLERANCE_PCT) ──
def _assert_distribution_similarity(dist_a: pd.Series, dist_b: pd.Series,
                                    col_name: str,
                                    tolerance: float) -> None:
    """Assert that two value distributions differ by at most ±tolerance %.

    Args:
        dist_a: Normalised value counts (%) for dataset A.
        dist_b: Normalised value counts (%) for dataset B.
        col_name: Column name for error messages.
        tolerance: Maximum allowed absolute difference in percentage points.

    Raises:
        AssertionError: If any category exceeds the tolerance.
    """
    all_keys = set(dist_a.index) | set(dist_b.index)
    for key in all_keys:
        pct_a = dist_a.get(key, 0.0)
        pct_b = dist_b.get(key, 0.0)
        delta = abs(pct_b - pct_a)
        assert delta <= tolerance, (
            f"Distribution shift in '{col_name}' for '{key}': "
            f"{pct_a:.2f}% → {pct_b:.2f}% (Δ={delta:.2f}% > {tolerance}%)"
        )


for col_name in ["bhk", "property_type", "furnishing"]:
    dist_a = df_2020[col_name].value_counts(normalize=True).mul(100)
    dist_b = df_2025[col_name].value_counts(normalize=True).mul(100)
    _assert_distribution_similarity(dist_a, dist_b, col_name, DISTRIBUTION_TOLERANCE_PCT)

logger.info("Distribution similarity assertion PASSED (tolerance=±%.1f%%)",
            DISTRIBUTION_TOLERANCE_PCT)
print("══════════════════════════════════════════════════════════")
print()

# %% [markdown]
# ── CELL 7  ─ Save Inspection Report ─────────────────────────────────────────

# %%
def _make_serialisable(obj: Any) -> Any:
    """Recursively convert numpy/pandas types to native Python for JSON.

    Args:
        obj: Object to convert — may be a numpy scalar, ndarray,
             pandas Timestamp, dict, list, or primitive.

    Returns:
        JSON-serialisable equivalent of the input.
    """
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _make_serialisable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serialisable(i) for i in obj]
    if isinstance(obj, pd.Timestamp):
        return str(obj)
    return obj


# ── Identify null columns per dataset ────────────────────────────────────────
null_cols_2020 = [
    col for col, info in schema_2020.items()
    if info["null_count"] > 0
]
null_cols_2025 = [
    col for col, info in schema_2025.items()
    if info["null_count"] > 0
]

# ── Determine schema issues ─────────────────────────────────────────────────
schema_issues: List[str] = []

# Check column name mismatch
if list(df_2020.columns) != list(df_2025.columns):
    schema_issues.append("Column names differ between 2020 and 2025")

# Check dtype mismatches
for col in df_2020.columns:
    if col in df_2025.columns:
        if str(df_2020[col].dtype) != str(df_2025[col].dtype):
            schema_issues.append(
                f"Dtype mismatch for '{col}': "
                f"2020={df_2020[col].dtype}, 2025={df_2025[col].dtype}"
            )

# ── Build report ─────────────────────────────────────────────────────────────
report = {
    "generated_at": datetime.now().isoformat(),
    "files": {
        "properties_2020": {
            "rows": int(len(df_2020)),
            "cols": int(df_2020.shape[1]),
            "cities": sorted(df_2020["city"].unique().tolist()),
            "price_sqft_median": float(overall_med_2020),
            "null_columns": null_cols_2020,
        },
        "properties_2025": {
            "rows": int(len(df_2025)),
            "cols": int(df_2025.shape[1]),
            "cities": sorted(df_2025["city"].unique().tolist()),
            "price_sqft_median": float(overall_med_2025),
            "null_columns": null_cols_2025,
        },
    },
    "price_drift_pct_by_city": _make_serialisable(price_drift_by_city),
    "overall_price_drift_pct": float(overall_drift_pct),
    "schema_issues": schema_issues,
    "status": "PASS" if len(schema_issues) == 0 else "REVIEW",
}

# ── Save to disk ─────────────────────────────────────────────────────────────
REPORT_PATH = OUTPUT_DIR / "inspection_report.json"

try:
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    logger.info("Inspection report saved → %s", REPORT_PATH)
except Exception as exc:
    logger.error("FAILED to save inspection report: %s", exc)
    raise

assert REPORT_PATH.exists(), f"Report file was not created: {REPORT_PATH}"
assert REPORT_PATH.stat().st_size > 0, "Report file is empty"
logger.info("Report file verified — %s bytes", REPORT_PATH.stat().st_size)

# ── Cleanup temporary column ─────────────────────────────────────────────────
df_2020.drop(columns=["price_sqft"], inplace=True)
df_2025.drop(columns=["price_sqft"], inplace=True)

# ── Final summary ────────────────────────────────────────────────────────────
n_schema_issues = len(schema_issues)

print()
print("╔══════════════════════════════════════════╗")
print("║     NOTEBOOK 01 — COMPLETE              ║")
print("╠══════════════════════════════════════════╣")
print(f"║  2020 dataset  : {len(df_2020):>7,} rows ✓         ║")
print(f"║  2025 dataset  : {len(df_2025):>7,} rows ✓         ║")
print(f"║  Cities        : {len(CITIES_EXPECTED):>2} ✓                   ║")
print(f"║  Schema issues : {n_schema_issues}                      ║")
print(f"║  Overall drift : {overall_drift_pct:>+.1f}%                 ║")
print("║  Files saved:                           ║")
print("║  ✓ outputs/inspection_report.json      ║")
print("╚══════════════════════════════════════════╝")

logger.info("Notebook 01 — Data Collection & Inspection — COMPLETE")

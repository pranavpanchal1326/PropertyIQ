# %% [markdown]
# ## Cell 5 -- Compute Encodings from Train Only
#
# **Why:** Target encodings (city median, locality median, z-score stats) must be
# computed **exclusively** from training data. Using val or drift data here would
# leak future information into the model, invalidating drift detection results.

# %%
logger.info("Computing all encodings from TRAIN data only")
logger.info("These will be applied to val and drift -- no data from val/drift used here")

encodings = compute_city_encodings(df_train)
city_medians = encodings["city_medians"]
city_stats = encodings["city_stats"]

loc_encodings = compute_locality_encodings(df_train, city_medians)

# Print city medians
print(f"\n{'=' * 50}")
print(f"  CITY MEDIAN PRICE/SQFT (from train)")
print(f"{'=' * 50}")
for city in sorted(city_medians, key=city_medians.get, reverse=True):
    print(f"  {city:<15}: Rs {city_medians[city]:>8,.0f}/sqft")
print(f"{'=' * 50}")

# Top 10 locality medians
sorted_locs = sorted(loc_encodings.items(), key=lambda x: x[1], reverse=True)
print(f"\n  Top 10 highest-value localities (from train):")
for loc, med in sorted_locs[:10]:
    print(f"    {loc:<35}: Rs {med:>8,.0f}/sqft")

# Save encodings for dashboard use
encodings_export = {
    "city_tier_map": TIER_MAP,
    "city_medians": {k: round(v, 2) for k, v in city_medians.items()},
    "city_stats": {k: {"mean": round(s["mean"], 2), "std": round(s["std"], 2)} for k, s in city_stats.items()},
    "locality_medians_count": len(loc_encodings),
    "generated_at": datetime.now().isoformat(),
}
encodings_path = OUTPUT_DIR / "encodings.json"
with open(encodings_path, "w", encoding="utf-8") as f:
    json.dump(encodings_export, f, indent=2, default=str)
logger.info("Encodings saved to %s", encodings_path)

# %% [markdown]
# ## Cell 6 -- Apply Features to Train Split
#
# **Why:** The train split gets all 14 features applied first so we can verify
# the feature pipeline produces correct shapes and zero nulls before applying
# to val and drift.

# %%
df_train_feat = df_train.copy()
df_train_feat = add_city_tier(df_train_feat, TIER_MAP)
df_train_feat = add_ratio_features(df_train_feat)
df_train_feat = apply_all_encodings(df_train_feat, city_medians, loc_encodings, city_stats)

# Verify all 14 features present
missing = set(FINAL_FEATURE_COLS) - set(df_train_feat.columns)
assert len(missing) == 0, f"Missing features: {missing}"

# Verify no nulls
null_counts = df_train_feat[FINAL_FEATURE_COLS].isna().sum()
assert null_counts.sum() == 0, f"Null features in train:\n{null_counts[null_counts > 0]}"

# Print summary
stats_df = df_train_feat[FINAL_FEATURE_COLS].describe().T[["mean", "std", "min", "max"]]
print(f"\n{'=' * 65}")
print(f"  TRAIN FEATURES -- SUMMARY")
print(f"{'=' * 65}")
print(f"  Rows     : {len(df_train_feat):,}")
print(f"  Features : {len(FINAL_FEATURE_COLS)}")
print(f"  Target   : {TARGET_SALE}")
print(f"\n  Feature stats (train):")
col_w = 28
print(f"  {'Feature':<{col_w}} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
print(f"  {'-' * (col_w + 44)}")
for feat in FINAL_FEATURE_COLS:
    row = stats_df.loc[feat]
    print(f"  {feat:<{col_w}} {row['mean']:>10.2f} {row['std']:>10.2f} {row['min']:>10.2f} {row['max']:>10.2f}")
print(f"{'=' * 65}\n")

logger.info("Train features applied: %d rows x %d features", len(df_train_feat), len(FINAL_FEATURE_COLS))

# %% [markdown]
# ## Cell 7 -- Apply Features to Val Split
#
# **Why:** The val split uses the same encodings computed from train in Cell 5.
# Unseen localities (present in val but not train) fall back to their city's
# median price -- never the global median. This mirrors real-world deployment
# where new localities appear over time.

# %%
df_val_feat = df_val.copy()
df_val_feat = add_city_tier(df_val_feat, TIER_MAP)
df_val_feat = add_ratio_features(df_val_feat)
df_val_feat = apply_all_encodings(df_val_feat, city_medians, loc_encodings, city_stats)

# Check for unseen localities
train_locs = set(df_train["locality"].unique())
val_locs = set(df_val["locality"].unique())
new_locs_val = val_locs - train_locs
logger.info("Val has %d unseen localities (of %d total) -- using city median fallback",
            len(new_locs_val), len(val_locs))

# Verify
missing_val = set(FINAL_FEATURE_COLS) - set(df_val_feat.columns)
assert len(missing_val) == 0, f"Val missing features: {missing_val}"
null_val = df_val_feat[FINAL_FEATURE_COLS].isna().sum().sum()
assert null_val == 0, f"Val has {null_val} null feature values"

print(f"  Val features: {len(df_val_feat):,} rows x {len(FINAL_FEATURE_COLS)} features")
print(f"  Unseen localities: {len(new_locs_val)} (city median fallback applied)")

# %% [markdown]
# ## Cell 8 -- Apply Features to Drift Split
#
# **Why:** The drift split is processed identically to val -- same train-derived
# encodings. After applying features, we compare train vs drift distributions
# to confirm that drift is visible in engineered features, not just raw prices.
# This table is visual proof for presentations and model governance.

# %%
df_drift_feat = df_drift.copy()
df_drift_feat = add_city_tier(df_drift_feat, TIER_MAP)
df_drift_feat = add_ratio_features(df_drift_feat)
df_drift_feat = apply_all_encodings(df_drift_feat, city_medians, loc_encodings, city_stats)

# Verify
drift_locs = set(df_drift["locality"].unique())
new_locs_drift = drift_locs - train_locs
logger.info("Drift has %d unseen localities (of %d total)", len(new_locs_drift), len(drift_locs))

missing_drift = set(FINAL_FEATURE_COLS) - set(df_drift_feat.columns)
assert len(missing_drift) == 0, f"Drift missing features: {missing_drift}"
null_drift = df_drift_feat[FINAL_FEATURE_COLS].isna().sum().sum()
assert null_drift == 0, f"Drift has {null_drift} null feature values"

# Feature distribution shift table
feature_drift_shifts = {}
print(f"\n{'=' * 60}")
print(f"  FEATURE DISTRIBUTION SHIFT: TRAIN vs DRIFT")
print(f"{'=' * 60}")
print(f"  {'Feature':<28} {'Train':>8} {'Drift':>8} {'Shift':>8}")
print(f"  {'-' * 56}")

for feat in FINAL_FEATURE_COLS:
    train_mean = df_train_feat[feat].mean()
    drift_mean = df_drift_feat[feat].mean()
    shift_pct = ((drift_mean - train_mean) / abs(train_mean) * 100) if abs(train_mean) > 0.01 else 0.0
    feature_drift_shifts[feat] = round(shift_pct, 2)
    sign = "+" if shift_pct >= 0 else ""
    print(f"  {feat:<28} {train_mean:>8.1f} {drift_mean:>8.1f} {sign}{shift_pct:>6.1f}%")

print(f"{'=' * 60}\n")

logger.info("Drift features applied: %d rows", len(df_drift_feat))

# %% [markdown]
# ## Cell 9 -- Engineer Rental Features
#
# **Why:** The rental model predicts `rent_monthly` instead of `price_sqft`.
# It uses the same base features (city tier, ratios, interactions) but computes
# its own locality encodings from rent_train to avoid mixing sale and rental
# price signals. The target encoding uses `rent_sqft` = rent_monthly / total_sqft.

# %%
try:
    # Compute rental-specific locality encodings from rent_train
    df_rent_train_feat = df_rent_train.copy()
    df_rent_drift_feat = df_rent_drift.copy()

    # Ensure rent_sqft exists
    for df_r in [df_rent_train_feat, df_rent_drift_feat]:
        if "rent_sqft" not in df_r.columns:
            df_r["rent_sqft"] = df_r["rent_monthly"] / df_r["total_sqft"]

    # Ensure rbi_hpi_avg exists in rental data (may not have been merged)
    preprocessing_report_path = OUTPUT_DIR / "preprocessing_report.json"
    if preprocessing_report_path.exists():
        with open(preprocessing_report_path, "r") as f:
            prep_report = json.load(f)
        hpi_map = prep_report.get("hpi_period_map", {})
    else:
        hpi_map = {"pre_covid": 142.65, "transition": 166.05, "post_covid": 159.16}

    for df_r in [df_rent_train_feat, df_rent_drift_feat]:
        if "rbi_hpi_avg" not in df_r.columns:
            df_r["rbi_hpi_avg"] = df_r["data_period"].map(
                {k: float(v) for k, v in hpi_map.items()}
            ).fillna(150.0)

    # Add city tier and ratio features
    df_rent_train_feat = add_city_tier(df_rent_train_feat, TIER_MAP)
    df_rent_train_feat = add_ratio_features(df_rent_train_feat)
    df_rent_drift_feat = add_city_tier(df_rent_drift_feat, TIER_MAP)
    df_rent_drift_feat = add_ratio_features(df_rent_drift_feat)

    # Compute rental locality encodings (rent_sqft median per locality, from train only)
    rent_locality_medians = df_rent_train_feat.groupby("locality")["rent_sqft"].median().to_dict()
    rent_city_medians_val = df_rent_train_feat.groupby("city")["rent_sqft"].median().to_dict()

    # For rental we map locality_median_price_sqft to rent_sqft-based locality medians
    # and city_median_price_sqft to rent-based city medians, scaled to monthly rent level
    rent_city_medians_monthly = df_rent_train_feat.groupby("city")["rent_monthly"].median().to_dict()
    rent_city_stats = df_rent_train_feat.groupby("city")["rent_sqft"].agg(["mean", "std"]).to_dict("index")

    # Apply city/locality encodings to both rental splits
    for df_name, df_r in [("rent_train", df_rent_train_feat), ("rent_drift", df_rent_drift_feat)]:
        global_rent_median = np.median(list(rent_city_medians_val.values()))
        df_r["city_median_price_sqft"] = df_r["city"].map(rent_city_medians_val).fillna(global_rent_median)
        df_r["locality_median_price_sqft"] = df_r["locality"].map(rent_locality_medians)
        unseen = df_r["locality_median_price_sqft"].isna()
        df_r.loc[unseen, "locality_median_price_sqft"] = df_r.loc[unseen, "city"].map(rent_city_medians_val)
        df_r["locality_median_price_sqft"] = df_r["locality_median_price_sqft"].fillna(global_rent_median)

        # Z-score for rental
        df_r["price_sqft_city_zscore"] = df_r.apply(
            lambda row: (
                (row.get("rent_sqft", 0) - rent_city_stats.get(row["city"], {"mean": global_rent_median})["mean"])
                / max(rent_city_stats.get(row["city"], {"std": 1.0})["std"], 1.0)
            ),
            axis=1,
        ).clip(-ZSCORE_CAP, ZSCORE_CAP)

        # Interaction features
        df_r["hpi_tier_interaction"] = df_r["rbi_hpi_avg"] * df_r["city_tier_encoded"]
        df_r["sqft_city_interaction"] = df_r["total_sqft"] * df_r["city_tier_encoded"]

    # Update the outer variables
    df_rent_train_feat = df_rent_train_feat
    df_rent_drift_feat = df_rent_drift_feat

    # Verify
    for feat_col in FINAL_FEATURE_COLS:
        for rn, rdf in [("rent_train", df_rent_train_feat), ("rent_drift", df_rent_drift_feat)]:
            assert feat_col in rdf.columns, f"{rn} missing feature: {feat_col}"
    assert TARGET_RENTAL in df_rent_train_feat.columns, f"rent_train missing target: {TARGET_RENTAL}"

    print(f"\n  Rent train features: {len(df_rent_train_feat):,} rows x {len(FINAL_FEATURE_COLS)} features")
    print(f"  Rent drift features: {len(df_rent_drift_feat):,} rows x {len(FINAL_FEATURE_COLS)} features")
    logger.info("Rental features applied to both splits")

except Exception as exc:
    logger.error("Rental feature engineering failed: %s", exc)

# %% [markdown]
# ## Cell 10 -- Feature Correlation Analysis
#
# **Why:** Understanding which features correlate most strongly with the target
# guides model interpretation and identifies potential redundancies. The
# horizontal bar chart is a presentation-ready visual for stakeholders.

# %%
# Compute correlations with target on train
corr_with_target = df_train_feat[FINAL_FEATURE_COLS + [TARGET_SALE]].corr()[TARGET_SALE].drop(TARGET_SALE)
corr_sorted = corr_with_target.abs().sort_values(ascending=False)

# Print table
print(f"\n{'=' * 55}")
print(f"  FEATURE CORRELATION WITH {TARGET_SALE} (TRAIN)")
print(f"{'=' * 55}")
for feat in corr_sorted.index:
    val = corr_with_target[feat]
    bar_len = int(abs(val) * 20)
    bar = "#" * bar_len
    sign = "+" if val >= 0 else "-"
    print(f"  {feat:<30}: {sign}{abs(val):.3f}  {bar}")
print(f"{'=' * 55}\n")

# Save correlation chart
try:
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in corr_with_target[corr_sorted.index]]
    ax.barh(range(len(corr_sorted)), corr_with_target[corr_sorted.index].values, color=colors)
    ax.set_yticks(range(len(corr_sorted)))
    ax.set_yticklabels(corr_sorted.index, fontsize=10)
    ax.set_xlabel("Pearson Correlation", fontsize=12)
    ax.set_title(f"Feature Correlations with {TARGET_SALE}", fontsize=14, fontweight="bold")
    ax.invert_yaxis()
    ax.axvline(x=0, color="black", linewidth=0.5)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    chart_path = OUTPUT_DIR / "feature_correlations.png"
    fig.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Correlation chart saved to %s", chart_path)
except Exception as exc:
    logger.warning("Chart generation failed: %s", exc)

# %% [markdown]
# ## Cell 11 -- Save All Feature Files & Report
#
# **Why:** Persisting feature files ensures Notebook 04 (Model Training) can load
# them directly. The `feature_report.json` captures all metadata needed for
# reproducibility and model governance documentation.

# %%
# Define save columns
SAVE_COLS_SALE = FINAL_FEATURE_COLS + [TARGET_SALE]
SAVE_COLS_RENTAL = [c for c in FINAL_FEATURE_COLS if c in df_rent_train_feat.columns] + [TARGET_RENTAL]

# Save sale feature files
df_train_feat[SAVE_COLS_SALE].to_csv(PROCESSED_DIR / "features_train.csv", index=False)
df_val_feat[SAVE_COLS_SALE].to_csv(PROCESSED_DIR / "features_val.csv", index=False)
df_drift_feat[SAVE_COLS_SALE].to_csv(PROCESSED_DIR / "features_drift.csv", index=False)

# Save rental feature files
df_rent_train_feat[SAVE_COLS_RENTAL].to_csv(PROCESSED_DIR / "features_rent_train.csv", index=False)
df_rent_drift_feat[SAVE_COLS_RENTAL].to_csv(PROCESSED_DIR / "features_rent_drift.csv", index=False)

# Build feature report
correlations_dict = {k: round(float(v), 4) for k, v in corr_with_target.items()}

feature_report = {
    "generated_at": datetime.now().isoformat(),
    "project": "PropertyIQ",
    "notebook": "03_feature_engineering",
    "feature_count": len(FINAL_FEATURE_COLS),
    "feature_names": FINAL_FEATURE_COLS,
    "train_rows": int(len(df_train_feat)),
    "val_rows": int(len(df_val_feat)),
    "drift_rows": int(len(df_drift_feat)),
    "rent_train_rows": int(len(df_rent_train_feat)),
    "rent_drift_rows": int(len(df_rent_drift_feat)),
    "city_tier_map": TIER_MAP,
    "city_medians": {k: round(v, 2) for k, v in city_medians.items()},
    "top_correlations": dict(sorted(correlations_dict.items(), key=lambda x: abs(x[1]), reverse=True)),
    "unseen_localities_val": int(len(new_locs_val)),
    "unseen_localities_drift": int(len(new_locs_drift)),
    "feature_drift_shifts": feature_drift_shifts,
    "encodings_saved": "outputs/encodings.json",
}

report_path = OUTPUT_DIR / "feature_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(feature_report, f, indent=2, default=str)
assert report_path.exists()

# Print final manifest
files_manifest = {
    "features_train.csv": (len(df_train_feat), len(SAVE_COLS_SALE)),
    "features_val.csv": (len(df_val_feat), len(SAVE_COLS_SALE)),
    "features_drift.csv": (len(df_drift_feat), len(SAVE_COLS_SALE)),
    "features_rent_train.csv": (len(df_rent_train_feat), len(SAVE_COLS_RENTAL)),
    "features_rent_drift.csv": (len(df_rent_drift_feat), len(SAVE_COLS_RENTAL)),
}

print(f"\n{'=' * 55}")
print(f"  FILES SAVED -- data/processed/")
print(f"{'=' * 55}")
for fname, (rows, cols) in files_manifest.items():
    print(f"  [OK] {fname:<30} {rows:>6,} rows x {cols} cols")
print(f"\n  outputs/feature_report.json saved [OK]")
print(f"  outputs/encodings.json saved [OK]")
if (OUTPUT_DIR / "feature_correlations.png").exists():
    print(f"  outputs/feature_correlations.png saved [OK]")
print(f"{'=' * 55}\n")

logger.info("Notebook 03 complete -- all feature files saved to %s", PROCESSED_DIR)

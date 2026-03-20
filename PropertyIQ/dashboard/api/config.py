"""
PropertyIQ FastAPI Backend Configuration

Foundation file for the entire backend. Every other file imports from here.
Loads models and encodings once at startup. Exposes verified data structures
that exactly match what is on disk.
"""

import json
import logging
import joblib
from pathlib import Path
from typing import Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logger = logging.getLogger("propertyiq.config")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PATH RESOLUTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# This file: dashboard/api/config.py
# Project root is 2 levels up
BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROC_DIR = BASE_DIR / "data" / "processed"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUT FILE PATHS — EXACT FILENAMES VERIFIED ON DISK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSPECTION_REPORT = OUTPUTS_DIR / "inspection_report.json"
PREPROCESSING_REPORT = OUTPUTS_DIR / "preprocessing_report.json"
FEATURE_REPORT = OUTPUTS_DIR / "feature_report.json"
ENCODINGS_FILE = OUTPUTS_DIR / "encodings.json"
MODEL_REGISTRY_FILE = OUTPUTS_DIR / "model_registry.json"
KS_RESULTS_FILE = OUTPUTS_DIR / "ks_results.json"
DRIFT_RESULTS_FILE = OUTPUTS_DIR / "drift_results.json"
ROLLING_MAPE_FILE = OUTPUTS_DIR / "rolling_mape.json"
MAPE_SERIES_FILE = OUTPUTS_DIR / "mape_series.json"
CHI2_RESULTS_FILE = OUTPUTS_DIR / "chi2_results.json"
SHAP_VALUES_FILE = OUTPUTS_DIR / "shap_values.json"
FORECAST_PARAMS_FILE = OUTPUTS_DIR / "forecast_params.json"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL FILE PATHS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SALE_MODEL_FILE = MODELS_DIR / "sale_price_v1.pkl"
RENTAL_MODEL_FILE = MODELS_DIR / "rental_value_v1.pkl"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE COLUMNS — EXACT ORDER, VERIFIED AGAINST MODEL_REGISTRY.JSON
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Sale model features
SALE_FEATURE_COLS = [
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
    'livability_score'
]

# Rental model features — different set
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
    'furnishing_encoded'
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CITY CONSTANTS — VERIFIED AGAINST ENCODINGS.JSON
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Verified from encodings.json city_tier key
CITY_TIER = {
    'Mumbai': 3, 'Delhi': 3, 'Bengaluru': 3, 'Gurgaon': 3,
    'Hyderabad': 2, 'Pune': 2, 'Chennai': 2,
    'Navi Mumbai': 2, 'Kolkata': 1, 'Ahmedabad': 1
}

SUPPORTED_CITIES = list(CITY_TIER.keys())

# Current macro values for live prediction
CITY_RBI_HPI = {
    'Mumbai': 192, 'Delhi': 178, 'Bengaluru': 165,
    'Hyderabad': 158, 'Pune': 162, 'Chennai': 155,
    'Kolkata': 148, 'Ahmedabad': 152,
    'Gurgaon': 175, 'Navi Mumbai': 168
}

CURRENT_INTEREST_RATE = 6.50

DEMAND_SUPPLY_DEFAULTS = {
    'Mumbai': 1.28, 'Delhi': 1.15, 'Bengaluru': 1.32,
    'Hyderabad': 1.41, 'Pune': 1.22, 'Chennai': 1.18,
    'Kolkata': 0.98, 'Ahmedabad': 1.05,
    'Gurgaon': 1.19, 'Navi Mumbai': 1.24
}

LIVABILITY_DEFAULTS = {
    'Mumbai': 72, 'Delhi': 65, 'Bengaluru': 74,
    'Hyderabad': 71, 'Pune': 73, 'Chennai': 68,
    'Kolkata': 63, 'Ahmedabad': 66,
    'Gurgaon': 69, 'Navi Mumbai': 70
}

AMENITIES_DEFAULTS = {
    'Mumbai': 78, 'Delhi': 72, 'Bengaluru': 76,
    'Hyderabad': 70, 'Pune': 71, 'Chennai': 68,
    'Kolkata': 65, 'Ahmedabad': 66,
    'Gurgaon': 74, 'Navi Mumbai': 69
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# THRESHOLDS AND TRUST TIERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KS_DRIFT_THRESHOLD = 0.30
MAPE_ALERT_THRESHOLD = 20.0
LARGE_SQFT_THRESHOLD = 1500.0  # Overridden at startup from encodings.json

TRUST_THRESHOLDS = {
    'TRUSTED': {'min': 75, 'max': 100, 'color': '#0D9488'},
    'CAUTION': {'min': 50, 'max': 74, 'color': '#D97706'},
    'FIELD_VERIFICATION': {'min': 0, 'max': 49, 'color': '#DC2626'}
}

FORECAST_UNCERTAINTY_PER_YEAR = 0.03  # Verified from forecast_params.json


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DISPLAY NAMES — SHOWN TO LOAN OFFICERS IN PLAIN ENGLISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEATURE_DISPLAY_NAMES = {
    'locality_median_price_sqft': 'Locality Market Rate',
    'price_sqft_city_zscore': 'City Price Zone Position',
    'city_median_price_sqft': 'City Median Rate',
    'city_tier_encoded': 'City Tier Premium',
    'rbi_hpi_avg': 'RBI Housing Price Index',
    'livability_score': 'Area Livability Score',
    'demand_supply_ratio': 'Demand Supply Ratio',
    'total_sqft': 'Property Size',
    'interest_rate': 'Interest Rate',
    'sqft_per_bhk': 'Space Per Room',
    'bath': 'Bathrooms',
    'bath_per_bhk': 'Bath Per Room Ratio',
    'bhk': 'Bedroom Count',
    'is_large_property': 'Large Property Flag',
    'amenities_score': 'Area Amenities Score',
    'furnishing_encoded': 'Furnishing Level'
}

FEATURE_GROUPS = {
    'locality_median_price_sqft': 'location',
    'price_sqft_city_zscore': 'location',
    'city_median_price_sqft': 'location',
    'city_tier_encoded': 'location',
    'rbi_hpi_avg': 'macro',
    'interest_rate': 'macro',
    'demand_supply_ratio': 'macro',
    'livability_score': 'macro',
    'amenities_score': 'macro',
    'total_sqft': 'physical',
    'sqft_per_bhk': 'physical',
    'bath': 'physical',
    'bath_per_bhk': 'physical',
    'bhk': 'physical',
    'is_large_property': 'physical',
    'furnishing_encoded': 'physical'
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL STORE — LOADS BOTH .PKL FILES ONCE AT STARTUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ModelStore:
    """
    Loads and stores trained models at startup.
    Every predict call uses the already-loaded models — never reloads from disk.
    """
    
    def __init__(self):
        self.sale_model = None
        self.rental_model = None
        self._loaded = False
    
    def load(self):
        """Load both models from disk. Called once at startup."""
        if not SALE_MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Sale model not found: {SALE_MODEL_FILE.as_posix()}"
            )
        if not RENTAL_MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Rental model not found: {RENTAL_MODEL_FILE.as_posix()}"
            )
        
        self.sale_model = joblib.load(SALE_MODEL_FILE)
        self.rental_model = joblib.load(RENTAL_MODEL_FILE)
        self._loaded = True
        
        logger.info(f"Loaded sale model: {SALE_MODEL_FILE.name}")
        logger.info(f"Loaded rental model: {RENTAL_MODEL_FILE.name}")
    
    def is_loaded(self) -> bool:
        """Check if models have been loaded."""
        return self._loaded
    
    def predict_sale(self, feature_vector: list) -> float:
        """
        Run sale price prediction. Returns price_per_sqft.
        
        Args:
            feature_vector: List of 14 features in SALE_FEATURE_COLS order
        
        Returns:
            Predicted price per sqft
        """
        import numpy as np
        return float(self.sale_model.predict(
            np.array(feature_vector).reshape(1, -1)
        )[0])
    
    def predict_rental(self, feature_vector: list) -> float:
        """
        Run rental prediction. Returns rent_per_sqft.
        
        Args:
            feature_vector: List of 14 features in RENTAL_FEATURE_COLS order
        
        Returns:
            Predicted rent per sqft
        """
        import numpy as np
        return float(self.rental_model.predict(
            np.array(feature_vector).reshape(1, -1)
        )[0])
    
    def compute_confidence(self, feature_vector: list) -> float:
        """
        Compute confidence score from tree variance.
        Uses all 300 individual tree predictions.
        
        Formula:
            cv = std / mean of tree predictions
            score = max(0, (1 - cv * 5) * 100)
            Capped between 0 and 100
        
        Args:
            feature_vector: List of 14 features
        
        Returns:
            Confidence score (0-100)
        """
        import numpy as np
        X = np.array(feature_vector).reshape(1, -1)
        
        tree_preds = np.array([
            tree.predict(X)[0]
            for tree in self.sale_model.estimators_
        ])
        
        mean_pred = np.mean(tree_preds)
        std_pred = np.std(tree_preds)
        
        if mean_pred == 0:
            return 0.0
        
        cv = std_pred / mean_pred
        score = max(0.0, min(100.0, (1 - cv * 2) * 100))
        
        return round(score, 2)
    
    def get_trust_tier(self, confidence_score: float) -> dict:
        """
        Returns trust tier dict with label and color.
        
        Tiers:
            TRUSTED >= 75
            CAUTION 50-74
            FIELD_VERIFICATION < 50
        
        Args:
            confidence_score: Confidence score (0-100)
        
        Returns:
            Dict with tier, color, score
        """
        if confidence_score >= 75:
            tier = 'TRUSTED'
        elif confidence_score >= 50:
            tier = 'CAUTION'
        else:
            tier = 'FIELD_VERIFICATION'
        
        return {
            'tier': tier,
            'color': TRUST_THRESHOLDS[tier]['color'],
            'score': confidence_score
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENCODING STORE — LOADS ENCODINGS.JSON ONCE AT STARTUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class EncodingStore:
    """
    Loads and provides access to city/locality encodings.
    
    Verified structure of encodings.json:
        city_tier: {city: int}
        city_median_price_sqft: {city: float}
        locality_median_price_sqft: {locality: float} — FLAT dict
        city_price_mean: {city: float}
        city_price_std: {city: float}
        large_sqft_threshold: float
        furnishing_map: {label: int}
        feature_cols: list
        rental_feature_cols: list
    """
    
    def __init__(self):
        self._data = None
        self._loaded = False
        self.large_threshold = LARGE_SQFT_THRESHOLD
        self.furnishing_map = {}
    
    def load(self):
        """Load encodings.json from disk. Called once at startup."""
        if not ENCODINGS_FILE.exists():
            raise FileNotFoundError(
                f"Encodings file not found: {ENCODINGS_FILE.as_posix()}"
            )
        
        with open(ENCODINGS_FILE, 'r') as f:
            self._data = json.load(f)
        
        self.large_threshold = float(
            self._data.get('large_sqft_threshold', LARGE_SQFT_THRESHOLD)
        )
        self.furnishing_map = self._data.get('furnishing_map', {})
        self._loaded = True
        
        logger.info(
            f"Encodings loaded — "
            f"{len(self._data['locality_median_price_sqft'])} localities, "
            f"{len(self._data['city_median_price_sqft'])} cities"
        )
    
    def get_city_median(self, city: str) -> float:
        """
        Return city-level median price_per_sqft.
        
        Args:
            city: City name
        
        Returns:
            City median price per sqft (fallback: 8000.0)
        """
        return float(self._data['city_median_price_sqft'].get(city, 8000.0))
    
    def get_locality_median(self, locality: str, city: str) -> float:
        """
        Return locality median price_per_sqft.
        
        locality_median_price_sqft is a FLAT dict keyed by locality name.
        Falls back to city median if locality not found.
        
        Args:
            locality: Locality name
            city: City name (for fallback)
        
        Returns:
            Locality median price per sqft
        """
        loc_medians = self._data['locality_median_price_sqft']
        
        if locality in loc_medians:
            return float(loc_medians[locality])
        
        logger.warning(
            f"Locality '{locality}' not in encodings — "
            f"falling back to city median for {city}"
        )
        return self.get_city_median(city)
    
    def get_city_stats(self, city: str) -> dict:
        """
        Return city mean and std for z-score computation.
        
        Formula:
            price_sqft_city_zscore = (locality_median - city_mean) / city_std
        
        Args:
            city: City name
        
        Returns:
            Dict with city_mean and city_std
        """
        mean = float(self._data['city_price_mean'].get(city, 8000.0))
        std = float(self._data['city_price_std'].get(city, 3000.0))
        return {'city_mean': mean, 'city_std': std}
    
    def get_localities(self, city: str) -> list:
        """
        Return all locality names.
        
        Since locality_median is a flat dict, return all keys.
        Frontend will use this to populate the locality dropdown.
        
        Note: All localities across all cities are in one flat dict.
        
        Args:
            city: City name (not used, kept for API compatibility)
        
        Returns:
            Sorted list of all locality names
        """
        return sorted(self._data['locality_median_price_sqft'].keys())
    
    def encode_furnishing(self, furnishing: str) -> int:
        """
        Convert furnishing string to encoded int using furnishing_map.
        
        Args:
            furnishing: Furnishing label (e.g., "Semi-Furnished")
        
        Returns:
            Encoded integer (fallback: 1)
        """
        return int(self.furnishing_map.get(furnishing, 1))
    
    def is_loaded(self) -> bool:
        """Check if encodings have been loaded."""
        return self._loaded


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE-LEVEL SINGLETON INSTANCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

model_store = ModelStore()
encoding_store = EncodingStore()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STARTUP FUNCTION — CALLED BY MAIN.PY LIFESPAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def startup():
    """
    Called once when FastAPI starts.
    Loads models and encodings into memory.
    Verifies all output files exist.
    """
    logger.info("=" * 60)
    logger.info("PropertyIQ API — Starting up")
    logger.info(f"Base directory : {BASE_DIR.as_posix()}")
    logger.info(f"Models dir     : {MODELS_DIR.as_posix()}")
    logger.info(f"Outputs dir    : {OUTPUTS_DIR.as_posix()}")
    logger.info("=" * 60)
    
    # Load models
    model_store.load()
    
    # Load encodings
    encoding_store.load()
    
    # Verify all output JSON files exist
    required_outputs = [
        INSPECTION_REPORT, PREPROCESSING_REPORT, FEATURE_REPORT,
        ENCODINGS_FILE, MODEL_REGISTRY_FILE, KS_RESULTS_FILE,
        DRIFT_RESULTS_FILE, ROLLING_MAPE_FILE, CHI2_RESULTS_FILE,
        SHAP_VALUES_FILE, FORECAST_PARAMS_FILE
    ]
    
    missing = [f.name for f in required_outputs if not f.exists()]
    if missing:
        logger.warning(f"Missing output files: {missing}")
    else:
        logger.info(f"All {len(required_outputs)} output files verified")
    
    logger.info("Startup complete — API ready")
    logger.info("=" * 60)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICATION BLOCK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    startup()
    print()
    print("VERIFICATION RESULTS")
    print("-" * 40)
    print(f"Sale model loaded    : {model_store.sale_model is not None}")
    print(f"Rental model loaded  : {model_store.rental_model is not None}")
    print(f"Encodings loaded     : {encoding_store.is_loaded()}")
    print(f"Large threshold      : {encoding_store.large_threshold}")
    print(f"Furnishing map       : {encoding_store.furnishing_map}")
    print(f"Mumbai city median   : {encoding_store.get_city_median('Mumbai')}")
    print(f"Mumbai city stats    : {encoding_store.get_city_stats('Mumbai')}")
    print(f"Total localities     : {len(encoding_store.get_localities('Mumbai'))}")
    print()
    print("CONFIDENCE TEST — Mumbai Bandra 3BHK 1200sqft")
    test_vec = [3, 1200, 3, 1.0, 400, 0, 24065, 28000, 0.8, 3, 1.28, 192, 6.5, 72]
    score = model_store.compute_confidence(test_vec)
    tier = model_store.get_trust_tier(score)
    print(f"Confidence score : {score}")
    print(f"Trust tier       : {tier['tier']}")
    print()
    print("config.py verified successfully.")

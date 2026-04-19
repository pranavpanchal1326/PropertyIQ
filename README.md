# PropertyIQ

**Enterprise-style Property Valuation & ML Drift Monitoring Platform**

PropertyIQ is an end-to-end system that combines:
- **live property valuation**
- **model drift detection**
- **confidence scoring**
- **prediction explainability**
- **city-level trend analytics**

for risk-sensitive credit workflows.

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Business Problem](#2-business-problem)
- [3. Solution Overview](#3-solution-overview)
- [4. Key Results](#4-key-results)
- [5. Product Interfaces](#5-product-interfaces)
- [6. System Architecture](#6-system-architecture)
- [7. Data Design](#7-data-design)
- [8. ML Pipeline](#8-ml-pipeline)
- [9. Feature Engineering](#9-feature-engineering)
- [10. Modeling Strategy](#10-modeling-strategy)
- [11. Drift Detection Framework](#11-drift-detection-framework)
- [12. Explainability Framework](#12-explainability-framework)
- [13. Forecasting Method](#13-forecasting-method)
- [14. API Contract](#14-api-contract)
- [15. Tech Stack](#15-tech-stack)
- [16. Repository Structure](#16-repository-structure)
- [17. Local Setup](#17-local-setup)
- [18. Reproducibility & Data Integrity](#18-reproducibility--data-integrity)
- [19. Limitations](#19-limitations)
- [20. Roadmap](#20-roadmap)
- [21. Screenshots](#21-screenshots)
- [22. License](#22-license)
- [23. Contact](#23-contact)

---

## 1. Executive Summary

PropertyIQ addresses a practical lending problem: valuation models trained on historical data degrade when market distributions shift.  
The platform continuously evaluates model reliability and translates statistical signals into decision-ready outputs for analysts and loan officers.

**Outcome:** strong valuation performance on validation data and explicit drift alerts on out-of-period data.

---

## 2. Business Problem

In collateral-backed lending, incorrect valuation affects downstream credit decisions (e.g., LTV assessment).  
When market conditions shift, models can remain in production without obvious failure flags.

### Risk if unmanaged
- silent valuation bias
- inaccurate risk pricing
- weak early-warning visibility
- delayed retraining decisions

---

## 3. Solution Overview

PropertyIQ provides two integrated surfaces:

| Module | Primary User | Purpose |
|---|---|---|
| Admin Console | Risk Analyst | Monitor drift, model health, error trends, alerts |
| Client Portal | Loan Officer | Generate valuation, view trust score, inspect explanation |

### Core capabilities
- Continuous drift diagnostics (KS + Chi-square + rolling MAPE)
- Ensemble-based confidence scoring
- Trust-tier translation for non-ML users
- SHAP-style explainability outputs
- City-level forecast context

---

## 4. Key Results

| Metric | Value | Target |
|---|---:|---:|
| Sale Price MAPE | **1.61%** | < 15% |
| Rental Value MAPE | **19.64%** | < 25% |
| OOB R^2 (Sale) | **0.9968** | > 0.95 |
| Total Records | **600,000** | -- |
| Cities | **10** | -- |
| API Endpoints | **14** | -- |
| Max City KS | **0.5566 (Hyderabad)** | > 0.30 drift threshold |
| All City p-values | **< 0.05** | drift detected |

---

## 5. Product Interfaces

### 5.1 Admin Console
- Drift summary and severity
- Feature-level KS ranking
- City-level KS ranking
- Rolling MAPE windows
- Chi-square categorical drift
- Global feature influence view
- Alerts with recommendations

### 5.2 Client Portal
- Input property details
- Live model valuation
- Confidence score
- Trust tier:
  - `TRUSTED`
  - `CAUTION`
  - `FIELD VERIFICATION`
- Top prediction drivers
- Locality map
- City forecast panel

---

## 6. System Architecture

```text
                        +--------------------------------------+
                        |          Data Generation             |
                        |  properties_2020 / properties_2025  |
                        +--------------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------+
|                        Notebook / Offline ML Pipeline                      |
|  NB01 Inspection -> NB02 Preprocess -> NB03 Features -> NB04 Train Models |
|  NB05 Drift Analysis -> NB06 Explainability/Forecast Params                |
+----------------------------------------------------------------------------+
                                         |
                                         v
                     +----------------------------------+
                     |  Artifacts + JSON Outputs       |
                     |  *.pkl, encodings.json,         |
                     |  drift_results.json, shap.json  |
                     +----------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------+
|                             FastAPI Backend                                |
|  /api/predict/*  /api/drift/*  /api/model/*  /api/forecast/* /api/shap/*  |
+----------------------------------------------------------------------------+
                                         |
                                         v
                    +--------------------------------------+
                    |         React Frontend              |
                    |  Admin Console + Client Portal      |
                    +--------------------------------------+
```

### 6.1 Request Flow (valuation)
1. UI sends request to `POST /api/predict/valuation`
2. API loads cached model + encoding artifacts
3. API builds 14-feature vector in fixed order
4. RF predicts valuation
5. Tree-level variance converted into confidence score
6. Trust tier assigned and response returned to UI

---

## 7. Data Design

Two synthetic datasets, macro-anchored and reproducible:

| File | Year | Rows | Role |
|---|---:|---:|---|
| `properties_2020.csv` | 2020 | 300,000 | Train + validation source |
| `properties_2025.csv` | 2025 | 300,000 | Drift evaluation window |

### 7.1 Macro anchors used
- Housing index trend references
- Policy rate trend references
- City-wise growth priors
- Fixed random seeds (`2020`, `2025`) for reproducibility

### 7.2 Coverage
Mumbai, Delhi, Bengaluru, Hyderabad, Pune, Chennai, Kolkata, Ahmedabad, Gurgaon, Navi Mumbai.

---

## 8. ML Pipeline

| Notebook | Stage | Output |
|---|---|---|
| NB01 | Data inspection | `inspection_report.json` |
| NB02 | Preprocessing + splits | train/val/drift partitions |
| NB03 | Feature engineering | `encodings.json` |
| NB04 | Model training | `sale_price_v1.pkl`, `rental_value_v1.pkl` |
| NB05 | Drift detection | `ks_results.json`, `drift_results.json` |
| NB06 | Explainability + forecast | `shap_values.json`, `forecast_params.json` |

---

## 9. Feature Engineering

Final sale model uses 14 engineered features:

1. `bhk`
2. `total_sqft`
3. `bath`
4. `bath_per_bhk`
5. `sqft_per_bhk`
6. `is_large_property`
7. `city_median_price_sqft`
8. `locality_median_price_sqft`
9. `price_sqft_city_zscore`
10. `city_tier_encoded`
11. `demand_supply_ratio`
12. `rbi_hpi_avg`
13. `interest_rate`
14. `livability_score`

### Design choices
- Target-style encoding for city/locality price signals
- City-aware engineered context (z-score positioning)
- No scaling needed for tree-based model

---

## 10. Modeling Strategy

### 10.1 Sale Model
- `RandomForestRegressor`
- `n_estimators=300`
- `max_depth=10`
- `min_samples_leaf=4`
- `oob_score=True`

### 10.2 Rental Model
- Separate target and feature emphasis
- Includes rental-relevant factors (amenity/furnishing context)

### 10.3 Why Random Forest
- Handles non-linear interactions
- Works well on mixed tabular features
- Robust with limited heavy preprocessing
- Enables ensemble disagreement-based confidence signal

---

## 11. Drift Detection Framework

### 11.1 Statistical methods
- **KS-test** for continuous features
- **Chi-square** for categorical features
- **Rolling MAPE** for temporal degradation tracking

### 11.2 Severity interpretation (KS)
| KS Statistic | Interpretation |
|---|---|
| 0.00 - 0.10 | Minimal shift |
| 0.10 - 0.30 | Moderate shift |
| 0.30 - 0.60 | Significant drift |
| > 0.60 | Extreme drift |

### 11.3 Observed highlights
- Major macro feature drift detected
- Strong city-level heterogeneity
- Tail-window error spikes visible in rolling MAPE

---

## 12. Explainability Framework

PropertyIQ returns:
- Global feature influence summaries
- Per-request contribution drivers

Observed behavior in runs:
- Location-derived features dominate physical features for valuation impact in this dataset context.

---

## 13. Forecasting Method

City-level forecasts use implied annual growth from historical medians:

$$
\text{CAGR} = \left(\frac{\text{median}_{2025}}{\text{median}_{2020}}\right)^{1/5} - 1
$$

Projected values are generated across horizons with confidence bands for UI consumption.

---

## 14. API Contract

### 14.1 Drift
- `GET /api/drift/summary`
- `GET /api/drift/ks-features`
- `GET /api/drift/ks-cities`
- `GET /api/drift/rolling-mape`
- `GET /api/drift/chi2`
- `GET /api/drift/city/{city}`

### 14.2 Forecast
- `GET /api/forecast/all`
- `GET /api/forecast/{city}`

### 14.3 Model
- `GET /api/model/registry`
- `GET /api/model/shap`
- `GET /api/model/localities`
- `GET /api/model/localities/{city}`

### 14.4 Prediction / Explainability
- `POST /api/shap/explain`
- `POST /api/predict/valuation`

### 14.5 Sample request/response

```json
{
  "city": "Mumbai",
  "locality": "Bandra West",
  "bhk": 3,
  "bath": 3,
  "total_sqft": 1200
}
```

```json
{
  "predicted_price_sqft": 21067.0,
  "confidence_score": 81.0,
  "trust_tier": "CAUTION",
  "top_drivers": [
    "locality_median_price_sqft",
    "city_median_price_sqft",
    "price_sqft_city_zscore"
  ]
}
```

---

## 15. Tech Stack

| Layer | Tools |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn, scikit-learn, SciPy, Joblib |
| Frontend | React 18, Vite, Tailwind CSS, Recharts, Framer Motion, React Leaflet |
| Data/Graph | Neo4j |
| Serialization | JSON + Joblib artifacts |

---

## 16. Repository Structure

```text
dashboard/
|- api/
|  |- main.py
|  |- config.py
|  |- models/
|  \- routes/
|- frontend/
|- notebooks/
|- models/
|- outputs/
\- README.md
```

---

## 17. Local Setup

> Prerequisite: run NB01 -> NB06 to generate required artifacts.

### Backend
```bash
cd dashboard/api
pip install fastapi uvicorn pandas numpy scikit-learn joblib scipy
python -m uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

### Frontend
```bash
cd dashboard/frontend
npm install
npm run dev
# App: http://localhost:5173
```

---

## 18. Reproducibility & Data Integrity

- Fixed seeds for data generation and split control
- Train/validation sourced only from 2020 data
- 2025 data isolated as drift window
- Encoding artifacts fit on training data only
- API uses persisted artifacts for deterministic inference

---

## 19. Limitations

- Synthetic dataset (macro-anchored) rather than proprietary bank transaction logs
- Confidence score is ensemble-variance based, not full predictive interval modeling
- Forecasting uses simplified growth assumptions
- Production security/compliance hardening not included in local demo mode

---

## 20. Roadmap

- Model registry with version promotion policy
- Scheduled drift jobs + notification pipeline
- Retraining trigger automation with governance thresholds
- Role-based access and audit logging
- Containerized deployment + CI/CD
- Monitoring stack (latency, error, drift, prediction quality)

---

## 21. Screenshots

### 21.1 Landing Page

Landing page screenshots (use the image files below):

#### 21.1.1 Hero
![Landing Hero](docs/images/Landing%20page%201.png)

#### 21.1.2 Admin Preview Block
![Landing Admin Console Preview](docs/images/Landing%20page%202.png)

#### 21.1.3 Problem Section
![Landing Problem Section](docs/images/Landing%20page%203.png)

#### 21.1.4 Three Layers Section
![Landing Three Layers Section](docs/images/Landing%20page%204.png)

#### 21.1.5 Metrics Section
![Landing Metrics Section](docs/images/Landing%20page%205.png)

#### 21.1.6 Comparison Table
![Landing Comparison Table](docs/images/Landing%20page%206.png)

#### 21.1.7 RBI Alignment Section
![Landing RBI Alignment Section](docs/images/Landing%20page%207.png)

### 21.2 Admin Console

Admin Console screenshots (use the image files below):

#### 21.2.1 Drift Monitor Overview
![Admin Console Drift Monitor Overview](docs/images/admin%201.png)

#### 21.2.2 City-Level KS Drift Table
![Admin Console City-Level KS Drift Table](docs/images/admin%202.png)

#### 21.2.3 Model Health
![Admin Console Model Health](docs/images/admin%203.png)

#### 21.2.4 City Analytics
![Admin Console City Analytics](docs/images/admin%204.png)

#### 21.2.5 Alert Log
![Admin Console Alert Log](docs/images/admin%205.png)

### 21.3 Client Portal

Client Portal screenshots (use the image files below):


#### 21.3.1 Empty State
![Client Portal Empty State](docs/images/client%201.png)

#### 21.3.2 Valuation Result (Field Verification)
![Client Portal Valuation Result Field Verification](docs/images/client%202.png)

#### 21.3.3 Map and Market Context (Mumbai)
![Client Portal Map and Market Context Mumbai](docs/images/client%203.png)

#### 21.3.4 Forecast View (Mumbai)
![Client Portal Forecast View Mumbai](docs/images/client%204.png)

#### 21.3.5 Valuation Result (Trusted)
![Client Portal Valuation Result Trusted](docs/images/client%205.png)

#### 21.3.6 Map and Market Context (Pune)
![Client Portal Map and Market Context Pune](docs/images/client%206.png)

#### 21.3.7 Forecast View (Pune)
![Client Portal Forecast View Pune](docs/images/client%207.png)

---

## 22. License



---

## 23. Contact

- Name: Pranav Panchal
- LinkedIn: https://www.linkedin.com/in/pranavpanchal1326/
- GitHub: https://github.com/pranavpanchal1326

# PropertyIQ

B2B SaaS Property Valuation & Drift Detection Platform for Indian Banks

## What it does
- Detects ML model drift using KS-test across 11 features and 10 Indian cities
- Live property valuation using Random Forest (MAPE 1.61%)
- SHAP explainability — location dominates by 250x over physical features
- Trust Translation Layer: TRUSTED / CAUTION / FIELD VERIFICATION
- Price forecasting using implied CAGR from 600,000 observations

## Stack
Python 3.13 · scikit-learn · FastAPI · React + Vite · Framer Motion · Leaflet

## Run locally
Terminal 1 — Backend:
```bash
cd dashboard/api && python -m uvicorn main:app --reload --port 8000
```

Terminal 2 — Frontend:
```bash
cd dashboard/frontend && npm install && npm run dev
```

## Results
- Sale Price MAPE: 1.61% (target < 15%)
- OOB R²: 0.9968
- Drift Severity: HIGH (max city KS 0.5566, Hyderabad)
- All 10 cities p = 0.0000

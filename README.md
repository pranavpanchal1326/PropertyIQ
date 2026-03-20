# PropertyIQ — Property Valuation & Drift Detection Platform

B2B SaaS ML platform for Indian bank credit risk teams.

## What it does
- Detects ML model drift using KS-test across 11 features and 10 Indian cities
- Live property valuation using Random Forest — MAPE 1.61%
- SHAP explainability — location dominates price by 250x over physical features  
- Trust Translation Layer — TRUSTED / CAUTION / FIELD VERIFICATION
- Price forecasting using implied CAGR from 600,000 observations (2020-2025)

## Stack
Python 3.13 · scikit-learn · FastAPI · React 18 + Vite · Framer Motion · Leaflet · Recharts

## Results
| Metric | Value |
|--------|-------|
| Sale Price MAPE | 1.61% (target < 15%) |
| OOB R² | 0.9968 |
| Drift Severity | HIGH — max city KS 0.5566 (Hyderabad) |
| Cities tested | 10 — all p = 0.0000 |
| Training data | 600,000 Indian property records |

## Run locally

**Terminal 1 — Backend**
```bash
cd dashboard/api
pip install fastapi uvicorn pandas numpy scikit-learn joblib
python -m uvicorn main:app --reload --port 8000
# API docs at localhost:8000/docs
```

**Terminal 2 — Frontend**
```bash
cd dashboard/frontend
npm install
npm run dev
# App at localhost:5173
```

## Project Structure
```
PropertyIQ/
├── notebooks/          # NB01-NB06 ML pipeline
├── models/             # Trained .pkl files (not in repo — run NB04)
├── outputs/            # Pre-computed JSON outputs from notebooks
├── data/               # Raw and processed CSVs (not in repo — run generator)
└── dashboard/
    ├── api/            # FastAPI backend — 14 endpoints
    └── frontend/       # React + Vite dashboard
```

## Pages
- **Landing** `localhost:5173/` — Product pitch with real data
- **Admin Console** `localhost:5173/admin/drift` — Drift Monitor, Model Health, City Analytics
- **Client Portal** `localhost:5173/client` — Live ML prediction with map and forecast

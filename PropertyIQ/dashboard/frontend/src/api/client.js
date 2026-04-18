import axios from 'axios'

// ── Axios instance ────────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor — dev logging ─────────────────────────────────────────
api.interceptors.request.use(config => {
  if (import.meta.env.DEV) {
    console.log(
      `%c→ ${config.method?.toUpperCase()} ${config.url}`,
      'color: #2DD4BF; font-weight: 600;'
    )
  }
  return config
})

// ── Response interceptor — surface errors clearly ─────────────────────────────
api.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.detail || err.message
    console.error(
      `%c✗ API Error: ${msg}`,
      'color: #FF7B72; font-weight: 600;'
    )
    return Promise.reject(err)
  }
)

// ═══════════════════════════════════════════════════════════════════════════
// DRIFT ENDPOINTS
// Source: drift_results.json + ks_results.json + rolling_mape from drift_results
// ═══════════════════════════════════════════════════════════════════════════

/** Overall drift severity, counts, recommendation */
export const getDriftSummary  = () => api.get('/api/drift/summary')

/** All features ranked by KS stat descending */
export const getKSFeatures    = () => api.get('/api/drift/ks-features')

/** All 10 cities ranked by KS stat descending */
export const getKSCities      = () => api.get('/api/drift/ks-cities')

/** 600 rolling MAPE windows + alert threshold */
export const getRollingMAPE   = () => api.get('/api/drift/rolling-mape')

/** Chi-square results for categorical features */
export const getChi2          = () => api.get('/api/drift/chi2')

/** Drift data for a single city */
export const getCityDrift     = (city) => api.get(`/api/drift/city/${city}`)

// ═══════════════════════════════════════════════════════════════════════════
// FORECAST ENDPOINTS
// Source: forecast_params.json (implied CAGR from 2020→2025)
// ═══════════════════════════════════════════════════════════════════════════

/** Summary row for all 10 cities — sorted by CAGR descending */
export const getAllForecasts   = () => api.get('/api/forecast/all')

/** Full 5-horizon forecast for one city */
export const getCityForecast  = (city) => api.get(`/api/forecast/${encodeURIComponent(city)}`)

// ═══════════════════════════════════════════════════════════════════════════
// MODEL ENDPOINTS
// Source: model_registry.json + shap_values.json + encodings.json
// ═══════════════════════════════════════════════════════════════════════════

/** All trained models with MAPE, R², OOB, status */
export const getModelRegistry = () => api.get('/api/model/registry')

/** SHAP global feature importance ranked */
export const getModelSHAP     = () => api.get('/api/model/shap')

/** All 122 localities for Client Portal dropdown */
export const getLocalities    = () => api.get('/api/model/localities')

// ═══════════════════════════════════════════════════════════════════════════
// SHAP ENDPOINTS
// Source: shap_values.json + model_registry.json feature_importances
// ═══════════════════════════════════════════════════════════════════════════

/** Raw shap_values.json contents */
export const getSHAPGlobal    = () => api.get('/api/shap/global')

/**
 * Per-prediction SHAP explanation
 * @param {Object} body - Same shape as ValuationRequest
 */
export const explainPrediction = (body) => api.post('/api/shap/explain', body)

// ═══════════════════════════════════════════════════════════════════════════
// PREDICT ENDPOINT
// Core endpoint — runs live model prediction
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Live property valuation
 * @param {{
 *   city: string,
 *   locality: string,
 *   bhk: number,
 *   total_sqft: number,
 *   bath: number,
 *   property_type: string,
 *   furnishing: string
 * }} body
 */
export const predictValuation = (body) => api.post('/api/predict/valuation', body)

// ═══════════════════════════════════════════════════════════════════════════
// SYSTEM ENDPOINTS
// ═══════════════════════════════════════════════════════════════════════════

/** Health check — confirms models loaded, outputs present */
export const getHealth        = () => api.get('/health')

export default api

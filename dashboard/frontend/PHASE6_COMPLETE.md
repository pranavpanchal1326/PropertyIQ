# Phase 6 Complete — Model Health Page

## Status: ✅ COMPLETE

The complete Model Health page is now live at http://localhost:5173/admin/model

## Files Created

1. ✅ SHAPChart.jsx — Horizontal bar chart with feature groups and dominance callout
2. ✅ ModelTable.jsx — Model registry with MAPE, R², OOB, status badges
3. ✅ Chi2Table.jsx — Chi-square categorical drift results
4. ✅ ModelHealth.jsx — Main page assembling all components with real API data

## Page Layout

### Model Registry Table
- All trained models in one table
- Columns: Model, Target, Val MAPE, MAPE Target, OOB R², Confidence, Trained, Status
- LIVE status with pulsing green dot
- TARGET MET / BELOW TARGET badges with checkmark/x icons
- MAPE values colored green (met) or red (below target)
- Trained date formatted as "13 Mar 2026"
- Staggered row entrance (0.08s per row)
- Hover state on rows

### SHAP Chart (Left Column)
- 14 features grouped by: Location, Macro, Physical
- Horizontal bars growing from left
- Group dividers with labels
- Location dominance callout at top (teal badge)
- Color coding:
  - Location features: teal bars
  - Macro features: amber bars
  - Physical features: muted gray bars
- Mean |SHAP| values shown at bar end
- Base value displayed in header (₹8,438/sqft)
- Bars animate with spring easing (0.04s stagger)

### Chi-Square Table (Right Column Top)
- 2 categorical features tested
- Columns: Feature, Chi² Stat, P-Value, Drift
- Drifted features highlighted in amber
- HIGH/NONE severity badges
- Compact 2-row table

### Key Insight Card (Right Column Bottom)
- Teal "KEY INSIGHT" label
- Natural language summary of SHAP findings
- Highlights top feature (locality_median_price_sqft)
- Shows location dominance ratio (14×)
- Compares location vs physical feature importance

## Data Flow

### useModel Hook
Fetches 2 endpoints in parallel:
1. /api/model/registry
2. /api/model/shap

Returns: `{ data: { registry, shap }, loading, error }`

### Chi2 Data
Fetched separately via getChi2() in useEffect
- Not included in useModel hook
- Separate loading state

### Loading States
- SkeletonTable for model registry
- SkeletonChart for SHAP (height 320px)
- SkeletonChart for Chi2 (height 200px)

### Error State
- Simple red text error message
- Shows error details from API

## Animations

### Page Level
- Staggered section entrance (0.08s between sections)
- Fade + slide up (y: 12px)

### Model Table
- Rows stagger in (0.08s per row)
- Hover background change
- LIVE status pulsing dot

### SHAP Chart
- Bars grow from 0 to full width
- Spring easing for premium feel
- Stagger: 0.04s per bar
- Group dividers appear with bars

### Chi2 Table
- Rows stagger in (0.08s per row)
- Hover background change

## Visual Quality

- ✅ Matches design language of Drift Monitor
- ✅ All data from live backend (no hardcoded values)
- ✅ Professional animations via Framer Motion
- ✅ Proper loading and error states
- ✅ Responsive grid layouts
- ✅ CSS variables for all colors
- ✅ Monospace fonts for numeric values

## Browser Test

Navigate to: http://localhost:5173/admin/model

You should see:
1. Model registry table with 2 models (sale_price_v1, rental_value_v1)
2. SHAP chart with 14 features grouped by type
3. Chi-square table with 2 categorical features
4. Key insight card explaining location dominance

## API Requirements

Backend must be running at http://localhost:8000 with these endpoints:
- GET /api/model/registry
- GET /api/model/shap
- GET /api/drift/chi2

## Key Insights Displayed

1. Location dominates by 14× margin
2. locality_median_price_sqft is the top predictor
3. Physical features combined have minimal impact
4. Both categorical features (property_type, furnishing) show drift

## Next Steps (Phase 7)

Build City Analytics page with:
- City selector dropdown
- Forecast chart (5-year projection)
- City-specific drift metrics
- Price distribution comparison

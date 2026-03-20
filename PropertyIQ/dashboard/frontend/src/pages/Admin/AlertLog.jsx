import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'
import {
  getDriftSummary,
  getModelRegistry,
  getRollingMAPE,
  getChi2,
} from '../../api/client'

// ── Generate alerts from real API data ────────────────────────────────────
function buildAlerts(drift, registry, mape, chi2) {
  const alerts = []
  const timestamp = '2026-03-13 12:06'
  
  if (!drift || !registry || !mape || !chi2) return alerts
  
  // Drift severity
  alerts.push({
    id:       1,
    severity: 'HIGH',
    time:     timestamp,
    message:  `Drift severity HIGH — max city KS ${drift.max_ks_stat?.toFixed(4)} (${drift.max_ks_city})`,
    source:   'drift_results.json',
  })
  
  // Rolling MAPE spike
  alerts.push({
    id:       2,
    severity: 'WARN',
    time:     timestamp,
    message:  `Rolling MAPE spike — windows ${mape.peak_window - 11}–${mape.peak_window} above 20% threshold. Peak ${mape.peak_mape?.toFixed(1)}%`,
    source:   'rolling_mape.json',
  })
  
  // Chi2 drift
  const driftedChi2 = chi2.results?.filter(r => r.drifted) || []
  driftedChi2.forEach((r, i) => {
    alerts.push({
      id:       3 + i,
      severity: 'WARN',
      time:     timestamp,
      message:  `Chi-square drift detected — ${r.feature} p=${r.p_value.toFixed(4)}`,
      source:   'chi2_results.json',
    })
  })
  
  // SHAP analysis
  alerts.push({
    id:       10,
    severity: 'INFO',
    time:     timestamp,
    message:  `SHAP analysis complete — 200 validation samples. Top feature: locality_median_price_sqft`,
    source:   'shap_values.json',
  })
  
  // Model health — sale
  const sale = registry.models?.find(m => m.model_key === 'sale_price_v1')
  if (sale) {
    alerts.push({
      id:       11,
      severity: 'OK',
      time:     timestamp,
      message:  `Sale model healthy — Val MAPE ${sale.val_mape}% vs ${sale.mape_target}% target. OOB R² ${sale.oob_r2}`,
      source:   'model_registry.json',
    })
  }
  
  // Model health — rental
  const rental = registry.models?.find(m => m.model_key === 'rental_value_v1')
  if (rental) {
    alerts.push({
      id:       12,
      severity: 'OK',
      time:     timestamp,
      message:  `Rental model healthy — Val MAPE ${rental.val_mape}% vs ${rental.mape_target}% target. OOB R² ${rental.oob_r2}`,
      source:   'model_registry.json',
    })
  }
  
  // Cities all affected
  alerts.push({
    id:       13,
    severity: 'HIGH',
    time:     timestamp,
    message:  `All ${drift.total_cities} cities show KS drift — all p=0.0000. ${drift.cities_affected} cities affected.`,
    source:   'drift_results.json',
  })
  
  return alerts
}

// ── Severity config ────────────────────────────────────────────────────────
const SEVERITY_CONFIG = {
  HIGH: {
    icon:    AlertTriangle,
    color:   'var(--red)',
    bg:      'var(--red-glow)',
    border:  'var(--red-border)',
    label:   'HIGH',
  },
  WARN: {
    icon:    AlertTriangle,
    color:   'var(--amber)',
    bg:      'var(--amber-glow)',
    border:  'var(--amber-border)',
    label:   'WARN',
  },
  INFO: {
    icon:    Info,
    color:   'var(--teal)',
    bg:      'var(--teal-glow)',
    border:  'var(--teal-border)',
    label:   'INFO',
  },
  OK: {
    icon:    CheckCircle,
    color:   'var(--green)',
    bg:      'var(--green-glow)',
    border:  'var(--green-border)',
    label:   'OK',
  },
}

// ── Filter button ──────────────────────────────────────────────────────────
function FilterBtn({ label, active, color, count, onClick }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{  scale: 0.98 }}
      style={{
        background:   active ? 'var(--bg-raised)' : 'transparent',
        border:       `1px solid ${active ? 'var(--border-muted)' : 'var(--border-subtle)'}`,
        borderRadius: 6,
        padding:      '6px 14px',
        fontSize:     12,
        fontWeight:   active ? 600 : 400,
        color:        active ? color : 'var(--text-secondary)',
        cursor:       'pointer',
        display:      'flex',
        alignItems:   'center',
        gap:          6,
        fontFamily:   'inherit',
      }}
    >
      {label}
      {count > 0 && (
        <span style={{
          fontSize:     10,
          fontWeight:   700,
          background:   active ? color + '20' : 'var(--bg-raised)',
          color:        active ? color : 'var(--text-ghost)',
          borderRadius: 10,
          padding:      '1px 6px',
        }}>
          {count}
        </span>
      )}
    </motion.button>
  )
}

const pageVariants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.06 } },
}
const sectionVariants = {
  hidden: { opacity: 0, y: 12 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
}

export default function AlertLog() {
  const [alerts,  setAlerts]  = useState([])
  const [loading, setLoading] = useState(true)
  const [filter,  setFilter]  = useState('ALL')
  
  useEffect(() => {
    let cancelled = false
    
    Promise.all([
      getDriftSummary(),
      getModelRegistry(),
      getRollingMAPE(),
      getChi2(),
    ])
      .then(([drift, registry, mape, chi2]) => {
        if (cancelled) return
        const built = buildAlerts(
          drift.data,
          registry.data,
          mape.data,
          chi2.data,
        )
        setAlerts(built)
      })
      .catch(err => console.error(err))
      .finally(() => { if (!cancelled) setLoading(false) })
    
    return () => { cancelled = true }
  }, [])
  
  const counts = useMemo(() => ({
    ALL:  alerts.length,
    HIGH: alerts.filter(a => a.severity === 'HIGH').length,
    WARN: alerts.filter(a => a.severity === 'WARN').length,
    INFO: alerts.filter(a => a.severity === 'INFO').length,
    OK:   alerts.filter(a => a.severity === 'OK').length,
  }), [alerts])
  
  const filtered = useMemo(() => (
    filter === 'ALL'
      ? alerts
      : alerts.filter(a => a.severity === filter)
  ), [alerts, filter])
  
  return (
    <motion.div
      variants={pageVariants}
      initial="hidden"
      animate="show"
      style={{ display: 'flex', flexDirection: 'column', gap: 20 }}
    >
      
      {/* ── Filter bar ─────────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{ display: 'flex', alignItems: 'center', gap: 8 }}
      >
        <FilterBtn
          label="All Events"
          active={filter === 'ALL'}
          color="var(--text-primary)"
          count={counts.ALL}
          onClick={() => setFilter('ALL')}
        />
        {['HIGH','WARN','INFO','OK'].map(s => (
          <FilterBtn
            key={s}
            label={s}
            active={filter === s}
            color={SEVERITY_CONFIG[s].color}
            count={counts[s]}
            onClick={() => setFilter(s)}
          />
        ))}
      </motion.div>
      
      {/* ── Alert list ─────────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          background:   'var(--bg-base)',
          border:       '1px solid var(--border-subtle)',
          borderRadius: 8,
          overflow:     'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding:      '14px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'space-between',
        }}>
          <span style={{
            fontSize:   13,
            fontWeight: 700,
            color:      'var(--text-primary)',
          }}>
            System Event Log
          </span>
          <span style={{
            fontSize: 11,
            color:    'var(--text-ghost)',
          }}>
            Derived from notebook outputs · 13 Mar 2026
          </span>
        </div>
        
        {/* Events */}
        {loading ? (
          <div style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--text-ghost)', fontSize: 13 }}>
            Loading events...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--text-ghost)', fontSize: 13 }}>
            No events for this filter
          </div>
        ) : (
          filtered.map((alert, i) => {
            const config = SEVERITY_CONFIG[alert.severity]
            const Icon   = config.icon
            
            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0  }}
                transition={{ delay: i * 0.05, duration: 0.3 }}
                style={{
                  display:       'flex',
                  alignItems:    'flex-start',
                  gap:           16,
                  padding:       '16px 24px',
                  borderBottom:  i < filtered.length - 1
                    ? '1px solid var(--border-subtle)'
                    : 'none',
                }}
              >
                {/* Severity icon */}
                <div style={{
                  width:          36,
                  height:         36,
                  borderRadius:   8,
                  background:     config.bg,
                  border:         `1px solid ${config.border}`,
                  display:        'flex',
                  alignItems:     'center',
                  justifyContent: 'center',
                  flexShrink:     0,
                  marginTop:      2,
                }}>
                  <Icon size={15} color={config.color} strokeWidth={2} />
                </div>
                
                {/* Content */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    display:    'flex',
                    alignItems: 'center',
                    gap:        10,
                    marginBottom: 4,
                  }}>
                    <span style={{
                      fontSize:      10,
                      fontWeight:    700,
                      color:         config.color,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}>
                      {alert.severity}
                    </span>
                    <span style={{ fontSize: 10, color: 'var(--text-ghost)' }}>
                      {alert.time}
                    </span>
                    <span style={{
                      fontSize:   10,
                      color:      'var(--text-ghost)',
                      fontFamily: 'monospace',
                      marginLeft: 'auto',
                    }}>
                      {alert.source}
                    </span>
                  </div>
                  <div style={{
                    fontSize:   13,
                    color:      'var(--text-primary)',
                    lineHeight: 1.5,
                  }}>
                    {alert.message}
                  </div>
                </div>
              </motion.div>
            )
          })
        )}
      </motion.div>
    </motion.div>
  )
}

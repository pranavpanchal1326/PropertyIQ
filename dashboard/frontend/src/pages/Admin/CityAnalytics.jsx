import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, TrendingUp, MapPin, Activity } from 'lucide-react'
import { getCityForecast, getCityDrift } from '../../api/client'
import ForecastChart  from '../../components/charts/ForecastChart'
import SeverityBadge  from '../../components/ui/SeverityBadge'
import AnimatedNumber from '../../components/ui/AnimatedNumber'
import { SkeletonChart, SkeletonStatCard } from '../../components/ui/SkeletonCard'

const CITIES = [
  'Mumbai','Delhi','Bengaluru','Hyderabad',
  'Pune','Chennai','Kolkata','Ahmedabad',
  'Gurgaon','Navi Mumbai',
]

const CONFIDENCE_COLOR = {
  HIGH:   'var(--green)',
  MEDIUM: 'var(--amber)',
  LOW:    'var(--text-ghost)',
}

const pageVariants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.07 } },
}
const sectionVariants = {
  hidden: { opacity: 0, y: 12 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
}

export default function CityAnalytics() {
  const [city,          setCity]          = useState('Mumbai')
  const [forecastData,  setForecastData]  = useState(null)
  const [driftData,     setDriftData]     = useState(null)
  const [loading,       setLoading]       = useState(true)
  
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    
    Promise.all([
      getCityForecast(city),
      getCityDrift(city),
    ])
      .then(([forecast, drift]) => {
        if (cancelled) return
        setForecastData(forecast.data)
        setDriftData(drift.data)
      })
      .catch(err => console.error(err))
      .finally(() => { if (!cancelled) setLoading(false) })
    
    return () => { cancelled = true }
  }, [city])
  
  return (
    <motion.div
      variants={pageVariants}
      initial="hidden"
      animate="show"
      style={{ display: 'flex', flexDirection: 'column', gap: 20 }}
    >
      
      {/* ── City selector ──────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          display:    'flex',
          alignItems: 'center',
          gap:        12,
        }}
      >
        <span style={{
          fontSize:   13,
          color:      'var(--text-secondary)',
          whiteSpace: 'nowrap',
        }}>
          Analysing city:
        </span>
        <div style={{ position: 'relative' }}>
          <select
            value={city}
            onChange={e => setCity(e.target.value)}
            style={{
              appearance:   'none',
              background:   'var(--bg-base)',
              border:       '1px solid var(--border-muted)',
              borderRadius: 6,
              padding:      '8px 36px 8px 14px',
              fontSize:     14,
              fontWeight:   600,
              color:        'var(--text-primary)',
              cursor:       'pointer',
              outline:      'none',
              fontFamily:   'inherit',
            }}
          >
            {CITIES.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <ChevronDown
            size={14}
            color="var(--text-ghost)"
            strokeWidth={1.5}
            style={{
              position:      'absolute',
              right:         12,
              top:           '50%',
              transform:     'translateY(-50%)',
              pointerEvents: 'none',
            }}
          />
        </div>
      </motion.div>
      
      {/* ── City stat cards ────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          display:             'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap:                 16,
        }}
      >
        {loading ? (
          Array(4).fill(0).map((_, i) => <SkeletonStatCard key={i} />)
        ) : forecastData && driftData ? (
          <>
            {/* Current median */}
            <div style={{
              background:   'var(--bg-base)',
              border:       '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding:      '20px 24px',
            }}>
              <div style={{
                fontSize:      10,
                fontWeight:    600,
                color:         'var(--text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                marginBottom:  12,
              }}>
                Current Median
              </div>
              <AnimatedNumber
                value={forecastData.current_median}
                decimals={0}
                prefix="₹"
                suffix="/sqft"
                style={{
                  fontSize:   24,
                  fontWeight: 800,
                  color:      'var(--teal)',
                  display:    'block',
                  marginBottom: 6,
                }}
              />
              <div style={{ fontSize: 11, color: 'var(--text-ghost)' }}>
                2025 dataset median
              </div>
            </div>
            
            {/* CAGR */}
            <div style={{
              background:   'var(--bg-base)',
              border:       '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding:      '20px 24px',
            }}>
              <div style={{
                fontSize:      10,
                fontWeight:    600,
                color:         'var(--text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                marginBottom:  12,
              }}>
                Annual Growth Rate
              </div>
              <AnimatedNumber
                value={forecastData.cagr_pct}
                decimals={2}
                suffix="%"
                style={{
                  fontSize:   24,
                  fontWeight: 800,
                  color:      'var(--green)',
                  display:    'block',
                  marginBottom: 6,
                }}
              />
              <div style={{ fontSize: 11, color: 'var(--text-ghost)' }}>
                Implied CAGR 2020→2025
              </div>
            </div>
            
            {/* KS Stat */}
            <div style={{
              background:   'var(--bg-base)',
              border:       '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding:      '20px 24px',
            }}>
              <div style={{
                fontSize:      10,
                fontWeight:    600,
                color:         'var(--text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                marginBottom:  12,
              }}>
                KS Drift Stat
              </div>
              <AnimatedNumber
                value={driftData.ks_stat}
                decimals={4}
                style={{
                  fontSize:   24,
                  fontWeight: 800,
                  color:      'var(--red)',
                  display:    'block',
                  marginBottom: 6,
                }}
              />
              <div style={{ fontSize: 11, color: 'var(--text-ghost)' }}>
                p = {driftData.p_value.toFixed(4)} · all cities p=0.0000
              </div>
            </div>
            
            {/* Price shift */}
            <div style={{
              background:   'var(--bg-base)',
              border:       '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding:      '20px 24px',
            }}>
              <div style={{
                fontSize:      10,
                fontWeight:    600,
                color:         'var(--text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                marginBottom:  12,
              }}>
                Price Shift
              </div>
              <AnimatedNumber
                value={driftData.price_shift_pct}
                decimals={2}
                prefix="+"
                suffix="%"
                style={{
                  fontSize:   24,
                  fontWeight: 800,
                  color:      'var(--red)',
                  display:    'block',
                  marginBottom: 6,
                }}
              />
              <div style={{ fontSize: 11, color: 'var(--text-ghost)' }}>
                2020 → 2025 appreciation
              </div>
            </div>
          </>
        ) : null}
      </motion.div>
      
      {/* ── Forecast chart + table row ─────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          display:             'grid',
          gridTemplateColumns: '1fr 360px',
          gap:                 20,
        }}
      >
        {/* Forecast chart */}
        {loading
          ? <SkeletonChart height={260} />
          : forecastData && (
            <ForecastChart
              forecastData={forecastData.forecast_points}
              currentMedian={forecastData.current_median}
              city={city}
            />
          )
        }
        
        {/* Forecast table */}
        {loading ? (
          <SkeletonChart height={260} />
        ) : forecastData ? (
          <div style={{
            background:   'var(--bg-base)',
            border:       '1px solid var(--border-subtle)',
            borderRadius: 8,
            overflow:     'hidden',
          }}>
            {/* Table header */}
            <div style={{
              padding:      '14px 20px',
              borderBottom: '1px solid var(--border-subtle)',
            }}>
              <span style={{
                fontSize:   13,
                fontWeight: 700,
                color:      'var(--text-primary)',
              }}>
                Forecast Projections
              </span>
            </div>
            
            {/* Column headers */}
            <div style={{
              display:             'grid',
              gridTemplateColumns: '70px 1fr 1fr 80px',
              padding:             '10px 20px',
              borderBottom:        '1px solid var(--border-subtle)',
              background:          'var(--bg-void)',
              gap:                 12,
            }}>
              {['HORIZON','PRICE','RANGE','CONF.'].map(h => (
                <div key={h} style={{
                  fontSize:      9,
                  fontWeight:    600,
                  color:         'var(--text-ghost)',
                  textTransform: 'uppercase',
                  letterSpacing: '1.5px',
                }}>
                  {h}
                </div>
              ))}
            </div>
            
            {/* Rows */}
            {forecastData.forecast_points.map((point, i) => (
              <motion.div
                key={point.horizon_label}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.06 }}
                style={{
                  display:             'grid',
                  gridTemplateColumns: '70px 1fr 1fr 80px',
                  padding:             '0 20px',
                  height:              44,
                  alignItems:          'center',
                  borderBottom:        i < forecastData.forecast_points.length - 1
                    ? '1px solid var(--border-subtle)'
                    : 'none',
                  gap:                 12,
                }}
              >
                <div style={{
                  fontSize:   12,
                  fontWeight: 700,
                  color:      'var(--teal)',
                  fontFamily: 'monospace',
                }}>
                  {point.horizon_label}
                </div>
                <div style={{
                  fontSize:   13,
                  fontWeight: 600,
                  color:      'var(--text-primary)',
                }}>
                  ₹{Math.round(point.projected_price).toLocaleString('en-IN')}
                </div>
                <div style={{
                  fontSize: 10,
                  color:    'var(--text-ghost)',
                }}>
                  {Math.round(point.lower_bound/1000)}K–{Math.round(point.upper_bound/1000)}K
                </div>
                <div style={{
                  fontSize:   10,
                  fontWeight: 600,
                  color:      CONFIDENCE_COLOR[point.confidence] || 'var(--text-ghost)',
                }}>
                  {point.confidence}
                </div>
              </motion.div>
            ))}
          </div>
        ) : null}
      </motion.div>
    </motion.div>
  )
}

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowUpRight, ArrowDownRight, AlertTriangle } from 'lucide-react'
import TrustBadge    from '../../components/ui/TrustBadge'
import AnimatedNumber from '../../components/ui/AnimatedNumber'
import PropertyMap   from '../../components/ui/PropertyMap'
import { getCityForecast } from '../../api/client'
import ForecastChart from '../../components/charts/ForecastChart'

// ── Section divider with centered label ───────────────────────────────────
function Divider({ label }) {
  return (
    <div style={{
      display:    'flex',
      alignItems: 'center',
      gap:        12,
      margin:     '24px 0',
    }}>
      <div style={{ flex: 1, height: 1, background: '#EAEEF2' }} />
      <span style={{
        fontSize:      9,
        fontWeight:    600,
        color:         '#8C959F',
        textTransform: 'uppercase',
        letterSpacing: '1.5px',
        whiteSpace:    'nowrap',
        background:    '#FFFFFF',
        padding:       '0 12px',
      }}>
        {label}
      </span>
      <div style={{ flex: 1, height: 1, background: '#EAEEF2' }} />
    </div>
  )
}

// ── Container and item variants ────────────────────────────────────────────
const container = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.07 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  show:   {
    opacity: 1,
    y:       0,
    transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
  },
}

// ── Forecast section component ─────────────────────────────────────────────
function ForecastSection({ city }) {
  const [forecast, setForecast] = useState(null)
  const [loading,  setLoading]  = useState(true)
  
  useEffect(() => {
    if (!city) return
    setLoading(true)
    getCityForecast(city)
      .then(r  => setForecast(r.data))
      .catch(() => setForecast(null))
      .finally(() => setLoading(false))
  }, [city])
  
  if (loading) return (
    <div style={{
      height:       160,
      background:   '#F6F8FA',
      borderRadius: 8,
      border:       '1px solid #D0D7DE',
      display:      'flex',
      alignItems:   'center',
      justifyContent:'center',
    }}>
      <div style={{ fontSize: 12, color: '#8C959F' }}>Loading forecast...</div>
    </div>
  )
  
  if (!forecast) return null
  
  const CONF_COLOR = {
    HIGH:   '#0D9488',
    MEDIUM: '#9A6700',
    LOW:    '#8C959F',
  }
  
  return (
    <div style={{
      background:   '#F6F8FA',
      border:       '1px solid #D0D7DE',
      borderRadius: 8,
      overflow:     'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding:        '14px 20px',
        borderBottom:   '1px solid #D0D7DE',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        background:     '#FFFFFF',
      }}>
        <div>
          <span style={{
            fontSize:   13,
            fontWeight: 700,
            color:      '#1F2328',
          }}>
            Price Forecast — {city}
          </span>
          <span style={{
            fontSize:   11,
            color:      '#8C959F',
            marginLeft: 10,
          }}>
            CAGR {forecast.cagr_pct}%/yr · implied from 2020→2025 actual data
          </span>
        </div>
        <span style={{
          fontSize:     10,
          fontWeight:   600,
          color:        '#0D9488',
          background:   '#0D948812',
          border:       '1px solid #0D948830',
          borderRadius: 4,
          padding:      '2px 8px',
        }}>
          {forecast.cagr_pct}% CAGR
        </span>
      </div>
      
      {/* Forecast table */}
      <div style={{ padding: '0 20px' }}>
        {forecast.forecast_points.map((point, i) => (
          <div
            key={point.horizon_label}
            style={{
              display:      'flex',
              alignItems:   'center',
              height:       44,
              borderBottom: i < forecast.forecast_points.length - 1
                ? '1px solid #EAEEF2'
                : 'none',
              gap:          16,
            }}
          >
            {/* Horizon label */}
            <div style={{
              width:      52,
              fontSize:   12,
              fontWeight: 700,
              color:      '#0D9488',
              fontFamily: 'monospace',
              flexShrink: 0,
            }}>
              {point.horizon_label}
            </div>
            
            {/* Progress bar showing growth */}
            <div style={{
              flex:         1,
              height:       6,
              background:   '#E2E8F0',
              borderRadius: 3,
              overflow:     'hidden',
            }}>
              <div style={{
                width:        `${Math.min(((point.projected_price - forecast.current_median) / forecast.current_median) * 100 * 3, 100)}%`,
                height:       '100%',
                background:   '#0D9488',
                borderRadius: 3,
                transition:   'width 0.8s ease',
                minWidth:     4,
              }} />
            </div>
            
            {/* Projected price */}
            <div style={{
              fontSize:   14,
              fontWeight: 700,
              color:      '#1F2328',
              minWidth:   120,
              textAlign:  'right',
              flexShrink: 0,
            }}>
              ₹{Math.round(point.projected_price).toLocaleString('en-IN')}
              <span style={{ fontSize: 10, color: '#8C959F', fontWeight: 400 }}>/sqft</span>
            </div>
            
            {/* Range */}
            <div style={{
              fontSize:   10,
              color:      '#8C959F',
              minWidth:   120,
              textAlign:  'right',
              flexShrink: 0,
            }}>
              ₹{Math.round(point.lower_bound/1000)}K — ₹{Math.round(point.upper_bound/1000)}K
            </div>
            
            {/* Confidence */}
            <div style={{
              fontSize:     10,
              fontWeight:   600,
              color:        CONF_COLOR[point.confidence] || '#8C959F',
              minWidth:     60,
              textAlign:    'right',
              flexShrink:   0,
            }}>
              {point.confidence}
            </div>
          </div>
        ))}
      </div>
      
      {/* Mini chart */}
      <div style={{
        padding:    '0 20px 16px',
        borderTop:  '1px solid #EAEEF2',
        marginTop:  8,
      }}>
        <ForecastChart
          forecastData={forecast.forecast_points}
          currentMedian={forecast.current_median}
          city={city}
        />
      </div>
      
      {/* Disclaimer */}
      <div style={{
        padding:    '8px 20px',
        background: '#F6F8FA',
        borderTop:  '1px solid #D0D7DE',
        fontSize:   10,
        color:      '#8C959F',
        lineHeight: 1.5,
      }}>
        Forecast based on implied CAGR from 600,000 observations (2020→2025).
        Confidence bands widen with horizon. Not financial advice.
      </div>
    </div>
  )
}

export default function ValuationResult({ data }) {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      style={{ maxWidth: 680 }}
    >
      
      {/* ── Primary price display ──────────────────────────── */}
      <motion.div variants={item}>
        <div style={{
          fontSize:      9,
          fontWeight:    600,
          color:         '#8C959F',
          textTransform: 'uppercase',
          letterSpacing: '2px',
          marginBottom:  12,
        }}>
          Valuation Report
        </div>
        
        {/* Large price */}
        <div style={{
          display:    'flex',
          alignItems: 'baseline',
          gap:        6,
          marginBottom: 10,
        }}>
          <span style={{
            fontSize:   22,
            fontWeight: 400,
            color:      '#8C959F',
            marginBottom: 12,
          }}>
            ₹
          </span>
          <AnimatedNumber
            value={data.predicted_price_sqft}
            duration={1000}
            decimals={0}
            style={{
              fontSize:   72,
              fontWeight: 800,
              color:      '#1F2328',
              lineHeight: 1,
              display:    'block',
            }}
          />
          <span style={{
            fontSize:   18,
            color:      '#8C959F',
            marginBottom: 12,
          }}>
            /sqft
          </span>
        </div>
        
        {/* Total value + rental */}
        <div style={{
          display:      'flex',
          gap:          32,
          marginBottom: 20,
          flexWrap:     'wrap',
        }}>
          <div>
            <span style={{ fontSize: 12, color: '#656D76' }}>
              Total Value{'  '}
            </span>
            <span style={{
              fontSize:   18,
              fontWeight: 700,
              color:      '#1F2328',
            }}>
              ₹{data.total_valuation_cr} Crores
            </span>
          </div>
          <div>
            <span style={{ fontSize: 12, color: '#656D76' }}>
              Est. Rental{'  '}
            </span>
            <span style={{
              fontSize:   15,
              fontWeight: 600,
              color:      '#656D76',
            }}>
              ₹{Math.round(data.rental_estimate).toLocaleString('en-IN')}/mo
            </span>
          </div>
        </div>
      </motion.div>
      
      {/* ── Trust badge ────────────────────────────────────── */}
      <motion.div variants={item}>
        <TrustBadge
          tier={data.trust_tier}
          score={data.confidence_score}
        />
      </motion.div>
      
      <Divider label="Why This Valuation" />
      
      {/* ── SHAP drivers ───────────────────────────────────── */}
      <motion.div variants={item}>
        {data.top_drivers.map((driver, i) => (
          <motion.div
            key={driver.feature}
            initial={{ opacity: 0, x: 14 }}
            animate={{ opacity: 1, x: 0  }}
            transition={{
              delay:    0.3 + i * 0.06,
              duration: 0.35,
              ease:     [0.22, 1, 0.36, 1],
            }}
            style={{
              display:      'flex',
              alignItems:   'center',
              height:       44,
              borderBottom: '1px solid #F6F8FA',
            }}
          >
            {/* Feature name */}
            <span style={{
              flex:       1,
              fontSize:   13,
              fontWeight: 500,
              color:      '#1F2328',
            }}>
              {driver.display_name}
            </span>
            
            {/* Contribution */}
            <div style={{
              display:    'flex',
              alignItems: 'center',
              gap:        4,
              fontSize:   13,
              fontWeight: 700,
              color:      driver.direction === 'UP'
                ? '#0D9488'
                : '#CF222E',
            }}>
              {driver.direction === 'UP'
                ? <ArrowUpRight   size={14} strokeWidth={2} />
                : <ArrowDownRight size={14} strokeWidth={2} />
              }
              {driver.direction === 'UP' ? '+' : ''}
              ₹{Math.abs(driver.contribution).toLocaleString('en-IN', {
                maximumFractionDigits: 0,
              })}
              <span style={{
                fontSize:   11,
                fontWeight: 400,
                color:      '#8C959F',
              }}>
                /sqft
              </span>
            </div>
          </motion.div>
        ))}
        
        {/* Base rate footer */}
        <div style={{
          display:        'flex',
          justifyContent: 'space-between',
          paddingTop:     10,
          borderTop:      '1px solid #EAEEF2',
          marginTop:      4,
        }}>
          <span style={{ fontSize: 11, color: '#8C959F' }}>
            Base market rate
          </span>
          <span style={{
            fontSize:   11,
            fontWeight: 600,
            color:      '#656D76',
          }}>
            ₹{Math.round(data.base_value).toLocaleString('en-IN')}/sqft
          </span>
        </div>
      </motion.div>
      
      <Divider label="Property Location" />
      
      {/* ── Map ───────────────────────────────────────────── */}
      <motion.div variants={item}>
        <PropertyMap city={data.city} locality={data.locality} />
      </motion.div>
      
      <Divider label={`${data.city} Market Context`} />
      
      {/* ── City context card ──────────────────────────────── */}
      <motion.div variants={item}>
        <div style={{
          background:   '#F6F8FA',
          border:       '1px solid #D0D7DE',
          borderRadius: 8,
          overflow:     'hidden',
        }}>
          {/* Three stat columns */}
          <div style={{
            display:             'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            padding:             20,
            gap:                 0,
          }}>
            {[
              {
                label: 'Current Median',
                value: `₹${Math.round(data.city_current_median).toLocaleString('en-IN')}/sqft`,
                color: '#1F2328',
              },
              {
                label: 'Growth Rate',
                value: `${data.city_cagr_pct}%`,
                color: '#0D9488',
              },
              {
                label:   'Drift Status',
                value:   data.city_drift_status,
                isBadge: true,
              },
            ].map((stat, i) => (
              <div
                key={stat.label}
                style={{
                  borderRight:  i < 2 ? '1px solid #D0D7DE' : 'none',
                  paddingRight: i < 2 ? 20 : 0,
                  paddingLeft:  i > 0 ? 20 : 0,
                }}
              >
                <div style={{
                  fontSize:      9,
                  fontWeight:    600,
                  color:         '#8C959F',
                  textTransform: 'uppercase',
                  letterSpacing: '1.5px',
                  marginBottom:  8,
                }}>
                  {stat.label}
                </div>
                {stat.isBadge ? (
                  <span style={{
                    fontSize:     11,
                    fontWeight:   700,
                    background:   '#9A670012',
                    border:       '1px solid #9A670040',
                    color:        '#9A6700',
                    borderRadius: 4,
                    padding:      '3px 10px',
                  }}>
                    {stat.value}
                  </span>
                ) : (
                  <div style={{
                    fontSize:   16,
                    fontWeight: 700,
                    color:      stat.color,
                  }}>
                    {stat.value}
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {/* Forecast strip */}
          <div style={{
            padding:    '12px 20px',
            borderTop:  '1px solid #D0D7DE',
            fontSize:   12,
            color:      '#656D76',
            lineHeight: 1.6,
          }}>
            <span style={{ fontWeight: 600, color: '#1F2328' }}>
              {data.city}
            </span>
            {' '}price forecast — implied CAGR{' '}
            <span style={{ fontWeight: 600, color: '#0D9488' }}>
              {data.city_cagr_pct}%/yr
            </span>
            {' '}from 2020→2025 actual data
          </div>
          
          {/* Drift alert strip */}
          <div style={{
            padding:    '10px 20px',
            background: '#9A670008',
            borderTop:  '1px solid #9A670025',
            display:    'flex',
            alignItems: 'center',
            gap:        8,
          }}>
            <AlertTriangle size={12} color="#9A6700" strokeWidth={2} />
            <span style={{ fontSize: 11, color: '#9A6700' }}>
              Macro variables drifted — cross-verify with recent comparable sales.
            </span>
          </div>
        </div>
      </motion.div>
      
      <Divider label={`${data.city} Price Forecast`} />
      
      {/* ── Forecast section ───────────────────────────────── */}
      <motion.div variants={item}>
        <ForecastSection city={data.city} />
      </motion.div>
      
      {/* ── Property summary chip row ──────────────────────── */}
      <motion.div
        variants={item}
        style={{
          display:   'flex',
          gap:       8,
          marginTop: 20,
          flexWrap:  'wrap',
        }}
      >
        {[
          `${data.city}`,
          `${data.locality}`,
          `${data.bhk} BHK`,
          `${data.total_sqft} sqft`,
          `${data.bath} bath`,
        ].map(chip => (
          <span
            key={chip}
            style={{
              fontSize:     11,
              fontWeight:   500,
              color:        '#656D76',
              background:   '#F6F8FA',
              border:       '1px solid #D0D7DE',
              borderRadius: 100,
              padding:      '4px 12px',
            }}
          >
            {chip}
          </span>
        ))}
      </motion.div>
     </motion.div>
  )
}

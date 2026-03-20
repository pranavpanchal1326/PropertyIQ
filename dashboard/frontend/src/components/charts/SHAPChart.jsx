import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const GROUP_COLORS = {
  location: { bar: 'var(--teal)',  label: 'Location Features'  },
  macro:    { bar: 'var(--amber)', label: 'Macro Features'     },
  physical: { bar: 'var(--border-muted)', label: 'Physical Features' },
}

export default function SHAPChart({ data }) {
  const ref    = useRef(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -40px 0px' })
  
  if (!data?.features?.length) return null
  
  const maxVal   = data.features[0]?.mean_shap || 1
  const LABEL_W  = 180
  
  // Group separator positions
  let lastGroup = null
  
  return (
    <div
      ref={ref}
      style={{
        background:   'var(--bg-base)',
        border:       '1px solid var(--border-subtle)',
        borderRadius: 8,
        padding:      20,
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: 4 }}>
        <span style={{
          fontSize:   13,
          fontWeight: 700,
          color:      'var(--text-primary)',
        }}>
          SHAP Global Feature Importance
        </span>
      </div>
      <div style={{
        fontSize:     11,
        color:        'var(--text-secondary)',
        marginBottom: 16,
      }}>
        Mean |SHAP| across 200 validation samples · base value ₹{Math.round(data.base_value).toLocaleString('en-IN')}/sqft
      </div>
      
      {/* Location dominance callout */}
      <div style={{
        display:      'flex',
        alignItems:   'center',
        gap:          10,
        background:   'var(--teal-glow)',
        border:       '1px solid var(--teal-border)',
        borderRadius: 6,
        padding:      '8px 12px',
        marginBottom: 20,
      }}>
        <span style={{
          fontSize:   11,
          fontWeight: 600,
          color:      'var(--teal)',
        }}>
          Location dominates by {data.location_dominance_ratio?.toFixed(0)}×
        </span>
        <span style={{
          fontSize: 11,
          color:    'var(--text-secondary)',
        }}>
          Where the property sits matters more than its size
        </span>
      </div>
      
      {/* Bars */}
      <div style={{ position: 'relative' }}>
        {data.features.map((item, i) => {
          const pct        = (item.mean_shap / maxVal) * 100
          const colors     = GROUP_COLORS[item.feature_group] || GROUP_COLORS.physical
          const showDivider = lastGroup !== null && lastGroup !== item.feature_group
          lastGroup = item.feature_group
          
          return (
            <div key={item.feature}>
              {/* Group divider */}
              {showDivider && (
                <div style={{
                  display:     'flex',
                  alignItems:  'center',
                  gap:         8,
                  margin:      '12px 0 10px',
                }}>
                  <div style={{
                    flex:       1,
                    height:     1,
                    background: 'var(--border-subtle)',
                  }} />
                  <span style={{
                    fontSize:      9,
                    fontWeight:    600,
                    color:         'var(--text-ghost)',
                    textTransform: 'uppercase',
                    letterSpacing: '1.5px',
                    whiteSpace:    'nowrap',
                  }}>
                    {colors.label}
                  </span>
                  <div style={{
                    flex:       1,
                    height:     1,
                    background: 'var(--border-subtle)',
                  }} />
                </div>
              )}
              
              {/* Bar row */}
              <div style={{
                display:      'flex',
                alignItems:   'center',
                gap:          10,
                marginBottom: 9,
              }}>
                {/* Feature label */}
                <div style={{
                  width:        LABEL_W,
                  fontSize:     11,
                  color:        item.feature_group === 'physical'
                    ? 'var(--text-ghost)'
                    : 'var(--text-secondary)',
                  textAlign:    'right',
                  flexShrink:   0,
                  overflow:     'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace:   'nowrap',
                  fontWeight:   item.feature_group === 'location' ? 500 : 400,
                }}>
                  {item.display_name}
                </div>
                
                {/* Bar track */}
                <div style={{
                  flex:         1,
                  height:       20,
                  borderRadius: '0 4px 4px 0',
                  overflow:     'hidden',
                }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={inView ? { width: `${pct}%` } : { width: 0 }}
                    transition={{
                      duration: 0.55,
                      delay:    i * 0.04,
                      ease:     [0.34, 1.2, 0.64, 1],
                    }}
                    style={{
                      height:       '100%',
                      background:   colors.bar,
                      borderRadius: '0 4px 4px 0',
                      minWidth:     2,
                    }}
                  />
                </div>
                
                {/* Value */}
                <div style={{
                  width:      60,
                  fontSize:   11,
                  fontWeight: item.feature_group === 'location' ? 700 : 400,
                  color:      item.feature_group === 'location'
                    ? 'var(--text-primary)'
                    : 'var(--text-ghost)',
                  flexShrink: 0,
                  fontFamily: 'monospace',
                  textAlign:  'right',
                }}>
                  {item.mean_shap.toFixed(1)}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

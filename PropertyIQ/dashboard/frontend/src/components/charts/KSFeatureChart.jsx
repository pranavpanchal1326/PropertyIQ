import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const SEVERITY_COLORS = {
  HIGH:   { bar: 'var(--red)',   glow: 'var(--red-glow)'   },
  MEDIUM: { bar: 'var(--amber)', glow: 'var(--amber-glow)' },
  LOW:    { bar: 'var(--border-muted)', glow: 'transparent' },
  NONE:   { bar: 'var(--border-muted)', glow: 'transparent' },
}

export default function KSFeatureChart({ data }) {
  const ref    = useRef(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -40px 0px' })
  
  if (!data?.length) return null
  
  const THRESHOLD = 0.30
  const MAX       = 1.0
  const LABEL_W   = 170
  
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
      <div style={{
        display:        'flex',
        justifyContent: 'space-between',
        alignItems:     'flex-start',
        marginBottom:   4,
      }}>
        <span style={{
          fontSize:   13,
          fontWeight: 700,
          color:      'var(--text-primary)',
        }}>
          KS Statistic by Feature
        </span>
        <span style={{
          fontSize:    10,
          color:       'var(--text-ghost)',
          fontFamily:  'monospace',
        }}>
          ks_results.json
        </span>
      </div>
      <div style={{
        fontSize:     11,
        color:        'var(--text-secondary)',
        marginBottom: 20,
      }}>
        Sorted by drift severity — threshold 0.30
      </div>
      
      {/* Chart area */}
      <div style={{ position: 'relative' }}>
        {data.map((item, i) => {
          const pct    = (item.ks_stat / MAX) * 100
          const colors = SEVERITY_COLORS[item.severity] || SEVERITY_COLORS.NONE
          
          return (
            <div
              key={item.feature}
              style={{
                display:       'flex',
                alignItems:    'center',
                gap:           10,
                marginBottom:  10,
                position:      'relative',
              }}
            >
              {/* Feature label */}
              <div style={{
                width:        LABEL_W,
                fontSize:     11,
                color:        item.drifted
                  ? 'var(--text-secondary)'
                  : 'var(--text-ghost)',
                textAlign:    'right',
                flexShrink:   0,
                overflow:     'hidden',
                textOverflow: 'ellipsis',
                whiteSpace:   'nowrap',
                fontWeight:   item.drifted ? 500 : 400,
              }}>
                {item.display_name}
              </div>
              
              {/* Bar track */}
              <div style={{
                flex:         1,
                height:       22,
                position:     'relative',
                background:   item.drifted ? colors.glow : 'transparent',
                borderRadius: '0 4px 4px 0',
                overflow:     'hidden',
              }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={inView ? { width: `${pct}%` } : { width: 0 }}
                  transition={{
                    duration: 0.55,
                    delay:    i * 0.045,
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
              
              {/* Value label */}
              <div style={{
                width:      52,
                fontSize:   11,
                fontWeight: item.drifted ? 700 : 400,
                color:      item.drifted
                  ? 'var(--text-primary)'
                  : 'var(--text-ghost)',
                flexShrink: 0,
                fontFamily: 'monospace',
              }}>
                {item.ks_stat.toFixed(4)}
              </div>
            </div>
          )
        })}
        
        {/* Threshold line — positioned at 30% of chart width */}
        <ThresholdLine
          threshold={THRESHOLD}
          max={MAX}
          labelWidth={LABEL_W}
          inView={inView}
        />
      </div>
    </div>
  )
}

function ThresholdLine({ threshold, max, labelWidth, inView }) {
  const pct = (threshold / max) * 100
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={inView ? { opacity: 1 } : { opacity: 0 }}
      transition={{ delay: 0.6, duration: 0.3 }}
      style={{
        position:      'absolute',
        top:           0,
        bottom:        0,
        pointerEvents: 'none',
        // offset by label width + gap
        left:          `calc(${labelWidth}px + 10px + ${pct}% * (100% - ${labelWidth}px - 72px) / 100)`,
      }}
    >
      {/* Dashed line */}
      <div style={{
        width:       1,
        height:      '100%',
        borderLeft:  '1px dashed var(--amber)',
        position:    'relative',
      }}>
        {/* Floating label */}
        <div style={{
          position:     'absolute',
          top:          -2,
          left:         '50%',
          transform:    'translateX(-50%)',
          background:   'var(--amber-glow)',
          border:       '1px solid var(--amber-border)',
          borderRadius: 4,
          padding:      '2px 7px',
          fontSize:     9,
          fontWeight:   600,
          color:        'var(--amber)',
          whiteSpace:   'nowrap',
        }}>
          0.30
        </div>
      </div>
    </motion.div>
  )
}

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import AnimatedNumber from '../../components/ui/AnimatedNumber'

const STATS = [
  { value: 1.61,    suffix: '%',  label: 'Sale Model MAPE',     sub: 'Val MAPE vs 15% target', color: '#2DD4BF', decimals: 2 },
  { value: 0.9968,  suffix: '',   label: 'OOB R²',              sub: 'Out-of-bag validation',  color: '#E6EDF3', decimals: 4 },
  { value: 600000,  suffix: '',   label: 'Training Records',    sub: '2020 + 2025 combined',   color: '#2DD4BF', decimals: 0 },
  { value: 10,      suffix: '',   label: 'Indian Cities',       sub: 'Mumbai to Kolkata',      color: '#E6EDF3', decimals: 0 },
  { value: 2,       suffix: '/11',label: 'Features Drifted',    sub: 'KS-test confirmed',      color: '#FF7B72', decimals: 0 },
  { value: 5,       suffix: ' yr',label: 'Temporal Gap',        sub: '2020 training → 2025 drift', color: '#E3B341', decimals: 0 },
]

export default function RealNumbers() {
  const ref    = useRef(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -80px 0px' })
  
  return (
    <section
      ref={ref}
      style={{
        padding:   '120px 80px',
        background: '#06090F',
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
        style={{ textAlign: 'center', marginBottom: 64 }}
      >
        <div style={{
          fontSize:      10,
          fontWeight:    600,
          color:         '#2DD4BF',
          textTransform: 'uppercase',
          letterSpacing: '2px',
          marginBottom:  16,
        }}>
          Real Data. Real Results.
        </div>
        <h2 style={{
          fontSize:     48,
          fontWeight:   800,
          letterSpacing:'-1px',
          color:        '#E6EDF3',
        }}>
          Not a demo. Not simulated.
        </h2>
        <p style={{
          fontSize:   18,
          color:      '#7D8590',
          marginTop:  12,
        }}>
          600,000 actual Indian property records · verified outputs
        </p>
      </motion.div>
      
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap:                 16,
        maxWidth:            1100,
        margin:              '0 auto',
      }}>
        {STATS.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: i * 0.07 }}
            style={{
              background:   '#0D1117',
              border:       '1px solid #21262D',
              borderRadius: 8,
              padding:      '28px 32px',
            }}
          >
            <div style={{ marginBottom: 6 }}>
              <AnimatedNumber
                value={s.value}
                decimals={s.decimals}
                suffix={s.suffix}
                style={{
                  fontSize:   48,
                  fontWeight: 800,
                  color:      s.color,
                  lineHeight: 1,
                }}
              />
            </div>
            <div style={{
              fontSize:     14,
              fontWeight:   600,
              color:        '#E6EDF3',
              marginBottom: 4,
            }}>
              {s.label}
            </div>
            <div style={{ fontSize: 12, color: '#484F58' }}>
              {s.sub}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}

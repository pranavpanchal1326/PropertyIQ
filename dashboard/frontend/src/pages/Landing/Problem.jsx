import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const PROBLEMS = [
  {
    number: '5 years',
    label:  'since training data was collected',
    body:   'Indian banks approve home loans using ML models trained on 2020 data. Post-COVID prices surged 30–67% across 10 cities. The model never knew.',
    color:  '#FF7B72',
  },
  {
    number: '+54%',
    label:  'average price appreciation 2020→2025',
    body:   'The model produces stale undervalued estimates. No alert fires. No analyst notices. The degradation is completely silent.',
    color:  '#E3B341',
  },
  {
    number: 'ZERO',
    label:  'existing tools detect this drift',
    body:   'No standardised KS-test framework exists for Indian property markets. No tool translates p-values into credit officer guidance.',
    color:  '#FF7B72',
  },
]

export default function Problem() {
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
          The Problem
        </div>
        <h2 style={{
          fontSize:     48,
          fontWeight:   800,
          lineHeight:   1.15,
          letterSpacing:'-1px',
          color:        '#E6EDF3',
          maxWidth:     700,
          margin:       '0 auto',
        }}>
          Banks are approving loans on models that haven't seen 2025 prices.
        </h2>
      </motion.div>
      
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap:                 16,
        maxWidth:            1100,
        margin:              '0 auto',
      }}>
        {PROBLEMS.map((p, i) => (
          <motion.div
            key={p.number}
            initial={{ opacity: 0, y: 24 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            style={{
              background:   '#0D1117',
              border:       '1px solid #21262D',
              borderRadius: 10,
              padding:      32,
              borderTop:    `2px solid ${p.color}`,
            }}
          >
            <div style={{
              fontSize:     48,
              fontWeight:   800,
              color:        p.color,
              lineHeight:   1,
              marginBottom: 8,
            }}>
              {p.number}
            </div>
            <div style={{
              fontSize:     14,
              color:        '#7D8590',
              marginBottom: 20,
            }}>
              {p.label}
            </div>
            <div style={{
              fontSize:   14,
              color:      '#7D8590',
              lineHeight: 1.7,
            }}>
              {p.body}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}

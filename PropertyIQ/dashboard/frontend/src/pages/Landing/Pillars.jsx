import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const PILLARS = [
  {
    num:    '01',
    title:  'KS-Test Drift Detection',
    stat:   '0.5566',
    statLabel: 'Max KS Statistic detected',
    body:   'Automatically tests 11 features and 10 cities against the training distribution. p < 0.05 triggers a drift alert. No manual monitoring required.',
    color:  '#FF7B72',
  },
  {
    num:    '02',
    title:  'Ensemble Confidence Scoring',
    stat:   '82 / 100',
    statLabel: 'Confidence score per property',
    body:   '300 decision trees vote on every prediction. The variance between trees becomes your confidence score. No calibration needed.',
    color:  '#2DD4BF',
  },
  {
    num:    '03',
    title:  'Trust Translation Layer',
    stat:   'TRUSTED',
    statLabel: 'Plain English for credit officers',
    body:   'Converts KS p-values + MAPE alerts + ensemble variance into three tiers. A credit officer with no ML training reads it in 2 seconds.',
    color:  '#3FB950',
  },
]

export default function Pillars() {
  const ref    = useRef(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -80px 0px' })
  
  return (
    <section
      ref={ref}
      style={{
        padding:   '120px 80px',
        background: '#0D1117',
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
        style={{ marginBottom: 64, maxWidth: 1100, margin: '0 auto 64px' }}
      >
        <div style={{
          fontSize:      10,
          fontWeight:    600,
          color:         '#2DD4BF',
          textTransform: 'uppercase',
          letterSpacing: '2px',
          marginBottom:  16,
        }}>
          How PropertyIQ Works
        </div>
        <h2 style={{
          fontSize:     48,
          fontWeight:   800,
          lineHeight:   1.15,
          letterSpacing:'-1px',
          color:        '#E6EDF3',
          maxWidth:     700,
        }}>
          Three layers of protection between your model and a bad loan.
        </h2>
      </motion.div>
      
      <div style={{
        display:   'flex',
        flexDirection: 'column',
        gap:       16,
        maxWidth:  1100,
        margin:    '0 auto',
      }}>
        {PILLARS.map((p, i) => (
          <motion.div
            key={p.num}
            initial={{ opacity: 0, x: -24 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            style={{
              background:   '#06090F',
              border:       '1px solid #21262D',
              borderRadius: 10,
              padding:      '32px 40px',
              display:      'flex',
              alignItems:   'center',
              gap:          48,
            }}
          >
            {/* Left stat */}
            <div style={{ minWidth: 200, flexShrink: 0 }}>
              <div style={{
                fontSize:     i === 1 ? 40 : 48,
                fontWeight:   800,
                color:        p.color,
                lineHeight:   1,
                marginBottom: 8,
              }}>
                {p.stat}
              </div>
              <div style={{ fontSize: 12, color: '#7D8590' }}>
                {p.statLabel}
              </div>
            </div>
            
            {/* Divider */}
            <div style={{
              width:      1,
              height:     72,
              background: '#21262D',
              flexShrink: 0,
            }} />
            
            {/* Right content */}
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                <span style={{
                  fontSize:     11,
                  fontWeight:   700,
                  color:        '#484F58',
                  background:   '#161B22',
                  border:       '1px solid #21262D',
                  borderRadius: 4,
                  padding:      '3px 8px',
                  fontFamily:   'monospace',
                }}>
                  {p.num}
                </span>
                <h3 style={{
                  fontSize:   20,
                  fontWeight: 700,
                  color:      '#E6EDF3',
                }}>
                  {p.title}
                </h3>
              </div>
              <p style={{
                fontSize:   14,
                color:      '#7D8590',
                lineHeight: 1.7,
                maxWidth:   600,
              }}>
                {p.body}
              </p>
            </div>
            
            {/* Number right */}
            <div style={{
              width:          40,
              height:         40,
              borderRadius:   '50%',
              background:     '#161B22',
              border:         '1px solid #21262D',
              display:        'flex',
              alignItems:     'center',
              justifyContent: 'center',
              fontSize:       13,
              fontWeight:     700,
              color:          '#484F58',
              flexShrink:     0,
            }}>
              {p.num}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}

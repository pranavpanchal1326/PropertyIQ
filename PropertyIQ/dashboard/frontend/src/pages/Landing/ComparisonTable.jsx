import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Check, X, Minus } from 'lucide-react'

const ROWS = [
  { capability: 'KS-test drift detection',          piq: true,  manual: false,  avm: false   },
  { capability: 'Ensemble confidence score',         piq: true,  manual: false,  avm: false   },
  { capability: 'City-level granularity (10 cities)',piq: true,  manual: 'partial', avm: 'partial' },
  { capability: 'Trust tier for credit officers',    piq: true,  manual: false,  avm: false   },
  { capability: 'RBI MRM circular alignment',        piq: true,  manual: false,  avm: false   },
  { capability: 'Indian market calibration',         piq: true,  manual: 'partial', avm: false },
  { capability: 'Time to valuation',                 piq: '< 2 sec', manual: '3–5 days', avm: 'Minutes' },
  { capability: 'MAPE on Indian data',               piq: '1.61%',  manual: 'N/A',    avm: '~8–12%' },
]

function CellValue({ value, isPiq }) {
  if (value === true) return (
    <div style={{
      width:          28,
      height:         28,
      borderRadius:   '50%',
      background:     isPiq ? '#3FB95015' : '#3FB95015',
      display:        'flex',
      alignItems:     'center',
      justifyContent: 'center',
    }}>
      <Check size={14} color="#3FB950" strokeWidth={2.5} />
    </div>
  )
  if (value === false) return (
    <div style={{
      width:          28,
      height:         28,
      borderRadius:   '50%',
      background:     '#FF7B7212',
      display:        'flex',
      alignItems:     'center',
      justifyContent: 'center',
    }}>
      <X size={14} color="#FF7B72" strokeWidth={2.5} />
    </div>
  )
  if (value === 'partial') return (
    <div style={{
      width:          28,
      height:         28,
      borderRadius:   '50%',
      background:     '#E3B34112',
      display:        'flex',
      alignItems:     'center',
      justifyContent: 'center',
    }}>
      <Minus size={14} color="#E3B341" strokeWidth={2.5} />
    </div>
  )
  return (
    <span style={{
      fontSize:   13,
      fontWeight: 600,
      color:      isPiq ? '#2DD4BF' : '#7D8590',
    }}>
      {value}
    </span>
  )
}

export default function ComparisonTable() {
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
          Why PropertyIQ
        </div>
        <h2 style={{
          fontSize:     48,
          fontWeight:   800,
          letterSpacing:'-1px',
          color:        '#E6EDF3',
        }}>
          The only platform built specifically for Indian bank model risk.
        </h2>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.1 }}
        style={{
          maxWidth:     1100,
          margin:       '0 auto',
          background:   '#06090F',
          border:       '1px solid #21262D',
          borderRadius: 10,
          overflow:     'hidden',
        }}
      >
        {/* Column headers */}
        <div style={{
          display:             'grid',
          gridTemplateColumns: '1fr 200px 200px 200px',
          background:          '#0D1117',
          borderBottom:        '1px solid #21262D',
          padding:             '16px 32px',
          gap:                 16,
        }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#484F58', textTransform: 'uppercase', letterSpacing: '1.5px' }}>
            Capability
          </div>
          {[
            { name: 'PropertyIQ', highlight: true },
            { name: 'Manual Appraisal', highlight: false },
            { name: 'Generic AVM', highlight: false },
          ].map(col => (
            <div
              key={col.name}
              style={{
                fontSize:     13,
                fontWeight:   700,
                color:        col.highlight ? '#2DD4BF' : '#7D8590',
                textAlign:    'center',
                paddingBottom: col.highlight ? 12 : 0,
                borderBottom: col.highlight ? '2px solid #2DD4BF' : 'none',
              }}
            >
              {col.name}
            </div>
          ))}
        </div>
        
        {/* Rows */}
        {ROWS.map((row, i) => (
          <motion.div
            key={row.capability}
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.15 + i * 0.05 }}
            style={{
              display:             'grid',
              gridTemplateColumns: '1fr 200px 200px 200px',
              padding:             '0 32px',
              height:              52,
              alignItems:          'center',
              borderBottom:        i < ROWS.length - 1 ? '1px solid #21262D' : 'none',
              gap:                 16,
              background:          i % 2 === 0 ? '#06090F' : '#080C14',
            }}
          >
            <div style={{ fontSize: 14, color: '#E6EDF3' }}>
              {row.capability}
            </div>
            {/* PropertyIQ column — subtle tint */}
            <div style={{
              display:        'flex',
              justifyContent: 'center',
              background:     '#2DD4BF06',
              margin:         '-16px 0',
              padding:        '16px 0',
            }}>
              <CellValue value={row.piq} isPiq />
            </div>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <CellValue value={row.manual} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <CellValue value={row.avm} />
            </div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  )
}

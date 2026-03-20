import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { ShieldCheck } from 'lucide-react'

export default function RBICallout() {
  const ref    = useRef(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -80px 0px' })
  
  return (
    <section
      ref={ref}
      style={{
        padding:    '80px',
        background: '#06090F',
        borderTop:  '1px solid #21262D',
        borderBottom:'1px solid #21262D',
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
        style={{
          maxWidth:       900,
          margin:         '0 auto',
          background:     '#0D1117',
          border:         '1px solid #2DD4BF35',
          borderRadius:   12,
          padding:        '48px 64px',
          textAlign:      'center',
        }}
      >
        {/* Shield icon */}
        <div style={{
          width:          56,
          height:         56,
          borderRadius:   '50%',
          background:     '#2DD4BF15',
          border:         '1px solid #2DD4BF35',
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          margin:         '0 auto 24px',
        }}>
          <ShieldCheck size={26} color="#2DD4BF" strokeWidth={1.8} />
        </div>
        
        <h2 style={{
          fontSize:     32,
          fontWeight:   700,
          color:        '#E6EDF3',
          lineHeight:   1.3,
          maxWidth:     600,
          margin:       '0 auto 16px',
        }}>
          Built in alignment with RBI Model Risk Management Circular, 2023.
        </h2>
        
        <p style={{
          fontSize:   16,
          color:      '#7D8590',
          lineHeight: 1.7,
          maxWidth:   640,
          margin:     '0 auto 28px',
        }}>
          PropertyIQ's Trust Translation Layer directly addresses the circular's
          requirement for model output interpretability for non-technical stakeholders.
          Drift detection maps to ongoing model monitoring requirements.
        </p>
        
        {/* Badge */}
        <div style={{
          display:      'inline-flex',
          alignItems:   'center',
          gap:          8,
          background:   '#2DD4BF10',
          border:       '1px solid #2DD4BF30',
          borderRadius: 100,
          padding:      '8px 20px',
          fontSize:     12,
          fontWeight:   600,
          color:        '#2DD4BF',
          letterSpacing:'1px',
          textTransform:'uppercase',
        }}>
          RBI MRM · 2023 · Aligned
        </div>
      </motion.div>
    </section>
  )
}

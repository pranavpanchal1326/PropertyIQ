import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

export default function FinalCTA() {
  const ref      = useRef(null)
  const inView   = useInView(ref, { once: true, margin: '0px 0px -80px 0px' })
  const navigate = useNavigate()
  
  return (
    <section
      ref={ref}
      style={{
        padding:   '120px 80px',
        background: '#06090F',
        textAlign: 'center',
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 style={{
          fontSize:     64,
          fontWeight:   800,
          letterSpacing:'-1.5px',
          color:        '#E6EDF3',
          marginBottom: 16,
        }}>
          PropertyIQ is ready.
        </h2>
        
        <p style={{
          fontSize:     20,
          color:        '#7D8590',
          marginBottom: 48,
          lineHeight:   1.6,
        }}>
          Backend API live · 14 endpoints · Swagger documented
          <br />
          Trained on 600,000 records · MAPE 1.61%
        </p>
        
        <div style={{
          display:        'flex',
          gap:            14,
          justifyContent: 'center',
          alignItems:     'center',
        }}>
          <motion.button
            onClick={() => navigate('/client')}
            whileHover={{ scale: 1.02 }}
            whileTap={{  scale: 0.97 }}
            style={{
              height:       52,
              padding:      '0 32px',
              background:   '#2DD4BF',
              border:       'none',
              borderRadius: 8,
              fontSize:     15,
              fontWeight:   700,
              color:        '#06090F',
              cursor:       'pointer',
              fontFamily:   'inherit',
            }}
          >
            Try Live Demo →
          </motion.button>
          
          <motion.a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ scale: 1.02 }}
            style={{
              height:       52,
              padding:      '0 28px',
              background:   '#0D1117',
              border:       '1px solid #21262D',
              borderRadius: 8,
              fontSize:     14,
              fontWeight:   600,
              color:        '#2DD4BF',
              cursor:       'pointer',
              display:      'flex',
              alignItems:   'center',
              textDecoration:'none',
              fontFamily:   'monospace',
            }}
          >
            localhost:8000/docs
          </motion.a>
        </div>
      </motion.div>
    </section>
  )
}

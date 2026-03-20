import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, ExternalLink } from 'lucide-react'

// ── Sticky nav ─────────────────────────────────────────────────────────────
function Nav() {
  const navigate = useNavigate()
  
  return (
    <nav style={{
      position:       'fixed',
      top:            0,
      left:           0,
      right:          0,
      zIndex:         100,
      height:         72,
      background:     'rgba(6,9,15,0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom:   '1px solid #21262D',
      display:        'flex',
      alignItems:     'center',
      justifyContent: 'space-between',
      padding:        '0 80px',
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ position: 'relative', width: 24, height: 24 }}>
          <div style={{
            width: 15, height: 15, background: '#2DD4BF',
            borderRadius: 3, position: 'absolute', top: 0, left: 0,
          }} />
          <div style={{
            width: 15, height: 15, background: '#2DD4BF',
            borderRadius: 3, position: 'absolute', bottom: 0, right: 0,
            opacity: 0.45,
          }} />
        </div>
        <span style={{ fontSize: 16, fontWeight: 700, color: '#E6EDF3' }}>
          PropertyIQ
        </span>
      </div>
      
      {/* Nav links */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 40 }}>
        {['Product', 'Data', 'Methodology', 'API Docs'].map(link => (
          <span
            key={link}
            style={{
              fontSize:   14,
              fontWeight: 500,
              color:      '#7D8590',
              cursor:     'pointer',
              transition: 'color 0.15s',
            }}
            onMouseEnter={e => e.target.style.color = '#E6EDF3'}
            onMouseLeave={e => e.target.style.color = '#7D8590'}
          >
            {link}
          </span>
        ))}
      </div>
      
      {/* Right CTAs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <motion.button
          onClick={() => navigate('/admin/drift')}
          whileHover={{ scale: 1.02 }}
          whileTap={{  scale: 0.97 }}
          style={{
            background:   'transparent',
            border:       '1px solid #21262D',
            borderRadius: 6,
            padding:      '8px 18px',
            fontSize:     14,
            fontWeight:   500,
            color:        '#E6EDF3',
            cursor:       'pointer',
            fontFamily:   'inherit',
          }}
        >
          Admin Console
        </motion.button>
        <motion.button
          onClick={() => navigate('/client')}
          whileHover={{ scale: 1.02 }}
          whileTap={{  scale: 0.97 }}
          style={{
            background:   '#2DD4BF',
            border:       'none',
            borderRadius: 6,
            padding:      '8px 18px',
            fontSize:     14,
            fontWeight:   700,
            color:        '#06090F',
            cursor:       'pointer',
            fontFamily:   'inherit',
          }}
        >
          Try Demo →
        </motion.button>
      </div>
    </nav>
  )
}

// ── Hero section ───────────────────────────────────────────────────────────
export default function Hero() {
  const navigate = useNavigate()
  
  return (
    <>
      <Nav />
      <section style={{
        minHeight:      '100vh',
        display:        'flex',
        flexDirection:  'column',
        alignItems:     'center',
        justifyContent: 'center',
        padding:        '120px 80px 80px',
        position:       'relative',
        overflow:       'hidden',
        textAlign:      'center',
      }}>
        {/* Teal radial glow — subtle, not garish */}
        <div style={{
          position:   'absolute',
          top:        '-10%',
          left:       '50%',
          transform:  'translateX(-50%)',
          width:      800,
          height:     600,
          background: 'radial-gradient(ellipse at center, rgba(45,212,191,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        
        {/* Eyebrow pill */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0  }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          style={{
            display:      'inline-flex',
            alignItems:   'center',
            gap:          8,
            background:   '#2DD4BF15',
            border:       '1px solid #2DD4BF35',
            borderRadius: 100,
            padding:      '6px 16px',
            marginBottom: 28,
          }}
        >
          <div style={{
            width:        6,
            height:       6,
            borderRadius: '50%',
            background:   '#2DD4BF',
          }} />
          <span style={{
            fontSize:   12,
            fontWeight: 600,
            color:      '#2DD4BF',
          }}>
            Built for RBI Model Risk Management Compliance · 2023 Circular
          </span>
        </motion.div>
        
        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0  }}
          transition={{ duration: 0.55, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
          style={{
            fontSize:     64,
            fontWeight:   800,
            lineHeight:   1.1,
            letterSpacing:'-1.5px',
            marginBottom: 20,
            maxWidth:     820,
            color:        '#E6EDF3',
          }}
        >
          Know when your property model{' '}
          <span style={{ color: '#2DD4BF' }}>
            is lying to you.
          </span>
        </motion.h1>
        
        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0  }}
          transition={{ duration: 0.5, delay: 0.16, ease: [0.22, 1, 0.36, 1] }}
          style={{
            fontSize:     20,
            fontWeight:   400,
            color:        '#7D8590',
            lineHeight:   1.6,
            maxWidth:     580,
            marginBottom: 40,
          }}
        >
          PropertyIQ detects ML model drift in Indian real estate before the
          loan goes bad. Built for credit risk teams at Indian banks.
        </motion.p>
        
        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0  }}
          transition={{ duration: 0.5, delay: 0.24, ease: [0.22, 1, 0.36, 1] }}
          style={{ display: 'flex', gap: 14, marginBottom: 56 }}
        >
          <motion.button
            onClick={() => navigate('/client')}
            whileHover={{ scale: 1.02, background: '#25B8A0' }}
            whileTap={{  scale: 0.97 }}
            style={{
              height:       52,
              padding:      '0 28px',
              background:   '#2DD4BF',
              border:       'none',
              borderRadius: 8,
              fontSize:     15,
              fontWeight:   700,
              color:        '#06090F',
              cursor:       'pointer',
              display:      'flex',
              alignItems:   'center',
              gap:          8,
              fontFamily:   'inherit',
            }}
          >
            Try Live Demo
            <ArrowRight size={16} strokeWidth={2.5} />
          </motion.button>
          
          <motion.button
            onClick={() => navigate('/admin/drift')}
            whileHover={{ borderColor: '#30363D', background: '#161B22' }}
            whileTap={{  scale: 0.97 }}
            style={{
              height:       52,
              padding:      '0 28px',
              background:   'transparent',
              border:       '1px solid #21262D',
              borderRadius: 8,
              fontSize:     15,
              fontWeight:   500,
              color:        '#E6EDF3',
              cursor:       'pointer',
              display:      'flex',
              alignItems:   'center',
              gap:          8,
              fontFamily:   'inherit',
              transition:   'all 0.15s',
            }}
          >
            Admin Console
            <ExternalLink size={14} strokeWidth={1.8} />
          </motion.button>
        </motion.div>
        
        {/* Social proof strip */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          style={{
            display:    'flex',
            alignItems: 'center',
            gap:        8,
            fontSize:   13,
            color:      '#484F58',
            marginBottom: 72,
          }}
        >
          <span>Trained on</span>
          <span style={{ fontWeight: 700, color: '#E6EDF3' }}>600,000</span>
          <span>Indian property observations across</span>
          <span style={{ fontWeight: 700, color: '#E6EDF3' }}>10 cities</span>
          <span>·</span>
          <span style={{ fontWeight: 700, color: '#E6EDF3' }}>2020–2025</span>
        </motion.div>
        
        {/* Product screenshot frame */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0  }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          style={{
            width:        '100%',
            maxWidth:     1100,
            borderRadius: 12,
            overflow:     'hidden',
            border:       '1px solid #21262D',
            background:   '#0D1117',
            boxShadow:    '0 0 80px rgba(45,212,191,0.08)',
          }}
        >
          {/* Fake browser chrome */}
          <div style={{
            height:       40,
            background:   '#161B22',
            borderBottom: '1px solid #21262D',
            display:      'flex',
            alignItems:   'center',
            padding:      '0 16px',
            gap:          8,
          }}>
            {['#FF5F57','#FFBD2E','#28C840'].map(c => (
              <div key={c} style={{
                width:        12,
                height:       12,
                borderRadius: '50%',
                background:   c,
                opacity:      0.6,
              }} />
            ))}
            <div style={{
              flex:         1,
              display:      'flex',
              justifyContent: 'center',
            }}>
              <div style={{
                background:   '#0D1117',
                border:       '1px solid #21262D',
                borderRadius: 6,
                padding:      '4px 16px',
                fontSize:     12,
                color:        '#484F58',
                fontFamily:   'monospace',
              }}>
                localhost:5173/admin/drift
              </div>
            </div>
          </div>
          
          {/* Dashboard preview — text representation */}
          <div style={{
            display: 'flex',
            height:  420,
          }}>
            {/* Sidebar preview */}
            <div style={{
              width:        200,
              background:   '#0D1117',
              borderRight:  '1px solid #21262D',
              padding:      16,
              flexShrink:   0,
            }}>
              <div style={{
                display:      'flex',
                alignItems:   'center',
                gap:          8,
                marginBottom: 24,
                paddingBottom: 16,
                borderBottom: '1px solid #21262D',
              }}>
                <div style={{ position: 'relative', width: 20, height: 20 }}>
                  <div style={{
                    width: 12, height: 12, background: '#2DD4BF',
                    borderRadius: 2, position: 'absolute', top: 0, left: 0,
                  }} />
                  <div style={{
                    width: 12, height: 12, background: '#2DD4BF',
                    borderRadius: 2, position: 'absolute', bottom: 0, right: 0,
                    opacity: 0.4,
                  }} />
                </div>
                <span style={{ fontSize: 13, fontWeight: 700, color: '#E6EDF3' }}>PropertyIQ</span>
              </div>
              {['Drift Monitor','Model Health','City Analytics','Alert Log'].map((item, i) => (
                <div key={item} style={{
                  height:       32,
                  borderRadius: 5,
                  padding:      '0 10px',
                  display:      'flex',
                  alignItems:   'center',
                  marginBottom: 2,
                  background:   i === 0 ? '#161B22' : 'transparent',
                  boxShadow:    i === 0 ? 'inset 2px 0 0 #2DD4BF' : 'none',
                  fontSize:     12,
                  fontWeight:   i === 0 ? 600 : 400,
                  color:        i === 0 ? '#E6EDF3' : '#7D8590',
                }}>
                  {item}
                </div>
              ))}
            </div>
            
            {/* Main content preview */}
            <div style={{ flex: 1, padding: 20, background: '#06090F' }}>
              {/* KPI cards row */}
              <div style={{
                display:             'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap:                 12,
                marginBottom:        16,
              }}>
                {[
                  { label: 'DRIFT SEVERITY', value: 'HIGH',   color: '#FF7B72' },
                  { label: 'CITIES AFFECTED',value: '10 / 10',color: '#E3B341' },
                  { label: 'MAX KS STAT',    value: '0.5566', color: '#FF7B72' },
                  { label: 'WINDOWS HEALTHY',value: '98.0%',  color: '#3FB950' },
                ].map(card => (
                  <div key={card.label} style={{
                    background:   '#0D1117',
                    border:       '1px solid #21262D',
                    borderRadius: 6,
                    padding:      '12px 14px',
                  }}>
                    <div style={{
                      fontSize:      8,
                      color:         '#7D8590',
                      textTransform: 'uppercase',
                      letterSpacing: '1px',
                      marginBottom:  8,
                    }}>
                      {card.label}
                    </div>
                    <div style={{
                      fontSize:   20,
                      fontWeight: 800,
                      color:      card.color,
                    }}>
                      {card.value}
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Chart placeholders */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: 12,
                marginBottom: 12,
              }}>
                {['KS Statistic by Feature', 'Rolling MAPE — 600 Windows'].map(title => (
                  <div key={title} style={{
                    background:   '#0D1117',
                    border:       '1px solid #21262D',
                    borderRadius: 6,
                    padding:      '12px 14px',
                    height:       130,
                  }}>
                    <div style={{
                      fontSize:     11,
                      fontWeight:   600,
                      color:        '#E6EDF3',
                      marginBottom: 4,
                    }}>
                      {title}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 12 }}>
                      {[0.97, 0.87, 0.09, 0.02, 0.02].map((v, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <div style={{
                            width:        v * 120,
                            height:       8,
                            borderRadius: '0 3px 3px 0',
                            background:   v > 0.30 ? '#FF7B72' : '#30363D',
                          }} />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
        
        {/* Bottom fade */}
        <div style={{
          position:   'absolute',
          bottom:     0,
          left:       0,
          right:      0,
          height:     120,
          background: 'linear-gradient(to bottom, transparent, #06090F)',
          pointerEvents: 'none',
        }} />
      </section>
    </>
  )
}

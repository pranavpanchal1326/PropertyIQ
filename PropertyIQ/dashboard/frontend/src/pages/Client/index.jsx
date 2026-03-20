import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bell } from 'lucide-react'
import ValuationForm   from './ValuationForm'
import ValuationResult from './ValuationResult'
import { usePredict }  from '../../hooks/usePredict'
import api             from '../../api/client'

// ── Client Portal top bar — clean, no user name ────────────────────────────
function ClientTopBar() {
  return (
    <header style={{
      height:         60,
      flexShrink:     0,
      background:     '#FFFFFF',
      borderBottom:   '1px solid #D0D7DE',
      padding:        '0 32px',
      display:        'flex',
      alignItems:     'center',
      justifyContent: 'space-between',
      position:       'sticky',
      top:            0,
      zIndex:         40,
    }}>
      {/* Left — logo + portal label */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ position: 'relative', width: 20, height: 20 }}>
            <div style={{
              width: 13, height: 13,
              background: '#0D9488', borderRadius: 2,
              position: 'absolute', top: 0, left: 0,
            }} />
            <div style={{
              width: 13, height: 13,
              background: '#0D9488', borderRadius: 2,
              position: 'absolute', bottom: 0, right: 0,
              opacity: 0.45,
            }} />
          </div>
          <span style={{ fontSize: 15, fontWeight: 700, color: '#1F2328' }}>
            PropertyIQ
          </span>
        </div>
        <div style={{ width: 1, height: 18, background: '#D0D7DE' }} />
        <span style={{ fontSize: 13, color: '#656D76' }}>Client Portal</span>
      </div>
      
      {/* Right — minimal, no user name */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <Bell size={18} color="#656D76" strokeWidth={1.5} />
        <span style={{
          fontSize:     10,
          fontWeight:   600,
          color:        '#0D9488',
          background:   '#0D948812',
          border:       '1px solid #0D948830',
          borderRadius: 4,
          padding:      '4px 10px',
          textTransform:'uppercase',
          letterSpacing:'0.5px',
        }}>
          Live Model
        </span>
      </div>
    </header>
  )
}

// ── Empty state ────────────────────────────────────────────────────────────
function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{
        height:         '100%',
        display:        'flex',
        flexDirection:  'column',
        alignItems:     'center',
        justifyContent: 'center',
        padding:        '40px 32px',
        textAlign:      'center',
      }}
    >
      <div style={{
        fontSize:     80,
        fontWeight:   800,
        color:        '#F6F8FA',
        lineHeight:   1,
        marginBottom: 24,
        userSelect:   'none',
      }}>
        ₹
      </div>
      <div style={{
        fontSize:     16,
        fontWeight:   600,
        color:        '#656D76',
        marginBottom: 8,
      }}>
        Enter property details to get valuation
      </div>
      <div style={{
        fontSize:   13,
        color:      '#8C959F',
        lineHeight: 1.6,
        maxWidth:   360,
      }}>
        Powered by Random Forest · MAPE 1.61% · Trained on 600,000 Indian property records
      </div>
      <div style={{
        display:        'flex',
        gap:            8,
        marginTop:      24,
        flexWrap:       'wrap',
        justifyContent: 'center',
      }}>
        {['Live ML Prediction','Confidence Scoring','SHAP Explainability','Drift Detection','10 Indian Cities'].map(c => (
          <span key={c} style={{
            fontSize:     11,
            color:        '#0D9488',
            background:   '#0D948810',
            border:       '1px solid #0D948830',
            borderRadius: 100,
            padding:      '4px 12px',
            fontWeight:   500,
          }}>
            {c}
          </span>
        ))}
      </div>
    </motion.div>
  )
}

// ── Main ───────────────────────────────────────────────────────────────────
export default function ClientPortal() {
  const [localities,   setLocalities]   = useState([])
  const [currentCity,  setCurrentCity]  = useState('Mumbai')
  const { result, loading, error, predict } = usePredict()
  
  // Fetch localities whenever selected city changes
  const fetchLocalities = useCallback((city) => {
    api.get(`/api/model/localities/${encodeURIComponent(city)}`)
      .then(r => setLocalities(r.data.localities))
      .catch(() => setLocalities([]))
  }, [])
  
  useEffect(() => {
    fetchLocalities(currentCity)
  }, [currentCity, fetchLocalities])
  
  // Called by form when city changes
  const handleCityChange = useCallback((city) => {
    setCurrentCity(city)
  }, [])
  
  return (
    <div style={{
      minHeight:     '100vh',
      background:    '#FFFFFF',
      display:       'flex',
      flexDirection: 'column',
    }}>
      <ClientTopBar />
      
      <div style={{
        flex:     1,
        display:  'flex',
        overflow: 'hidden',
        height:   'calc(100vh - 60px)',
      }}>
        {/* Left panel */}
        <div style={{
          width:      420,
          flexShrink: 0,
          background: '#F6F8FA',
          borderRight:'1px solid #D0D7DE',
          overflowY:  'auto',
          padding:    '32px 28px',
        }}>
          <ValuationForm
            localities={localities}
            onSubmit={predict}
            loading={loading}
            onCityChange={handleCityChange}
          />
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                marginTop:    16,
                background:   '#CF222E10',
                border:       '1px solid #CF222E40',
                borderRadius: 8,
                padding:      '12px 16px',
                fontSize:     12,
                color:        '#CF222E',
                lineHeight:   1.5,
              }}
            >
              {error}
            </motion.div>
          )}
        </div>
        
        {/* Right panel */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 40 }}>
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0  }}
                exit={{   opacity: 0, y: -12 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              >
                <ValuationResult data={result} />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{   opacity: 0 }}
              >
                <EmptyState />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

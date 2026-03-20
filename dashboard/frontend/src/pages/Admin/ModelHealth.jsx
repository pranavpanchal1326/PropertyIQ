import { motion } from 'framer-motion'
import { Cpu } from 'lucide-react'
import { useModel }  from '../../hooks/useModel'
import ModelTable    from '../../components/tables/ModelTable'
import SHAPChart     from '../../components/charts/SHAPChart'
import Chi2Table     from '../../components/tables/Chi2Table'
import { getChi2 }  from '../../api/client'
import { useState, useEffect } from 'react'
import {
  SkeletonChart,
  SkeletonTable,
} from '../../components/ui/SkeletonCard'

const pageVariants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.08 } },
}

const sectionVariants = {
  hidden: { opacity: 0, y: 12 },
  show:   {
    opacity: 1, y: 0,
    transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
  },
}

export default function ModelHealth() {
  const { data, loading, error } = useModel()
  
  // Chi2 fetched separately since useModel doesn't include it
  const [chi2,     setChi2]     = useState(null)
  const [chi2Load, setChi2Load] = useState(true)
  
  useEffect(() => {
    getChi2()
      .then(r => setChi2(r.data))
      .catch(() => setChi2(null))
      .finally(() => setChi2Load(false))
  }, [])
  
  if (error) return (
    <div style={{
      padding:   32,
      color:     'var(--red)',
      fontSize:  14,
    }}>
      Failed to load model data: {error}
    </div>
  )
  
  return (
    <motion.div
      variants={pageVariants}
      initial="hidden"
      animate="show"
      style={{ display: 'flex', flexDirection: 'column', gap: 20 }}
    >
      
      {/* ── Model Registry ──────────────────────────────────── */}
      <motion.div variants={sectionVariants}>
        {loading
          ? <SkeletonTable />
          : <ModelTable data={data.registry} />
        }
      </motion.div>
      
      {/* ── SHAP + Chi2 row ─────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          display:             'grid',
          gridTemplateColumns: '1fr 420px',
          gap:                 20,
        }}
      >
        {/* SHAP chart */}
        {loading
          ? <SkeletonChart height={320} />
          : <SHAPChart data={data.shap} />
        }
        
        {/* Chi2 table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {chi2Load
            ? <SkeletonChart height={200} />
            : chi2 && <Chi2Table data={chi2} />
          }
          
          {/* Key insight card */}
          {!loading && data?.shap && (
            <div style={{
              background:   'var(--bg-base)',
              border:       '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding:      20,
            }}>
              <div style={{
                fontSize:     11,
                fontWeight:   700,
                color:        'var(--teal)',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginBottom: 10,
              }}>
                Key Insight
              </div>
              <div style={{
                fontSize:   13,
                color:      'var(--text-secondary)',
                lineHeight: 1.6,
              }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                  {data.shap.top_feature_display}
                </span>
                {' '}is the dominant predictor with mean SHAP of{' '}
                <span style={{ color: 'var(--teal)', fontWeight: 700, fontFamily: 'monospace' }}>
                  {data.shap.features[0]?.mean_shap.toFixed(0)}
                </span>
                {' '}vs physical features at just{' '}
                <span style={{ color: 'var(--text-primary)', fontWeight: 600, fontFamily: 'monospace' }}>
                  {data.shap.physical_shap_sum.toFixed(1)}
                </span>
                {' '}combined. Location dominates by{' '}
                <span style={{ color: 'var(--teal)', fontWeight: 700 }}>
                  {data.shap.location_dominance_ratio.toFixed(0)}×
                </span>
                {' '}margin.
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

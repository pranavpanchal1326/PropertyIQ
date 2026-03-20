import { motion } from 'framer-motion'
import SeverityBadge from '../ui/SeverityBadge'

export default function Chi2Table({ data }) {
  if (!data?.results?.length) return null
  
  return (
    <div style={{
      background:   'var(--bg-base)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      overflow:     'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding:      '14px 24px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <span style={{
          fontSize:   13,
          fontWeight: 700,
          color:      'var(--text-primary)',
        }}>
          Chi-Square Categorical Drift
        </span>
        <span style={{
          fontSize:   11,
          color:      'var(--text-secondary)',
          marginLeft: 10,
        }}>
          {data.drifted_count} of {data.total_tested} categorical features drifted
        </span>
      </div>
      
      {/* Column headers */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: '1fr 120px 120px 100px',
        padding:             '10px 24px',
        borderBottom:        '1px solid var(--border-subtle)',
        background:          'var(--bg-void)',
        gap:                 16,
      }}>
        {['FEATURE', 'CHI² STAT', 'P-VALUE', 'DRIFT'].map(h => (
          <div key={h} style={{
            fontSize:      9,
            fontWeight:    600,
            color:         'var(--text-ghost)',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
          }}>
            {h}
          </div>
        ))}
      </div>
      
      {/* Rows */}
      {data.results.map((row, i) => (
        <motion.div
          key={row.feature}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08, duration: 0.3 }}
          whileHover={{ background: 'var(--bg-raised)' }}
          style={{
            display:             'grid',
            gridTemplateColumns: '1fr 120px 120px 100px',
            padding:             '0 24px',
            height:              48,
            alignItems:          'center',
            borderBottom:        i < data.results.length - 1
              ? '1px solid var(--border-subtle)'
              : 'none',
            gap:                 16,
            transition:          'background 0.1s',
          }}
        >
          {/* Feature name */}
          <div style={{
            fontSize:   13,
            fontWeight: 500,
            color:      'var(--text-primary)',
            fontFamily: 'monospace',
          }}>
            {row.feature}
          </div>
          
          {/* Chi2 stat */}
          <div style={{
            fontSize:   13,
            fontWeight: row.drifted ? 700 : 400,
            color:      row.drifted ? 'var(--amber)' : 'var(--text-secondary)',
            fontFamily: 'monospace',
          }}>
            {row.chi2_stat.toFixed(4)}
          </div>
          
          {/* P-value */}
          <div style={{
            fontSize:   13,
            color:      row.drifted ? 'var(--amber)' : 'var(--text-secondary)',
            fontFamily: 'monospace',
          }}>
            {row.p_value.toFixed(6)}
          </div>
          
          {/* Severity badge */}
          <SeverityBadge
            severity={row.drifted ? 'HIGH' : 'NONE'}
            size="sm"
          />
        </motion.div>
      ))}
    </div>
  )
}

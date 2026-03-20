import { motion } from 'framer-motion'
import { CheckCircle, XCircle } from 'lucide-react'

function StatusBadge({ status }) {
  const isLive = status === 'LIVE'
  return (
    <div style={{
      display:     'flex',
      alignItems:  'center',
      gap:         6,
      fontSize:    11,
      fontWeight:  600,
      color:       isLive ? 'var(--green)' : 'var(--text-ghost)',
    }}>
      <div
        className={isLive ? 'pulse-dot' : ''}
        style={{
          width:        7,
          height:       7,
          borderRadius: '50%',
          background:   isLive ? 'var(--green)' : 'var(--border-muted)',
          flexShrink:   0,
        }}
      />
      {status}
    </div>
  )
}

function TargetBadge({ met }) {
  return (
    <div style={{
      display:    'flex',
      alignItems: 'center',
      gap:        5,
      fontSize:   11,
      fontWeight: 600,
      color:      met ? 'var(--green)' : 'var(--red)',
    }}>
      {met
        ? <CheckCircle size={13} strokeWidth={2} color="var(--green)" />
        : <XCircle    size={13} strokeWidth={2} color="var(--red)"   />
      }
      {met ? 'TARGET MET' : 'BELOW TARGET'}
    </div>
  )
}

const COLUMNS = [
  { label: 'MODEL',         w: '1fr'  },
  { label: 'TARGET',        w: '100px' },
  { label: 'VAL MAPE',      w: '100px' },
  { label: 'MAPE TARGET',   w: '110px' },
  { label: 'OOB R²',        w: '90px'  },
  { label: 'CONFIDENCE',    w: '110px' },
  { label: 'TRAINED',       w: '140px' },
  { label: 'STATUS',        w: '90px'  },
]

const GRID = COLUMNS.map(c => c.w).join(' ')

export default function ModelTable({ data }) {
  if (!data?.models?.length) return null
  
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
          Model Registry
        </span>
        <span style={{
          fontSize:   11,
          color:      'var(--text-secondary)',
          marginLeft: 10,
        }}>
          {data.live_models} of {data.total_models} models live
        </span>
      </div>
      
      {/* Column headers */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: GRID,
        padding:             '10px 24px',
        borderBottom:        '1px solid var(--border-subtle)',
        background:          'var(--bg-void)',
        gap:                 16,
      }}>
        {COLUMNS.map(col => (
          <div key={col.label} style={{
            fontSize:      9,
            fontWeight:    600,
            color:         'var(--text-ghost)',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
          }}>
            {col.label}
          </div>
        ))}
      </div>
      
      {/* Rows */}
      {data.models.map((model, i) => (
        <motion.div
          key={model.model_key}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08, duration: 0.3 }}
          whileHover={{ background: 'var(--bg-raised)' }}
          style={{
            display:             'grid',
            gridTemplateColumns: GRID,
            padding:             '0 24px',
            height:              56,
            alignItems:          'center',
            borderBottom:        i < data.models.length - 1
              ? '1px solid var(--border-subtle)'
              : 'none',
            gap:                 16,
            transition:          'background 0.1s',
          }}
        >
          {/* Model name */}
          <div>
            <div style={{
              fontSize:   13,
              fontWeight: 600,
              color:      'var(--text-primary)',
              marginBottom: 2,
            }}>
              {model.model_name}
            </div>
            <div style={{
              fontSize:   10,
              color:      'var(--text-ghost)',
              fontFamily: 'monospace',
            }}>
              {model.model_key}
            </div>
          </div>
          
          {/* Target */}
          <div style={{
            fontSize:   12,
            color:      'var(--text-secondary)',
            fontFamily: 'monospace',
          }}>
            {model.target}
          </div>
          
          {/* Val MAPE */}
          <div style={{
            fontSize:   14,
            fontWeight: 700,
            color:      model.mape_target_met ? 'var(--green)' : 'var(--red)',
            fontFamily: 'monospace',
          }}>
            {model.val_mape}%
          </div>
          
          {/* MAPE target */}
          <TargetBadge met={model.mape_target_met} />
          
          {/* OOB R² */}
          <div style={{
            fontSize:   13,
            fontWeight: 600,
            color:      'var(--text-primary)',
            fontFamily: 'monospace',
          }}>
            {model.oob_r2}
          </div>
          
          {/* Confidence mean */}
          <div style={{
            fontSize:   13,
            color:      'var(--text-secondary)',
          }}>
            {model.confidence_mean}%
          </div>
          
          {/* Trained date */}
          <div style={{
            fontSize: 11,
            color:    'var(--text-ghost)',
          }}>
            {new Date(model.trained_at).toLocaleDateString('en-IN', {
              day:   'numeric',
              month: 'short',
              year:  'numeric',
            })}
          </div>
          
          {/* Status */}
          <StatusBadge status={model.status} />
        </motion.div>
      ))}
    </div>
  )
}

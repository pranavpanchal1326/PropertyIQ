import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, ArrowUpRight } from 'lucide-react'
import SeverityBadge from '../ui/SeverityBadge'

export default function CityDriftTable({ data }) {
  const [filter, setFilter] = useState('')
  
  const filtered = useMemo(() => {
    if (!data) return []
    return data.filter(c =>
      c.city.toLowerCase().includes(filter.toLowerCase())
    )
  }, [data, filter])
  
  return (
    <div style={{
      background:   'var(--bg-base)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      overflow:     'hidden',
    }}>
      
      {/* Table header */}
      <div style={{
        padding:        '14px 24px',
        borderBottom:   '1px solid var(--border-subtle)',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        background:     'var(--bg-base)',
      }}>
        <div>
          <span style={{
            fontSize:   13,
            fontWeight: 700,
            color:      'var(--text-primary)',
          }}>
            City-Level KS Drift
          </span>
          <span style={{
            fontSize:    11,
            color:       'var(--text-secondary)',
            marginLeft:  10,
          }}>
            2020 → 2025  ·  All 10 cities
          </span>
        </div>
        
        {/* Filter input */}
        <div style={{
          display:      'flex',
          alignItems:   'center',
          gap:          8,
          background:   'var(--bg-raised)',
          border:       '1px solid var(--border-subtle)',
          borderRadius: 6,
          padding:      '0 12px',
          height:       34,
        }}>
          <Search
            size={13}
            strokeWidth={1.5}
            color="var(--text-ghost)"
          />
          <input
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Filter cities..."
            style={{
              background: 'none',
              border:     'none',
              outline:    'none',
              fontSize:   12,
              color:      'var(--text-primary)',
              width:      140,
              fontFamily: 'inherit',
            }}
          />
        </div>
      </div>
      
      {/* Column headers */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: '56px 1fr 130px 200px 110px',
        padding:             '10px 24px',
        borderBottom:        '1px solid var(--border-subtle)',
        background:          'var(--bg-void)',
      }}>
        {['RANK', 'CITY', 'KS STAT', 'PRICE SHIFT 2020→2025', 'STATUS'].map(h => (
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
      
      {/* Data rows */}
      {filtered.map((city, i) => (
        <motion.div
          key={city.city}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            delay:    i * 0.05,
            duration: 0.3,
            ease:     [0.22, 1, 0.36, 1],
          }}
          whileHover={{ background: 'var(--bg-raised)' }}
          style={{
            display:             'grid',
            gridTemplateColumns: '56px 1fr 130px 200px 110px',
            padding:             '0 24px',
            height:              48,
            alignItems:          'center',
            borderBottom:        '1px solid var(--border-subtle)',
            transition:          'background 0.1s',
            cursor:              'default',
          }}
        >
          {/* Rank circle */}
          <div style={{
            width:          24,
            height:         24,
            borderRadius:   '50%',
            background:     'var(--bg-raised)',
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
            fontSize:       11,
            fontWeight:     500,
            color:          'var(--text-secondary)',
          }}>
            {city.rank}
          </div>
          
          {/* City name */}
          <div style={{
            fontSize:   14,
            fontWeight: 600,
            color:      'var(--text-primary)',
          }}>
            {city.city}
          </div>
          
          {/* KS stat */}
          <div style={{
            fontSize:   14,
            fontWeight: 700,
            color:      'var(--red)',
            fontFamily: 'monospace',
          }}>
            {city.ks_stat.toFixed(4)}
          </div>
          
          {/* Price shift */}
          <div style={{
            display:    'flex',
            alignItems: 'center',
            gap:        4,
            fontSize:   13,
            fontWeight: 600,
            color:      'var(--red)',
          }}>
            <ArrowUpRight size={14} strokeWidth={2} />
            +{city.price_shift_pct.toFixed(2)}%
          </div>
          
          {/* Severity badge */}
          <SeverityBadge severity={city.drift_status} />
        </motion.div>
      ))}
      
      {/* Empty state */}
      {filtered.length === 0 && (
        <div style={{
          padding:        '32px 24px',
          textAlign:      'center',
          color:          'var(--text-ghost)',
          fontSize:       13,
        }}>
          No cities match "{filter}"
        </div>
      )}
    </div>
  )
}

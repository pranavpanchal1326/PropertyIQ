import { motion } from 'framer-motion'
import AnimatedNumber from './AnimatedNumber'

const COLOR_MAP = {
  teal:  {
    text:   'var(--teal)',
    bg:     'var(--teal-glow)',
    border: 'var(--teal-border)',
    edge:   'var(--teal)',
  },
  red:   {
    text:   'var(--red)',
    bg:     'var(--red-glow)',
    border: 'var(--red-border)',
    edge:   'var(--red)',
  },
  amber: {
    text:   'var(--amber)',
    bg:     'var(--amber-glow)',
    border: 'var(--amber-border)',
    edge:   'var(--amber)',
  },
  green: {
    text:   'var(--green)',
    bg:     'var(--green-glow)',
    border: 'var(--green-border)',
    edge:   'var(--green)',
  },
}

/**
 * @param {React.ElementType} icon     - Lucide icon component
 * @param {string}  label              - Uppercase label above value
 * @param {number|string} value        - The main KPI value
 * @param {string}  sub                - Small descriptive text below value
 * @param {string}  color              - teal | red | amber | green
 * @param {string}  prefix             - Prefix for AnimatedNumber
 * @param {string}  suffix             - Suffix for AnimatedNumber
 * @param {number}  decimals           - Decimal places for AnimatedNumber
 * @param {boolean} isText             - If true renders value as-is, no animation
 * @param {number}  index              - Stagger delay index (0-3)
 */
export default function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  color    = 'teal',
  prefix   = '',
  suffix   = '',
  decimals = 0,
  isText   = false,
  index    = 0,
}) {
  const c = COLOR_MAP[color] || COLOR_MAP.teal
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.4,
        delay:    index * 0.07,
        ease:     [0.22, 1, 0.36, 1],
      }}
      whileHover={{
        y: -2,
        borderColor: 'var(--border-muted)',
        transition: { duration: 0.15 },
      }}
      style={{
        position:     'relative',
        background:   'var(--bg-base)',
        border:       '1px solid var(--border-subtle)',
        borderRadius: 8,
        padding:      '20px 24px',
        overflow:     'hidden',
        cursor:       'default',
      }}
    >
      {/* Right edge accent bar */}
      <div style={{
        position:     'absolute',
        right:        0, top: 0,
        width:        3,
        height:       '100%',
        background:   c.bg,
        borderRadius: '0 8px 8px 0',
      }} />
      
      {/* Icon circle + label row */}
      <div style={{
        display:     'flex',
        alignItems:  'center',
        gap:         10,
        marginBottom: 14,
      }}>
        <div style={{
          width:          32,
          height:         32,
          borderRadius:   '50%',
          background:     c.bg,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          flexShrink:     0,
        }}>
          {Icon && <Icon size={15} color={c.text} strokeWidth={1.8} />}
        </div>
        <span style={{
          fontSize:      10,
          fontWeight:    600,
          color:         'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '1.5px',
        }}>
          {label}
        </span>
      </div>
      
      {/* Main value */}
      {isText ? (
        <div style={{
          fontSize:   32,
          fontWeight: 800,
          color:      c.text,
          lineHeight: 1,
          marginBottom: 6,
        }}>
          {value}
        </div>
      ) : (
        <AnimatedNumber
          value={value}
          prefix={prefix}
          suffix={suffix}
          decimals={decimals}
          style={{
            display:      'block',
            fontSize:     32,
            fontWeight:   800,
            color:        c.text,
            lineHeight:   1,
            marginBottom: 6,
          }}
        />
      )}
      
      {/* Sub label */}
      <div style={{
        fontSize: 11,
        color:    'var(--text-ghost)',
        lineHeight: 1.4,
      }}>
        {sub}
      </div>
    </motion.div>
  )
}

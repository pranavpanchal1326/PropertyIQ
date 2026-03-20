import { motion } from 'framer-motion'
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react'
import AnimatedNumber from './AnimatedNumber'

const TIER_CONFIG = {
  TRUSTED: {
    label:     'TRUSTED',
    icon:      CheckCircle,
    color:     '#0D9488',
    bg:        '#0D948812',
    border:    '#0D948840',
    dimColor:  '#0D948830',
  },
  CAUTION: {
    label:     'CAUTION / VERIFY',
    icon:      AlertTriangle,
    color:     '#9A6700',
    bg:        '#9A670010',
    border:    '#9A670040',
    dimColor:  '#9A670030',
  },
  FIELD_VERIFICATION: {
    label:     'FIELD VERIFICATION',
    icon:      XCircle,
    color:     '#CF222E',
    bg:        '#CF222E10',
    border:    '#CF222E40',
    dimColor:  '#CF222E30',
  },
}

/**
 * @param {string} tier  - TRUSTED | CAUTION | FIELD_VERIFICATION
 * @param {number} score - 0 to 100 confidence score
 */
export default function TrustBadge({ tier, score }) {
  const config = TIER_CONFIG[tier] || TIER_CONFIG.TRUSTED
  const Icon   = config.icon
  
  return (
    <motion.div
      initial={{ scale: 0.94, opacity: 0 }}
      animate={{ scale: 1,    opacity: 1 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      style={{
        width:        '100%',
        height:       88,
        borderRadius: 10,
        background:   config.bg,
        border:       `1px solid ${config.border}`,
        display:      'flex',
        alignItems:   'center',
        padding:      '0 24px',
      }}
    >
      {/* Left — icon + tier label */}
      <div style={{
        display:    'flex',
        alignItems: 'center',
        gap:        14,
        flex:       1,
      }}>
        {/* Icon circle */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          style={{
            width:          40,
            height:         40,
            borderRadius:   '50%',
            background:     config.bg,
            border:         `1px solid ${config.border}`,
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
            flexShrink:     0,
          }}
        >
          <Icon size={20} color={config.color} strokeWidth={2} />
        </motion.div>
        
        {/* Tier text */}
        <motion.span
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0  }}
          transition={{ delay: 0.15, duration: 0.3 }}
          style={{
            fontSize:      24,
            fontWeight:    800,
            color:         config.color,
            letterSpacing: '-0.5px',
          }}
        >
          {config.label}
        </motion.span>
      </div>
      
      {/* Center divider */}
      <motion.div
        initial={{ scaleY: 0, opacity: 0 }}
        animate={{ scaleY: 1, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.25 }}
        style={{
          width:        1,
          height:       52,
          background:   config.dimColor,
          margin:       '0 24px',
          flexShrink:   0,
        }}
      />
      
      {/* Right — confidence score */}
      <div style={{ textAlign: 'right', minWidth: 130 }}>
        <div style={{
          display:     'flex',
          alignItems:  'baseline',
          gap:         5,
          justifyContent: 'flex-end',
        }}>
          <AnimatedNumber
            value={score}
            duration={800}
            decimals={0}
            style={{
              fontSize:   40,
              fontWeight: 800,
              color:      config.color,
              lineHeight: 1,
            }}
          />
          <span style={{
            fontSize:   16,
            fontWeight: 400,
            color:      '#8C959F',
          }}>
            / 100
          </span>
        </div>
        <div style={{
          fontSize:      9,
          fontWeight:    600,
          color:         '#8C959F',
          textTransform: 'uppercase',
          letterSpacing: '1.5px',
          marginTop:     6,
        }}>
          Confidence Score
        </div>
      </div>
    </motion.div>
  )
}

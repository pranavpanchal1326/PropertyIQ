const SEVERITY_CONFIG = {
  HIGH:   {
    bg:     'var(--red-glow)',
    border: 'var(--red-border)',
    color:  'var(--red)',
  },
  MEDIUM: {
    bg:     'var(--amber-glow)',
    border: 'var(--amber-border)',
    color:  'var(--amber)',
  },
  LOW:    {
    bg:     'var(--green-glow)',
    border: 'var(--green-border)',
    color:  'var(--green)',
  },
  NONE:   {
    bg:     'var(--bg-raised)',
    border: 'var(--border-subtle)',
    color:  'var(--text-ghost)',
  },
}

/**
 * @param {string} severity - HIGH | MEDIUM | LOW | NONE
 * @param {string} size     - sm | md (default md)
 */
export default function SeverityBadge({ severity, size = 'md' }) {
  const config = SEVERITY_CONFIG[severity?.toUpperCase()] || SEVERITY_CONFIG.NONE
  const isSmall = size === 'sm'
  
  return (
    <span style={{
      display:       'inline-flex',
      alignItems:    'center',
      fontSize:      isSmall ? 9 : 10,
      fontWeight:    700,
      background:    config.bg,
      border:        `1px solid ${config.border}`,
      color:         config.color,
      borderRadius:  4,
      padding:       isSmall ? '2px 8px' : '3px 10px',
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      lineHeight:    1.4,
      whiteSpace:    'nowrap',
    }}>
      {severity}
    </span>
  )
}

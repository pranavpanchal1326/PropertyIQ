import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity, Cpu, MapPin,
  Bell, Settings,
} from 'lucide-react'

// ── Navigation definition ─────────────────────────────────────────────────
const NAV_ITEMS = [
  {
    path:  '/admin/drift',
    label: 'Drift Monitor',
    icon:  Activity,
  },
  {
    path:  '/admin/model',
    label: 'Model Health',
    icon:  Cpu,
  },
  {
    path:  '/admin/city',
    label: 'City Analytics',
    icon:  MapPin,
  },
  {
    path:   '/admin/alerts',
    label:  'Alert Log',
    icon:   Bell,
    badge:  1,
  },
]

// ── PropertyIQ Logomark ───────────────────────────────────────────────────
function Logomark() {
  return (
    <div style={{ position: 'relative', width: 24, height: 24, flexShrink: 0 }}>
      {/* Top-left square — full teal */}
      <div style={{
        width:        15,
        height:       15,
        background:   'var(--teal)',
        borderRadius: 3,
        position:     'absolute',
        top:          0,
        left:         0,
      }} />
      {/* Bottom-right square — dimmed teal, creates depth */}
      <div style={{
        width:        15,
        height:       15,
        background:   'var(--teal)',
        borderRadius: 3,
        position:     'absolute',
        bottom:       0,
        right:        0,
        opacity:      0.45,
      }} />
    </div>
  )
}

// ── Nav Item ──────────────────────────────────────────────────────────────
function NavItem({ path, label, icon: Icon, badge }) {
  const location = useLocation()
  const active   = location.pathname === path
  
  return (
    <NavLink
      to={path}
      style={{ textDecoration: 'none', display: 'block', marginBottom: 2 }}
    >
      <motion.div
        whileHover={{
          background: active ? 'var(--bg-raised)' : 'var(--bg-raised)',
          transition: { duration: 0.1 },
        }}
        style={{
          height:      38,
          borderRadius: 6,
          padding:     '0 12px',
          display:     'flex',
          alignItems:  'center',
          gap:         10,
          background:  active ? 'var(--bg-raised)' : 'transparent',
          // Left border — 2px teal when active, transparent when not
          // Using box-shadow inset to avoid layout shift
          boxShadow:   active
            ? 'inset 2px 0 0 var(--teal)'
            : 'inset 2px 0 0 transparent',
          transition:  'background 0.12s, box-shadow 0.12s',
          cursor:      'pointer',
        }}
      >
        <Icon
          size={16}
          strokeWidth={1.8}
          color={active ? 'var(--teal)' : 'var(--text-ghost)'}
          style={{ flexShrink: 0, transition: 'color 0.12s' }}
        />
        <span style={{
          fontSize:   13,
          fontWeight: active ? 600 : 400,
          color:      active
            ? 'var(--text-primary)'
            : 'var(--text-secondary)',
          flex:       1,
          transition: 'color 0.12s, font-weight 0.12s',
        }}>
          {label}
        </span>
        
        {/* Alert badge */}
        {badge && (
          <span style={{
            fontSize:     10,
            fontWeight:   700,
            background:   'var(--red-glow)',
            color:        'var(--red)',
            border:       '1px solid var(--red-border)',
            borderRadius: 10,
            padding:      '1px 6px',
            lineHeight:   1.4,
          }}>
            {badge}
          </span>
        )}
      </motion.div>
    </NavLink>
  )
}

// ── Model Status Card ─────────────────────────────────────────────────────
function ModelStatusCard() {
  return (
    <div style={{
      margin:       12,
      background:   'var(--bg-raised)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      padding:      14,
    }}>
      {/* Header row — LIVE dot + status + version badge */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        marginBottom:   8,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          {/* Pulsing green dot */}
          <div
            className="pulse-dot"
            style={{
              width:        8,
              height:       8,
              borderRadius: '50%',
              background:   'var(--green)',
              flexShrink:   0,
            }}
          />
          <span style={{
            fontSize:   11,
            fontWeight: 600,
            color:      'var(--green)',
          }}>
            LIVE
          </span>
        </div>
        
        {/* Version badge */}
        <span style={{
          fontSize:     10,
          fontWeight:   500,
          color:        'var(--text-ghost)',
          background:   'var(--border-subtle)',
          borderRadius: 3,
          padding:      '2px 7px',
        }}>
          v1
        </span>
      </div>
      
      {/* Model name */}
      <div style={{
        fontSize:     12,
        fontWeight:   600,
        color:        'var(--text-primary)',
        marginBottom: 4,
      }}>
        sale_price_v1.pkl
      </div>
      
      {/* Model stats */}
      <div style={{
        fontSize: 10,
        color:    'var(--text-secondary)',
        marginBottom: 12,
      }}>
        MAPE 1.61%  ·  OOB R² 0.9968
      </div>
      
      {/* Health bar — animates to 100% on mount */}
      <div style={{
        height:       4,
        borderRadius: 2,
        background:   'var(--border-subtle)',
        overflow:     'hidden',
      }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.6 }}
          style={{
            height:       '100%',
            background:   'var(--green)',
            borderRadius: 2,
          }}
        />
      </div>
    </div>
  )
}

// ── Main Sidebar ──────────────────────────────────────────────────────────
export default function Sidebar() {
  return (
    <aside style={{
      width:          240,
      flexShrink:     0,
      background:     'var(--bg-base)',
      borderRight:    '1px solid var(--border-subtle)',
      display:        'flex',
      flexDirection:  'column',
      height:         '100vh',
      position:       'sticky',
      top:            0,
      overflow:       'hidden',
    }}>
      
      {/* Logo zone */}
      <div style={{
        height:       60,
        padding:      '0 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display:      'flex',
        alignItems:   'center',
        gap:          10,
        flexShrink:   0,
      }}>
        <Logomark />
        <span style={{
          fontSize:   15,
          fontWeight: 700,
          color:      'var(--text-primary)',
        }}>
          PropertyIQ
        </span>
        {/* BETA pill */}
        <span style={{
          fontSize:      9,
          fontWeight:    600,
          color:         'var(--teal)',
          background:    'var(--teal-glow)',
          border:        '1px solid var(--teal-border)',
          borderRadius:  3,
          padding:       '2px 5px',
          letterSpacing: '0.5px',
          marginLeft:    2,
        }}>
          BETA
        </span>
      </div>
      
      {/* Navigation */}
      <nav style={{
        flex:       1,
        padding:    '12px 8px',
        overflowY:  'auto',
      }}>
        {/* ANALYTICS section label */}
        <div style={{
          fontSize:      9,
          fontWeight:    600,
          color:         'var(--text-ghost)',
          textTransform: 'uppercase',
          letterSpacing: '2px',
          padding:       '10px 12px 8px',
        }}>
          Analytics
        </div>
        
        {NAV_ITEMS.map(item => (
          <NavItem key={item.path} {...item} />
        ))}
        
        {/* SYSTEM section label */}
        <div style={{
          fontSize:      9,
          fontWeight:    600,
          color:         'var(--text-ghost)',
          textTransform: 'uppercase',
          letterSpacing: '2px',
          padding:       '16px 12px 8px',
        }}>
          System
        </div>
        
        {/* Settings item — non-navigable, visual only */}
        <motion.div
          whileHover={{
            background: 'var(--bg-raised)',
            transition: { duration: 0.1 },
          }}
          style={{
            height:      38,
            borderRadius: 6,
            padding:     '0 12px',
            display:     'flex',
            alignItems:  'center',
            gap:         10,
            cursor:      'pointer',
          }}
        >
          <Settings
            size={16}
            strokeWidth={1.8}
            color="var(--text-ghost)"
          />
          <span style={{
            fontSize: 13,
            color:    'var(--text-secondary)',
          }}>
            Settings
          </span>
        </motion.div>
      </nav>
      
      {/* Model status — pinned bottom */}
      <div style={{
        borderTop:  '1px solid var(--border-subtle)',
        flexShrink: 0,
      }}>
        <ModelStatusCard />
      </div>
    </aside>
  )
}

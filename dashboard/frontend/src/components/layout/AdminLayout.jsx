import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Bell, Clock } from 'lucide-react'
import Sidebar     from './Sidebar'
import ThemeToggle from '../ui/ThemeToggle'

// ── Page title map ─────────────────────────────────────────────────────────
const PAGE_TITLES = {
  '/admin/drift':   'Drift Monitor',
  '/admin/model':   'Model Health',
  '/admin/city':    'City Analytics',
  '/admin/alerts':  'Alert Log',
}

// ── Top Bar ────────────────────────────────────────────────────────────────
function TopBar({ isDark, onToggle }) {
  const location = useLocation()
  const title    = PAGE_TITLES[location.pathname] || 'Admin'
  
  return (
    <header style={{
      height:          56,
      flexShrink:      0,
      background:      'var(--bg-base)',
      borderBottom:    '1px solid var(--border-subtle)',
      padding:         '0 24px',
      display:         'flex',
      alignItems:      'center',
      justifyContent:  'space-between',
      position:        'sticky',
      top:             0,
      zIndex:          40,
    }}>
      
      {/* Left — breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{
          fontSize: 13,
          color:    'var(--text-secondary)',
        }}>
          Admin
        </span>
        <span style={{
          fontSize: 13,
          color:    'var(--text-ghost)',
          margin:   '0 2px',
        }}>
          /
        </span>
        <span style={{
          fontSize:   13,
          fontWeight: 600,
          color:      'var(--text-primary)',
        }}>
          {title}
        </span>
      </div>
      
      {/* Right — controls */}
      <div style={{
        display:    'flex',
        alignItems: 'center',
        gap:        12,
      }}>
        
        {/* PRODUCTION badge */}
        <span style={{
          fontSize:      10,
          fontWeight:    600,
          background:    'var(--teal-glow)',
          border:        '1px solid var(--teal-border)',
          color:         'var(--teal)',
          borderRadius:  4,
          padding:       '4px 10px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          whiteSpace:    'nowrap',
        }}>
          Production
        </span>
        
        {/* Divider */}
        <div style={{
          width:      1,
          height:     18,
          background: 'var(--border-subtle)',
          flexShrink: 0,
        }} />
        
        {/* Last updated timestamp */}
        <div style={{
          display:    'flex',
          alignItems: 'center',
          gap:        6,
        }}>
          <Clock
            size={12}
            strokeWidth={1.5}
            color="var(--text-ghost)"
          />
          <span style={{
            fontSize:   12,
            color:      'var(--text-secondary)',
            whiteSpace: 'nowrap',
          }}>
            Updated 13 Mar 2026 · 12:06
          </span>
        </div>
        
        {/* Divider */}
        <div style={{
          width:      1,
          height:     18,
          background: 'var(--border-subtle)',
          flexShrink: 0,
        }} />
        
        {/* Theme toggle */}
        <ThemeToggle isDark={isDark} onToggle={onToggle} />
        
        {/* Alert bell */}
        <div style={{ position: 'relative', cursor: 'pointer' }}>
          <Bell
            size={18}
            strokeWidth={1.5}
            color="var(--text-secondary)"
          />
          {/* Red dot */}
          <div style={{
            position:     'absolute',
            top:          -2,
            right:        -2,
            width:        7,
            height:       7,
            borderRadius: '50%',
            background:   'var(--red)',
            border:       '1.5px solid var(--bg-base)',
          }} />
        </div>
      </div>
    </header>
  )
}

// ── Admin Layout ───────────────────────────────────────────────────────────
export default function AdminLayout({ theme, onToggle, isDark }) {
  const location = useLocation()
  
  return (
    <div style={{
      display:    'flex',
      minHeight:  '100vh',
      background: 'var(--bg-void)',
    }}>
      
      {/* Sidebar — always visible */}
      <Sidebar />
      
      {/* Main content area */}
      <div style={{
        flex:          1,
        display:       'flex',
        flexDirection: 'column',
        minWidth:      0,
        overflow:      'hidden',
      }}>
        
        {/* Top bar */}
        <TopBar isDark={isDark} onToggle={onToggle} />
        
        {/* Page content — AnimatePresence for page transitions */}
        <main style={{
          flex:      1,
          overflowY: 'auto',
          padding:   24,
          background: 'var(--bg-void)',
        }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}

import { motion } from 'framer-motion'
import { Sun, Moon } from 'lucide-react'

/**
 * @param {boolean}  isDark    - Current theme state
 * @param {function} onToggle  - Toggle callback
 */
export default function ThemeToggle({ isDark, onToggle }) {
  return (
    <motion.button
      onClick={onToggle}
      whileHover={{ scale: 1.06 }}
      whileTap={{  scale: 0.94 }}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{
        width:          36,
        height:         36,
        borderRadius:   6,
        background:     'var(--bg-raised)',
        border:         '1px solid var(--border-subtle)',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'center',
        cursor:         'pointer',
        color:          'var(--text-secondary)',
        flexShrink:     0,
      }}
    >
      <motion.div
        animate={{ rotate: isDark ? 0 : 180 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        {isDark
          ? <Sun  size={15} strokeWidth={1.8} color="var(--text-secondary)" />
          : <Moon size={15} strokeWidth={1.8} color="var(--text-secondary)" />
        }
      </motion.div>
    </motion.button>
  )
}

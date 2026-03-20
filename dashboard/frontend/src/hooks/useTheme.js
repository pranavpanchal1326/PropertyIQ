import { useState, useEffect, useCallback } from 'react'

export function useTheme() {
  const [theme, setTheme] = useState(() => {
    // Read from localStorage on first render
    // Default to dark — Admin Console is always dark by default
    const stored = localStorage.getItem('piq-theme')
    return stored === 'light' ? 'light' : 'dark'
  })
  
  useEffect(() => {
    // Apply to <html> so CSS [data-theme] selector works
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('piq-theme', theme)
  }, [theme])
  
  const toggle = useCallback(() => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }, [])
  
  const setDark  = useCallback(() => setTheme('dark'),  [])
  const setLight = useCallback(() => setTheme('light'), [])
  
  return {
    theme,
    toggle,
    setDark,
    setLight,
    isDark:  theme === 'dark',
    isLight: theme === 'light',
  }
}

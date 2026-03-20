import { useEffect, useRef, useState } from 'react'
import { useInView } from 'framer-motion'

/**
 * Animates a number from 0 to target value when it enters the viewport.
 * Uses easeOutExpo easing — fast start, smooth finish.
 *
 * @param {number}  value     - Target number to count to
 * @param {number}  duration  - Animation duration in ms (default 1200)
 * @param {string}  prefix    - Text before number e.g. "₹"
 * @param {string}  suffix    - Text after number e.g. "%"
 * @param {number}  decimals  - Decimal places to show (default 0)
 * @param {object}  style     - Inline styles applied to the span
 * @param {string}  className - CSS class names
 */
export default function AnimatedNumber({
  value,
  duration  = 1200,
  prefix    = '',
  suffix    = '',
  decimals  = 0,
  style     = {},
  className = '',
}) {
  const [display, setDisplay] = useState(0)
  const ref                   = useRef(null)
  const isInView              = useInView(ref, { once: true, margin: '0px 0px -40px 0px' })
  const rafRef                = useRef(null)
  
  useEffect(() => {
    if (!isInView) return
    
    const numValue = parseFloat(value) || 0
    const start    = performance.now()
    
    function step(now) {
      const elapsed  = now - start
      const progress = Math.min(elapsed / duration, 1)
      
      // easeOutExpo — snappy start, precise landing
      const eased = progress === 1
        ? 1
        : 1 - Math.pow(2, -10 * progress)
      
      setDisplay(eased * numValue)
      
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(step)
      }
    }
    
    rafRef.current = requestAnimationFrame(step)
    
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [isInView, value, duration])
  
  const formatted = display.toFixed(decimals)
  
  return (
    <span ref={ref} style={style} className={className}>
      {prefix}{formatted}{suffix}
    </span>
  )
}

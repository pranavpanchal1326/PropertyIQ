import { useEffect } from 'react'
import Hero            from './Hero'
import Problem         from './Problem'
import Pillars         from './Pillars'
import RealNumbers     from './RealNumbers'
import ComparisonTable from './ComparisonTable'
import RBICallout      from './RBICallout'
import FinalCTA        from './FinalCTA'
import Footer          from './Footer'

export default function Landing() {
  // Force dark background for landing — independent of admin theme toggle
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'dark')
    return () => {
      // Restore user's theme preference on unmount
      const stored = localStorage.getItem('piq-theme') || 'dark'
      document.documentElement.setAttribute('data-theme', stored)
    }
  }, [])
  
  return (
    <div style={{
      background:    '#06090F',
      color:         '#E6EDF3',
      fontFamily:    "'Plus Jakarta Sans', sans-serif",
      overflowX:     'hidden',
    }}>
      <Hero />
      <Problem />
      <Pillars />
      <RealNumbers />
      <ComparisonTable />
      <RBICallout />
      <FinalCTA />
      <Footer />
    </div>
  )
}

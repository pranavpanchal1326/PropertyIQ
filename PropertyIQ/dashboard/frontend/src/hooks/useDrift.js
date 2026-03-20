import { useState, useEffect } from 'react'
import {
  getDriftSummary,
  getKSFeatures,
  getKSCities,
  getRollingMAPE,
  getChi2,
} from '../api/client'

export function useDrift() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  
  useEffect(() => {
    let cancelled = false
    
    async function fetchAll() {
      try {
        setLoading(true)
        setError(null)
        
        // All 5 in parallel — fastest possible load
        const [summary, features, cities, mape, chi2] = await Promise.all([
          getDriftSummary(),
          getKSFeatures(),
          getKSCities(),
          getRollingMAPE(),
          getChi2(),
        ])
        
        if (cancelled) return
        
        setData({
          summary:  summary.data,
          features: features.data,
          cities:   cities.data,
          mape:     mape.data,
          chi2:     chi2.data,
        })
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.detail || err.message || 'Failed to load drift data')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    
    fetchAll()
    return () => { cancelled = true }
  }, [])
  
  return { data, loading, error }
}

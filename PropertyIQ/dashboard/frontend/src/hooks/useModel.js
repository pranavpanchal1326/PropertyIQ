import { useState, useEffect } from 'react'
import { getModelRegistry, getModelSHAP } from '../api/client'

export function useModel() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  
  useEffect(() => {
    let cancelled = false
    
    async function fetchAll() {
      try {
        setLoading(true)
        const [registry, shap] = await Promise.all([
          getModelRegistry(),
          getModelSHAP(),
        ])
        if (cancelled) return
        setData({
          registry: registry.data,
          shap:     shap.data,
        })
      } catch (err) {
        if (!cancelled) setError(err.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    
    fetchAll()
    return () => { cancelled = true }
  }, [])
  
  return { data, loading, error }
}

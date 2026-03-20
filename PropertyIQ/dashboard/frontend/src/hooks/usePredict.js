import { useState, useCallback } from 'react'
import { predictValuation } from '../api/client'

export function usePredict() {
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)
  
  const predict = useCallback(async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await predictValuation(formData)
      setResult(res.data)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Prediction failed'
      setError(msg)
      return null
    } finally {
      setLoading(false)
    }
  }, [])
  
  const reset = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])
  
  return { result, loading, error, predict, reset }
}

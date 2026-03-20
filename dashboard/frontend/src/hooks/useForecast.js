import { useState, useEffect } from 'react'
import { getAllForecasts, getCityForecast } from '../api/client'

export function useAllForecasts() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  
  useEffect(() => {
    let cancelled = false
    getAllForecasts()
      .then(res  => { if (!cancelled) { setData(res.data);   setLoading(false) } })
      .catch(err => { if (!cancelled) { setError(err.message); setLoading(false) } })
    return () => { cancelled = true }
  }, [])
  
  return { data, loading, error }
}

export function useCityForecast(city) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  
  useEffect(() => {
    if (!city) return
    let cancelled = false
    setLoading(true)
    getCityForecast(city)
      .then(res  => { if (!cancelled) { setData(res.data);   setLoading(false) } })
      .catch(err => { if (!cancelled) { setError(err.message); setLoading(false) } })
    return () => { cancelled = true }
  }, [city])
  
  return { data, loading, error }
}

import { useState, useEffect } from 'react'
import { getDashboardStats } from '../api/client'

export function useDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = () => {
    setLoading(true)
    setError(null)
    getDashboardStats()
      .then((res) => setStats(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load dashboard stats'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { stats, loading, error, refresh }
}

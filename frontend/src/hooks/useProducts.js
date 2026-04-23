import { useState, useEffect } from 'react'
import { getProducts } from '../api/client'

export function useProducts(initialParams = {}) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [params, setParams] = useState(initialParams)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getProducts(params)
      .then((res) => {
        if (!cancelled) {
          const data = res.data
          setProducts(Array.isArray(data) ? data : data.products || [])
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.response?.data?.detail || 'Failed to load products')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [JSON.stringify(params)])

  return { products, loading, error, setParams }
}

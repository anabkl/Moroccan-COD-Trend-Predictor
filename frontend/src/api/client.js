import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API error:', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export const getProducts = (params = {}) => api.get('/products', { params })

export const getTopProducts = (n = 5) => api.get('/products/top', { params: { n } })

export const getProduct = (id) => api.get(`/products/${id}`)

export const getDashboardStats = () => api.get('/dashboard-stats')

export const analyzeComment = (text) => api.post('/analyze-comment', { text })

export const uploadCsv = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export default api

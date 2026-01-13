import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add JWT Authorization header
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log(`INFO [ApiClient]: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error: AxiosError) => {
    console.error('ERROR [ApiClient]: Request interceptor error:', error.message)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`INFO [ApiClient]: Response ${response.status} from ${response.config.url}`)
    return response
  },
  (error: AxiosError) => {
    const status = error.response?.status
    const url = error.config?.url

    console.error(`ERROR [ApiClient]: Response ${status} from ${url}:`, error.message)

    // Handle common error cases
    if (status === 401) {
      console.log('INFO [ApiClient]: Unauthorized - clearing token')
      localStorage.removeItem('token')
      // Redirect to login will be handled by auth context
    }

    return Promise.reject(error)
  }
)

export default apiClient

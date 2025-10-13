/**
 * API Service - Base HTTP client
 * Ham Dog & TC's communication hub with the backend!
 */

import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'

// Helper to get auth token from localStorage
function getAuthToken(): string | null {
  const authTokens = localStorage.getItem('authTokens')
  if (authTokens) {
    try {
      const tokens = JSON.parse(authTokens)
      return tokens.access
    } catch (e) {
      console.error('Failed to parse auth tokens:', e)
    }
  }
  return null
}

// Track if we're currently refreshing to prevent multiple refresh attempts
let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

// Helper to safely parse JSON responses
async function safeJsonParse(response: Response) {
  const text = await response.text()
  
  if (!text) {
    return null
  }
  
  try {
    return JSON.parse(text)
  } catch (err) {
    console.error('Failed to parse JSON response:', err)
    throw new Error('Invalid JSON response from server')
  }
}

// Custom API error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Main API client
class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request(
    endpoint: string,
    options: RequestInit = {},
    isRetry = false
  ): Promise<any> {
    const token = getAuthToken()
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    }

    // Handle body
    if (options.body && typeof options.body !== 'string') {
      config.body = JSON.stringify(options.body)
    }

    const url = `${this.baseURL}${endpoint}`
    
    try {
      const response = await fetch(url, config)
      
      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && !isRetry) {
        // Don't try to refresh for auth endpoints themselves
        if (endpoint.includes('/auth/login') || endpoint.includes('/auth/register')) {
          const errorData = await safeJsonParse(response)
          throw new ApiError(
            errorData?.detail || 'Authentication failed',
            401,
            errorData
          )
        }

        // Handle concurrent refresh attempts
        if (isRefreshing) {
          // Wait for the ongoing refresh
          if (refreshPromise) {
            const refreshSuccess = await refreshPromise
            if (refreshSuccess) {
              // Retry the original request with new token
              return this.request(endpoint, options, true)
            }
          }
        } else {
          // Start a new refresh
          isRefreshing = true
          const authStore = useAuthStore()
          
          refreshPromise = authStore.refreshToken()
          const refreshSuccess = await refreshPromise
          isRefreshing = false
          refreshPromise = null
          
          if (refreshSuccess) {
            // Retry the original request with new token
            return this.request(endpoint, options, true)
          } else {
            // Refresh failed, user needs to login again
            authStore.clearAuth()
            window.location.href = '/auth/login'
            throw new ApiError('Session expired', 401)
          }
        }
      }
      
      // Handle other non-2xx responses
      if (!response.ok) {
        const errorData = await safeJsonParse(response)
        
        // Pass the full error data so stores can extract specific field errors
        const apiError = new ApiError(
          errorData?.detail || errorData?.message || `HTTP ${response.status}`,
          response.status,
          errorData
        )
        
        // Attach response for better error handling
        ;(apiError as any).response = { data: errorData, status: response.status }
        throw apiError
      }
      
      // Handle 204 No Content
      if (response.status === 204) {
        return null
      }
      
      return await safeJsonParse(response)
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      
      // Network or other errors
      console.error('API request failed:', error)
      throw new ApiError(
        'Network error or server unavailable',
        0
      )
    }
  }

  // HTTP methods
  async get(endpoint: string, params?: Record<string, any>): Promise<any> {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : ''
    return this.request(`${endpoint}${queryString}`, {
      method: 'GET',
    })
  }

  async post(endpoint: string, data?: any): Promise<any> {
    return this.request(endpoint, {
      method: 'POST',
      body: data,
    })
  }

  async put(endpoint: string, data?: any): Promise<any> {
    return this.request(endpoint, {
      method: 'PUT',
      body: data,
    })
  }

  async patch(endpoint: string, data?: any): Promise<any> {
    return this.request(endpoint, {
      method: 'PATCH',
      body: data,
    })
  }

  async delete(endpoint: string, options?: { data?: any }): Promise<any> {
    return this.request(endpoint, {
      method: 'DELETE',
      body: options?.data,
    })
  }
}

// Export a singleton instance
const api = new ApiClient()
export default api

// Also export the class for custom instances
export { ApiClient }
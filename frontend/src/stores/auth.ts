import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

export interface User {
  id: number
  public_id: string // Added for project management
  email: string
  first_name: string
  last_name: string
  full_name?: string // Computed field from serializer
  is_active: boolean
  date_joined: string
  roles: string[]
  permissions: string[]
}

export interface LoginCredentials {
  email: string
  password: string
  remember?: boolean
}

export interface RegisterData {
  email: string
  password1: string
  password2: string
  first_name?: string
  last_name?: string
}

interface AuthTokens {
  access: string
  refresh: string
  access_expiry?: number // Unix timestamp for access token expiry
  refresh_expiry?: number // Unix timestamp for refresh token expiry
}

// API URL with fallback
const API_BASE_URL = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'

// Helper function to safely parse JSON responses
const safeJsonParse = async (response: Response) => {
  const text = await response.text()

  if (!text) {
    throw new Error('Empty response from server')
  }

  try {
    return JSON.parse(text)
  } catch (err) {
    console.error('Failed to parse JSON response:', err)
    console.error('Response text:', text)

    // If it looks like HTML (common error page), extract meaningful info
    if (text.includes('<html') || text.includes('<!DOCTYPE')) {
      if (text.includes('404')) {
        throw new Error('API endpoint not found (404)')
      } else if (text.includes('500')) {
        throw new Error('Server error (500)')
      } else if (text.includes('403')) {
        throw new Error('Access forbidden (403)')
      } else {
        throw new Error('Server returned HTML instead of JSON')
      }
    }

    throw new Error('Invalid JSON response from server')
  }
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  let refreshTimer: ReturnType<typeof setTimeout> | null = null

  // Computed
  const isAuthenticated = computed(() => !!user.value && !!tokens.value)
  const userRoles = computed(() => user.value?.roles || [])
  const userPermissions = computed(() => user.value?.permissions || [])
  const userName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.email
  })

  // Actions
  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  const setTokens = (authTokens: AuthTokens, expiryMinutes = 60, refreshDays = 7) => {
    // Calculate token expiry times
    const now = Date.now()
    authTokens.access_expiry = now + expiryMinutes * 60 * 1000
    authTokens.refresh_expiry = now + refreshDays * 24 * 60 * 60 * 1000

    tokens.value = authTokens
    localStorage.setItem('authTokens', JSON.stringify(authTokens))

    // Schedule auto-refresh (refresh 5 minutes before access token expires)
    scheduleTokenRefresh()
  }

  const setUser = (userData: User) => {
    user.value = userData
  }

  const clearAuth = () => {
    user.value = null
    tokens.value = null
    localStorage.removeItem('authTokens')
    localStorage.removeItem('rememberMe')
    localStorage.removeItem('rememberedEmail')

    // Clear any pending refresh timer
    if (refreshTimer) {
      clearTimeout(refreshTimer)
      refreshTimer = null
    }
  }

  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    clearError()

    console.log('API URL:', API_BASE_URL)

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login-custom/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      })

      const data = await safeJsonParse(response)

      if (!response.ok) {
        // Check for email verification error
        if (data.requires_email_verification) {
          const error = {
            message: data.non_field_errors?.[0] || 'Email verification required',
            requires_email_verification: true,
            email: data.email,
            email_sent: data.email_sent,
          }
          throw error
        }
        throw new Error(data.detail || data.non_field_errors?.[0] || 'Login failed')
      }

      // Store tokens with default expiry times (60 min access, 7 day refresh)
      setTokens(
        {
          access: data.access,
          refresh: data.refresh,
        },
        60,
        7,
      )

      // Store user data
      setUser(data.user)

      // Handle remember me functionality
      if (credentials.remember) {
        localStorage.setItem('rememberMe', 'true')
        localStorage.setItem('rememberedEmail', credentials.email)
      } else {
        localStorage.removeItem('rememberMe')
        localStorage.removeItem('rememberedEmail')
      }

      return { success: true, data }
    } catch (err: unknown) {
      // Handle email verification error specially
      if (err && typeof err === 'object' && 'requires_email_verification' in err) {
        const emailError = err as {
          message: string
          requires_email_verification: boolean
          email: string
          email_sent: boolean
        }
        setError(emailError.message)
        return {
          success: false,
          error: emailError.message,
          requires_email_verification: true,
          email: emailError.email,
          email_sent: emailError.email_sent,
        }
      }

      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Network error. Please check your connection and try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: RegisterData) => {
    isLoading.value = true
    clearError()

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      const data = await safeJsonParse(response)

      if (!response.ok) {
        // Handle validation errors
        if (data.email) throw new Error(data.email[0])
        if (data.password1) throw new Error(data.password1[0])
        if (data.password2) throw new Error(data.password2[0])
        if (data.non_field_errors) throw new Error(data.non_field_errors[0])
        throw new Error('Registration failed')
      }

      // Auto-login after successful registration
      setTokens(
        {
          access: data.access,
          refresh: data.refresh,
        },
        60,
        7,
      )

      setUser(data.user)

      return { success: true, data }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Registration failed. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true

    try {
      // Attempt to blacklist the refresh token on the server
      if (tokens.value?.refresh) {
        await fetch(`${API_BASE_URL}/auth/logout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${tokens.value.access}`,
          },
          body: JSON.stringify({
            refresh: tokens.value.refresh,
          }),
        })
      }
    } catch (err) {
      // Continue with logout even if server request fails
      console.warn('Failed to blacklist token on server:', err)
    } finally {
      clearAuth()
      isLoading.value = false
      router.push('/auth/login')
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    if (!tokens.value?.refresh) {
      clearAuth()
      return false
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh: tokens.value.refresh,
        }),
      })

      const data = await safeJsonParse(response)

      if (!response.ok) {
        clearAuth()
        return false
      }

      // Update tokens with new access token (refresh token rotates on backend)
      setTokens(
        {
          access: data.access,
          refresh: data.refresh || tokens.value.refresh, // Keep old refresh if not provided
        },
        60,
        7,
      )

      return true
    } catch {
      clearAuth()
      return false
    }
  }

  const checkAuth = async () => {
    if (!tokens.value?.access) return false

    try {
      const response = await fetch(`${API_BASE_URL}/auth/check/`, {
        headers: {
          Authorization: `Bearer ${tokens.value.access}`,
        },
      })

      if (!response.ok) {
        // Try to refresh token
        const refreshed = await refreshToken()
        if (!refreshed) return false

        // Retry with new token
        const retryResponse = await fetch(`${API_BASE_URL}/auth/check/`, {
          headers: {
            Authorization: `Bearer ${tokens.value!.access}`,
          },
        })

        if (!retryResponse.ok) {
          clearAuth()
          return false
        }

        const authData = await safeJsonParse(retryResponse)
        if (authData.authenticated) {
          // Get full user profile data
          const profileResponse = await fetch(`${API_BASE_URL}/auth/profile/`, {
            headers: {
              Authorization: `Bearer ${tokens.value!.access}`,
            },
          })

          if (profileResponse.ok) {
            const profileData = await safeJsonParse(profileResponse)
            setUser({
              ...profileData.user,
              roles: profileData.rbac.roles,
              permissions: profileData.rbac.permissions,
            })
            return true
          }
        }

        clearAuth()
        return false
      }

      const authData = await safeJsonParse(response)
      if (authData.authenticated) {
        // Get full user profile data
        const profileResponse = await fetch(`${API_BASE_URL}/auth/profile/`, {
          headers: {
            Authorization: `Bearer ${tokens.value.access}`,
          },
        })

        if (profileResponse.ok) {
          const profileData = await safeJsonParse(profileResponse)
          setUser({
            ...profileData.user,
            roles: profileData.rbac.roles,
            permissions: profileData.rbac.permissions,
          })
          return true
        }
      }

      clearAuth()
      return false
    } catch {
      clearAuth()
      return false
    }
  }

  const initializeAuth = async () => {
    // Check for stored tokens
    const storedTokens = localStorage.getItem('authTokens')
    if (storedTokens) {
      try {
        const parsedTokens = JSON.parse(storedTokens) as AuthTokens

        // Check if refresh token is still valid
        if (parsedTokens.refresh_expiry && Date.now() > parsedTokens.refresh_expiry) {
          // Refresh token expired, clear auth
          clearAuth()
          return
        }

        tokens.value = parsedTokens

        // Check if access token needs refresh
        if (parsedTokens.access_expiry && Date.now() > parsedTokens.access_expiry - 60000) {
          // Access token expired or about to expire, refresh it
          await refreshToken()
        }

        // Verify auth status
        await checkAuth()

        // Schedule next refresh if authenticated
        if (isAuthenticated.value) {
          scheduleTokenRefresh()
        }
      } catch {
        clearAuth()
      }
    }
  }

  // Permission helpers
  const hasRole = (role: string): boolean => {
    return userRoles.value.includes(role)
  }

  const hasPermission = (permission: string): boolean => {
    return userPermissions.value.includes(permission)
  }

  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some((role) => hasRole(role))
  }

  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some((permission) => hasPermission(permission))
  }

  // Token refresh scheduler
  const scheduleTokenRefresh = () => {
    // Clear any existing timer
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    if (!tokens.value?.access_expiry) return

    // Calculate when to refresh (5 minutes before expiry)
    const refreshTime = tokens.value.access_expiry - Date.now() - 5 * 60 * 1000

    if (refreshTime > 0) {
      refreshTimer = setTimeout(async () => {
        console.log('Auto-refreshing token...')
        const success = await refreshToken()
        if (success) {
          // Schedule next refresh
          scheduleTokenRefresh()
        } else {
          // Failed to refresh, user needs to login again
          clearAuth()
          router.push('/auth/login')
        }
      }, refreshTime)
    } else {
      // Token needs immediate refresh
      refreshToken().then((success) => {
        if (success) {
          scheduleTokenRefresh()
        } else {
          clearAuth()
          router.push('/auth/login')
        }
      })
    }
  }

  return {
    // State
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    userRoles,
    userPermissions,
    userName,

    // Actions
    login,
    register,
    logout,
    refreshToken,
    checkAuth,
    initializeAuth,
    setError,
    clearError,
    clearAuth,
    setTokens,
    setUser,

    // Permission helpers
    hasRole,
    hasPermission,
    hasAnyRole,
    hasAnyPermission,
  }
})

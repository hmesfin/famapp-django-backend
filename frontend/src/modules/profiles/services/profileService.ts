/**
 * Profile Service Layer
 * API communication hub for user profiles and settings
 */
import api from '@/services/api'
import { ERROR_MESSAGES } from '../constants/index'
import type {
  Profile,
  UserSettings,
  ProfileForm,
  SettingsForm,
  ProfileFilters,
  ProfileResponse,
} from '../types/profile.types'

class ProfileService {
  /**
   * List all profiles with optional filters
   * @param filters - Optional filters for search, location, company
   * @returns Paginated profile response
   */
  async listProfiles(filters?: ProfileFilters): Promise<ProfileResponse> {
    const params = new URLSearchParams()
    if (filters?.search) params.append('search', filters.search)
    if (filters?.location) params.append('location', filters.location)
    if (filters?.company) params.append('company', filters.company)

    const response = await api.get(`/profiles/?${params}`)
    return response
  }

  /**
   * Get a specific profile by public ID
   * @param publicId - The profile's public UUID
   * @returns Profile object
   */
  async getProfile(publicId: string): Promise<Profile> {
    const response = await api.get(`/profiles/${publicId}/`)
    return response
  }

  /**
   * Get the current authenticated user's profile
   * @returns Current user's profile object
   */
  async getCurrentUserProfile(): Promise<Profile> {
    const response = await api.get(`/profiles/me/`)
    return response
  }

  /**
   * Update a profile with new data
   * @param publicId - The profile's public UUID
   * @param data - Profile form data to update
   * @returns Updated profile object
   */
  async updateProfile(publicId: string, data: ProfileForm): Promise<Profile> {
    const response = await api.patch(`/profiles/${publicId}/`, data)
    return response
  }

  /**
   * Update the current user's profile
   * @param data - Profile form data to update
   * @returns Updated profile object
   */
  async updateCurrentUserProfile(data: ProfileForm): Promise<Profile> {
    // Get current user profile first to get the public_id
    const currentProfile = await this.getCurrentUserProfile()
    return this.updateProfile(currentProfile.public_id, data)
  }

  /**
   * Get current user's settings
   * @returns User settings object
   */
  async getUserSettings(): Promise<UserSettings> {
    const response = await api.get(`/settings/current_settings/`)
    return response
  }

  /**
   * Update current user's settings
   * @param data - Settings form data to update
   * @returns Updated settings object
   */
  async updateUserSettings(data: SettingsForm): Promise<UserSettings> {
    const response = await api.patch(`/settings/current_settings/`, data)
    return response
  }

  /**
   * Upload avatar image for current user
   * @param file - Image file to upload (max 5MB)
   * @returns Object with avatar_url property
   * @throws Error if upload fails or file is invalid
   */
  async uploadAvatar(file: File): Promise<{ avatar_url: string; message?: string }> {
    const formData = new FormData()
    formData.append('avatar', file)

    // For FormData, we need to let the browser set Content-Type automatically
    // The api client will handle this correctly when it detects FormData
    const API_BASE_URL = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'
    const token = localStorage.getItem('authTokens')
    let authToken = ''

    if (token) {
      try {
        const tokens = JSON.parse(token)
        authToken = tokens.access
      } catch (e) {
        console.error('Failed to parse auth tokens:', e)
      }
    }

    const response = await fetch(`${API_BASE_URL}/profiles/upload-avatar/`, {
      method: 'POST',
      headers: {
        ...(authToken && { Authorization: `Bearer ${authToken}` }),
        // Don't set Content-Type - let browser set it with boundary for multipart
      },
      body: formData,
    })

    if (!response.ok) {
      let errorData = {}
      try {
        errorData = await response.json()
      } catch (e) {
        // If response is not JSON, create a generic error with personality
        errorData = { detail: ERROR_MESSAGES.AVATAR_UPLOAD_FAILED }
      }

      const error = new Error((errorData as any).detail || ERROR_MESSAGES.AVATAR_UPLOAD_FAILED)
      ;(error as any).response = { data: errorData, status: response.status }
      throw error
    }

    return await response.json()
  }
}

export default new ProfileService()

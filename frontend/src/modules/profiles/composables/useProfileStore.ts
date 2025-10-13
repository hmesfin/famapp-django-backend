/**
 * Profile Store Composable
 * Encapsulates profile store interactions following RefactorA's recommendations
 * Reduces direct store access from components (Feature Envy smell)
 */

import { computed, readonly, ref, Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useProfileStore } from '../stores/profileStore'
import { useSettingsStore } from '../stores/settingsStore'
import { useToastStore } from '@/shared/stores/toastStore'
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '../constants'
import type { Profile, ProfileForm, UserSettings, SettingsForm } from '../types/profile.types'

export interface UseProfileReturn {
  // State (readonly)
  currentUserProfile: Readonly<Ref<Profile | null>>
  currentProfile: Readonly<Ref<Profile | null>>
  profiles: Readonly<Ref<Profile[]>>
  userSettings: Readonly<Ref<UserSettings | null>>
  loading: Readonly<Ref<boolean>>
  error: Readonly<Ref<string | null>>

  // Computed
  isOwnProfile: Readonly<Ref<boolean>>
  hasProfile: Readonly<Ref<boolean>>
  profileCompletion: Readonly<Ref<number>>

  // Actions
  loadCurrentUserProfile: () => Promise<void>
  loadProfile: (publicId: string) => Promise<void>
  updateProfile: (data: ProfileForm) => Promise<void>
  uploadAvatar: (file: File) => Promise<void>
  loadSettings: () => Promise<void>
  updateSettings: (data: SettingsForm) => Promise<void>
  refreshAll: () => Promise<void>
  clearError: () => void
}

/**
 * Composable for managing profile data and operations
 * Provides a clean interface to profile and settings stores
 */
export function useProfile(): UseProfileReturn {
  const profileStore = useProfileStore()
  const settingsStore = useSettingsStore()
  const toastStore = useToastStore()

  // Get reactive references from stores
  const {
    currentUserProfile,
    currentProfile,
    profiles,
    loading: profileLoading,
    error: profileError,
  } = storeToRefs(profileStore)

  const {
    userSettings,
    loading: settingsLoading,
    error: settingsError,
  } = storeToRefs(settingsStore)

  // Combined loading state
  const loading = computed(() => profileLoading.value || settingsLoading.value)

  // Combined error state
  const error = computed(() => profileError.value || settingsError.value)

  // Check if viewing own profile
  const isOwnProfile = computed(() => {
    if (!currentProfile.value || !currentUserProfile.value) return false
    return currentProfile.value.public_id === currentUserProfile.value.public_id
  })

  // Check if user has a profile
  const hasProfile = computed(() => currentUserProfile.value !== null)

  // Calculate profile completion percentage
  const profileCompletion = computed(() => {
    if (!currentUserProfile.value) return 0

    const fields = [
      currentUserProfile.value.bio,
      currentUserProfile.value.location,
      currentUserProfile.value.company,
      currentUserProfile.value.website,
      currentUserProfile.value.avatar_url,
    ]

    const filledFields = fields.filter((field) => field && field.length > 0).length
    return Math.round((filledFields / fields.length) * 100)
  })

  /**
   * Load current user's profile
   */
  async function loadCurrentUserProfile(): Promise<void> {
    try {
      await profileStore.fetchCurrentUserProfile()
    } catch (err) {
      // Error already handled by store
      console.error('Failed to load current user profile:', err)
    }
  }

  /**
   * Load a specific profile by ID
   */
  async function loadProfile(publicId: string): Promise<void> {
    try {
      // Check if it's the current user
      if (publicId === 'me' || publicId === currentUserProfile.value?.public_id) {
        await loadCurrentUserProfile()
        return
      }

      await profileStore.fetchProfile(publicId)
    } catch (err) {
      console.error('Failed to load profile:', err)
    }
  }

  /**
   * Update current user's profile
   */
  async function updateProfile(data: ProfileForm): Promise<void> {
    if (!currentUserProfile.value) {
      toastStore.error('No profile to update')
      throw new Error('No current user profile')
    }

    try {
      await profileStore.updateCurrentUserProfile(data)
      toastStore.success(SUCCESS_MESSAGES.PROFILE_UPDATED)
    } catch (err) {
      // Error already handled by store
      throw err
    }
  }

  /**
   * Upload avatar for current user
   */
  async function uploadAvatar(file: File): Promise<void> {
    try {
      await profileStore.uploadAvatar(file)
      toastStore.success(SUCCESS_MESSAGES.AVATAR_UPLOADED)
    } catch (err) {
      // Error already handled by store
      throw err
    }
  }

  /**
   * Load user settings
   */
  async function loadSettings(): Promise<void> {
    try {
      await settingsStore.fetchUserSettings()
    } catch (err) {
      console.error('Failed to load settings:', err)
    }
  }

  /**
   * Update user settings
   */
  async function updateSettings(data: SettingsForm): Promise<void> {
    try {
      await settingsStore.updateUserSettings(data)
      toastStore.success(SUCCESS_MESSAGES.SETTINGS_UPDATED)
    } catch (err) {
      // Error already handled by store
      throw err
    }
  }

  /**
   * Refresh all profile and settings data
   */
  async function refreshAll(): Promise<void> {
    await Promise.all([loadCurrentUserProfile(), loadSettings()])
  }

  /**
   * Clear any errors
   */
  function clearError(): void {
    profileStore.error = null
    settingsStore.error = null
  }

  return {
    // State (wrapped in readonly to prevent external mutations)
    currentUserProfile: readonly(currentUserProfile),
    currentProfile: readonly(currentProfile),
    profiles: readonly(profiles),
    userSettings: readonly(userSettings),
    loading: readonly(loading),
    error: readonly(error),

    // Computed
    isOwnProfile: readonly(isOwnProfile),
    hasProfile: readonly(hasProfile),
    profileCompletion: readonly(profileCompletion),

    // Actions
    loadCurrentUserProfile,
    loadProfile,
    updateProfile,
    uploadAvatar,
    loadSettings,
    updateSettings,
    refreshAll,
    clearError,
  }
}

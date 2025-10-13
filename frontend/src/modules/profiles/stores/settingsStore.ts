/**
 * Settings Store - Pinia State Management
 * User preferences and settings with persistence
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import profileService from '../services/profileService'
import { useToastStore } from '@/shared/stores/toastStore'
import type { UserSettings, SettingsForm, ThemeOption } from '../types/profile.types'

export const useSettingsStore = defineStore('settings', () => {
  const toastStore = useToastStore()

  // State
  const userSettings = ref<UserSettings | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Theme management with system preference detection
  const systemTheme = ref<'light' | 'dark'>('light')

  // Computed
  const currentTheme = computed(() => {
    // Don't default to light if we haven't loaded settings yet
    // Check localStorage for existing theme preference
    if (!userSettings.value) {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
        return savedTheme === 'auto' ? systemTheme.value : (savedTheme as ThemeOption)
      }
      return systemTheme.value // Use system preference as fallback
    }

    if (userSettings.value.theme === 'auto') {
      return systemTheme.value
    }
    return userSettings.value.theme
  })

  const hasSettings = computed(() => userSettings.value !== null)

  const notificationSettings = computed(() => ({
    email: userSettings.value?.email_notifications ?? true,
    push: userSettings.value?.push_notifications ?? true,
  }))

  const privacySettings = computed(() => ({
    profileVisibility: userSettings.value?.profile_visibility ?? 'public',
    showEmail: userSettings.value?.show_email ?? false,
    showActivity: userSettings.value?.show_activity ?? true,
  }))

  // Actions - Settings fetching
  async function fetchUserSettings() {
    loading.value = true
    error.value = null

    try {
      userSettings.value = await profileService.getUserSettings()
      // Don't apply theme here - the watcher will handle it if needed
      // This prevents theme flashing when navigating to settings
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch user settings'
      toastStore.error('Failed to load user settings')
      // Initialize with default settings if fetch fails
      initializeDefaultSettings()
    } finally {
      loading.value = false
    }
  }

  // Actions - Settings updating
  async function updateUserSettings(data: SettingsForm) {
    if (!userSettings.value) {
      toastStore.error('No settings loaded')
      return false
    }

    loading.value = true
    error.value = null

    try {
      const updatedSettings = await profileService.updateUserSettings(data)
      userSettings.value = updatedSettings

      // Apply theme if it was changed
      if (data.theme) {
        applyTheme()
      }

      toastStore.success('Settings updated successfully!')
      return true
    } catch (err: any) {
      // Extract meaningful error message
      let errorMessage = 'Failed to update settings'

      if (err.response?.data) {
        const errorData = err.response.data

        // Check for specific field errors
        const fieldErrors = []
        if (errorData.theme)
          fieldErrors.push(
            `Theme: ${Array.isArray(errorData.theme) ? errorData.theme[0] : errorData.theme}`,
          )
        if (errorData.language)
          fieldErrors.push(
            `Language: ${Array.isArray(errorData.language) ? errorData.language[0] : errorData.language}`,
          )
        if (errorData.timezone)
          fieldErrors.push(
            `Timezone: ${Array.isArray(errorData.timezone) ? errorData.timezone[0] : errorData.timezone}`,
          )

        if (fieldErrors.length > 0) {
          errorMessage = fieldErrors.join('; ')
        } else if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.non_field_errors) {
          errorMessage = Array.isArray(errorData.non_field_errors)
            ? errorData.non_field_errors[0]
            : errorData.non_field_errors
        }
      } else if (err.message) {
        errorMessage = err.message
      }

      error.value = errorMessage
      toastStore.error(errorMessage)
      return false
    } finally {
      loading.value = false
    }
  }

  // Theme management
  function setTheme(theme: ThemeOption) {
    if (userSettings.value) {
      updateUserSettings({ theme })
    }
  }

  function applyTheme() {
    const theme = currentTheme.value
    const html = document.documentElement

    if (theme === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }

    // Store in localStorage for persistence across page loads
    localStorage.setItem('theme', theme)
  }

  function initializeTheme() {
    // Check for system preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    systemTheme.value = mediaQuery.matches ? 'dark' : 'light'

    // Listen for system theme changes
    mediaQuery.addEventListener('change', (e) => {
      systemTheme.value = e.matches ? 'dark' : 'light'
      if (userSettings.value?.theme === 'auto') {
        applyTheme()
      }
    })

    // Apply saved theme or system preference
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    } else {
      applyTheme()
    }
  }

  // Notification preferences
  async function updateNotificationSettings(settings: { email?: boolean; push?: boolean }) {
    const updateData: SettingsForm = {}
    if (settings.email !== undefined) updateData.email_notifications = settings.email
    if (settings.push !== undefined) updateData.push_notifications = settings.push

    return await updateUserSettings(updateData)
  }

  // Privacy preferences
  async function updatePrivacySettings(settings: {
    profileVisibility?: 'public' | 'private' | 'friends'
    showEmail?: boolean
    showActivity?: boolean
  }) {
    const updateData: SettingsForm = {}
    if (settings.profileVisibility) updateData.profile_visibility = settings.profileVisibility
    if (settings.showEmail !== undefined) updateData.show_email = settings.showEmail
    if (settings.showActivity !== undefined) updateData.show_activity = settings.showActivity

    return await updateUserSettings(updateData)
  }

  // Custom metadata management
  async function updateCustomSetting(key: string, value: any) {
    if (!userSettings.value) return false

    const currentMetadata = userSettings.value.metadata || {}
    const updatedMetadata = { ...currentMetadata, [key]: value }

    return await updateUserSettings({ metadata: updatedMetadata })
  }

  function getCustomSetting<T = any>(key: string, defaultValue?: T): T | undefined {
    return userSettings.value?.metadata?.[key] ?? defaultValue
  }

  // Initialize default settings when API fails
  function initializeDefaultSettings() {
    userSettings.value = {
      public_id: '',
      theme: 'auto',
      language: 'en',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
      email_notifications: true,
      push_notifications: true,
      profile_visibility: 'public',
      show_email: false,
      show_activity: true,
      metadata: null,
    }
  }

  // Reset settings
  function resetSettings() {
    userSettings.value = null
    loading.value = false
    error.value = null
  }

  // Auto-apply theme when settings change
  watch(
    () => currentTheme.value,
    () => {
      applyTheme()
    },
  )

  return {
    // State
    userSettings,
    loading,
    error,
    systemTheme,

    // Computed
    currentTheme,
    hasSettings,
    notificationSettings,
    privacySettings,

    // Actions - Settings
    fetchUserSettings,
    updateUserSettings,

    // Actions - Theme
    setTheme,
    applyTheme,
    initializeTheme,

    // Actions - Notifications
    updateNotificationSettings,

    // Actions - Privacy
    updatePrivacySettings,

    // Actions - Custom metadata
    updateCustomSetting,
    getCustomSetting,

    // Utils
    resetSettings,
  }
})

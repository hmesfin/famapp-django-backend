import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import profileService from '../services/profileService'
import { useToastStore } from '@/shared/stores/toastStore'
import { handleApiError, formatErrorForToast } from '@/shared/utils/errorHandler'
import type { Profile, ProfileForm, ProfileFilters } from '../types/profile.types'

export const useProfileStore = defineStore('profile', () => {
  const toastStore = useToastStore()

  // Single source of truth: Map of profiles by public_id
  const profilesMap = ref<Map<string, Profile>>(new Map())
  const currentUserPublicId = ref<string | null>(null)
  const currentProfilePublicId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Filters
  const profileFilters = ref<ProfileFilters>({})

  // Computed - derived from single source of truth
  const profiles = computed(() => Array.from(profilesMap.value.values()))
  const currentUserProfile = computed(() =>
    currentUserPublicId.value ? profilesMap.value.get(currentUserPublicId.value) || null : null,
  )
  const currentProfile = computed(() =>
    currentProfilePublicId.value
      ? profilesMap.value.get(currentProfilePublicId.value) || null
      : null,
  )
  const hasCurrentUserProfile = computed(() => currentUserProfile.value !== null)
  const currentUserFullName = computed(() => currentUserProfile.value?.user_full_name || '')
  const currentUserEmail = computed(() => currentUserProfile.value?.user_email || '')
  const currentUserAvatar = computed(() => currentUserProfile.value?.avatar_url || null)
  const profileCount = computed(() => profilesMap.value.size)

  // Helper functions for single source of truth
  function setProfile(profile: Profile) {
    profilesMap.value.set(profile.public_id, profile)
  }

  function setProfiles(profileList: Profile[]) {
    // Clear existing profiles and set new ones
    profilesMap.value.clear()
    profileList.forEach((profile) => {
      profilesMap.value.set(profile.public_id, profile)
    })
  }

  function updateProfileInMap(publicId: string, updates: Partial<Profile>) {
    const existingProfile = profilesMap.value.get(publicId)
    if (existingProfile) {
      profilesMap.value.set(publicId, { ...existingProfile, ...updates })
    }
  }

  // Actions - Profile fetching
  async function fetchProfiles(filters?: ProfileFilters) {
    loading.value = true
    error.value = null

    try {
      const response = await profileService.listProfiles(filters)
      setProfiles(response.results || [])
      profileFilters.value = filters || {}
    } catch (err: any) {
      const parsedError = handleApiError(err, 'Failed to fetch profiles')
      error.value = parsedError.message
      toastStore.error(formatErrorForToast(parsedError))
      setProfiles([])
    } finally {
      loading.value = false
    }
  }

  async function fetchProfile(publicId: string) {
    loading.value = true
    error.value = null

    try {
      const profile = await profileService.getProfile(publicId)
      setProfile(profile)
      currentProfilePublicId.value = publicId
    } catch (err: any) {
      const parsedError = handleApiError(err, 'Failed to fetch profile')
      error.value = parsedError.message
      toastStore.error(formatErrorForToast(parsedError))
      currentProfilePublicId.value = null
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUserProfile() {
    loading.value = true
    error.value = null

    try {
      const profile = await profileService.getCurrentUserProfile()
      setProfile(profile)
      currentUserPublicId.value = profile.public_id
    } catch (err: any) {
      const parsedError = handleApiError(err, 'Failed to fetch your profile')
      error.value = parsedError.message
      toastStore.error(formatErrorForToast(parsedError))
      currentUserPublicId.value = null
    } finally {
      loading.value = false
    }
  }

  // Actions - Profile updating
  async function updateProfile(publicId: string, data: ProfileForm) {
    loading.value = true
    error.value = null

    try {
      const updatedProfile = await profileService.updateProfile(publicId, data)

      // Single source of truth: just update the map
      setProfile(updatedProfile)

      toastStore.success('Profile updated successfully!')
      return updatedProfile
    } catch (err: any) {
      // Use shared error handler
      const parsedError = handleApiError(err, 'Failed to update profile')
      error.value = parsedError.message
      toastStore.error(formatErrorForToast(parsedError))
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCurrentUserProfile(data: ProfileForm) {
    if (!currentUserProfile.value) {
      toastStore.error('No current user profile loaded')
      throw new Error('No current user profile loaded')
    }

    return await updateProfile(currentUserProfile.value.public_id, data)
  }

  // Actions - Avatar upload
  async function uploadAvatar(file: File) {
    loading.value = true
    error.value = null

    try {
      const response = await profileService.uploadAvatar(file)

      // Update current user profile with new avatar URL using single source of truth
      if (currentUserPublicId.value) {
        updateProfileInMap(currentUserPublicId.value, {
          avatar_url: response.avatar_url,
        })
      }

      // Return the full response object, not just the URL
      return response
    } catch (err: any) {
      // Use shared error handler
      const parsedError = handleApiError(err, 'Failed to upload avatar')
      error.value = parsedError.message
      toastStore.error(formatErrorForToast(parsedError))
      throw err
    } finally {
      loading.value = false
    }
  }

  // Search and filtering helpers
  function updateFilters(newFilters: ProfileFilters) {
    profileFilters.value = { ...profileFilters.value, ...newFilters }
  }

  function clearFilters() {
    profileFilters.value = {}
  }

  // Backward compatibility helpers
  function clearCurrentProfile() {
    currentProfilePublicId.value = null
  }

  // Reset store
  function resetProfileStore() {
    profilesMap.value.clear()
    currentUserPublicId.value = null
    currentProfilePublicId.value = null
    loading.value = false
    error.value = null
    profileFilters.value = {}
  }

  return {
    profiles,
    currentUserProfile,
    currentProfile,
    loading,
    error,
    profileFilters,
    hasCurrentUserProfile,
    currentUserFullName,
    currentUserEmail,
    currentUserAvatar,
    profileCount,
    fetchProfiles,
    fetchProfile,
    fetchCurrentUserProfile,

    // Actions - Profile updating
    updateProfile,
    updateCurrentUserProfile,

    // Actions - Avatar
    uploadAvatar,

    // Utils
    updateFilters,
    clearFilters,
    clearCurrentProfile,
    resetProfileStore,
  }
})

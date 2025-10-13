/**
 * Profile Composable
 * Reusable logic for profile data fetching and management
 */
import { ref, computed, watch } from 'vue'
import { useProfileStore } from '../stores/profileStore'
import { useDebounce, DEBOUNCE_DELAYS } from '@/composables/useDebounce'
import type { Profile, ProfileFilters } from '../types/profile.types'

export function useProfile() {
  const profileStore = useProfileStore()

  // Local reactive state for search and filtering
  const searchQuery = ref('')
  const locationFilter = ref('')
  const companyFilter = ref('')
  const debouncedSearch = ref('')

  // Enhanced debounced search with our utility
  const debouncedSearchUpdate = useDebounce((query: string) => {
    debouncedSearch.value = query
  }, DEBOUNCE_DELAYS.SEARCH)

  watch(searchQuery, (newValue) => {
    debouncedSearchUpdate(newValue)
  })

  // Debounced filter updates for location and company
  const debouncedLocationUpdate = useDebounce(async () => {
    await fetchProfiles(activeFilters.value)
  }, DEBOUNCE_DELAYS.SEARCH)

  const debouncedCompanyUpdate = useDebounce(async () => {
    await fetchProfiles(activeFilters.value)
  }, DEBOUNCE_DELAYS.SEARCH)

  watch(locationFilter, () => {
    debouncedLocationUpdate()
  })

  watch(companyFilter, () => {
    debouncedCompanyUpdate()
  })

  // Computed filters
  const activeFilters = computed<ProfileFilters>(() => ({
    search: debouncedSearch.value || undefined,
    location: locationFilter.value || undefined,
    company: companyFilter.value || undefined,
  }))

  const hasFilters = computed(() => {
    return !!(debouncedSearch.value || locationFilter.value || companyFilter.value)
  })

  // Profile fetching with filters
  const fetchProfiles = async (customFilters?: ProfileFilters) => {
    const filters = customFilters || activeFilters.value
    await profileStore.fetchProfiles(filters)
  }

  // Fetch current user profile
  const fetchCurrentProfile = async () => {
    await profileStore.fetchCurrentUserProfile()
  }

  // Fetch specific profile by public ID
  const fetchProfileById = async (publicId: string) => {
    await profileStore.fetchProfile(publicId)
  }

  // Search functionality
  const performSearch = async () => {
    await fetchProfiles(activeFilters.value)
  }

  // Filter management
  const clearFilters = () => {
    searchQuery.value = ''
    locationFilter.value = ''
    companyFilter.value = ''
    debouncedSearch.value = ''
    profileStore.clearFilters()
  }

  const applyFilters = async () => {
    await fetchProfiles(activeFilters.value)
  }

  // Auto-search when debouncedSearch changes (already handled by individual watchers above)

  return {
    // Store state
    profiles: computed(() => profileStore.profiles),
    currentProfile: computed(() => profileStore.currentProfile),
    currentUserProfile: computed(() => profileStore.currentUserProfile),
    loading: computed(() => profileStore.loading),
    error: computed(() => profileStore.error),
    profileCount: computed(() => profileStore.profileCount),

    // Debounce states
    searchPending: computed(() => 
      debouncedSearchUpdate.pending.value || 
      debouncedLocationUpdate.pending.value || 
      debouncedCompanyUpdate.pending.value
    ),

    // Current user computed
    hasCurrentUserProfile: computed(() => profileStore.hasCurrentUserProfile),
    currentUserFullName: computed(() => profileStore.currentUserFullName),
    currentUserEmail: computed(() => profileStore.currentUserEmail),
    currentUserAvatar: computed(() => profileStore.currentUserAvatar),

    // Local state for filtering
    searchQuery,
    locationFilter,
    companyFilter,
    activeFilters,
    hasFilters,

    // Actions
    fetchProfiles,
    fetchCurrentProfile,
    fetchProfileById,
    performSearch,
    clearFilters,
    applyFilters,

    // Store actions
    updateProfile: profileStore.updateProfile,
    updateCurrentUserProfile: profileStore.updateCurrentUserProfile,
    uploadAvatar: profileStore.uploadAvatar,
    resetStore: profileStore.resetProfileStore,
  }
}

/**
 * Single Profile Composable
 * For managing a single profile view/edit
 */
export function useSingleProfile(publicId?: string) {
  const profileStore = useProfileStore()
  const isEditing = ref(false)
  const localProfile = ref<Profile | null>(null)

  // Get profile data
  const profile = computed(() => {
    if (publicId) {
      return profileStore.currentProfile
    }
    return profileStore.currentUserProfile || localProfile.value
  })

  // Load profile data
  const loadProfile = async () => {
    if (publicId) {
      await profileStore.fetchProfile(publicId)
    } else {
      await profileStore.fetchCurrentUserProfile()
    }
  }

  // Update profile
  const updateProfile = async (data: any) => {
    if (!profile.value) throw new Error('No profile loaded')

    const result = await profileStore.updateProfile(profile.value.public_id, data)

    // Update local profile if not using store profile
    if (!publicId) {
      localProfile.value = result
    }

    return result
  }

  // Toggle edit mode
  const toggleEdit = () => {
    isEditing.value = !isEditing.value
  }

  const startEdit = () => {
    isEditing.value = true
  }

  const cancelEdit = () => {
    isEditing.value = false
  }

  return {
    // State
    profile,
    isEditing,
    loading: computed(() => profileStore.loading),
    error: computed(() => profileStore.error),

    // Actions
    loadProfile,
    updateProfile,
    toggleEdit,
    startEdit,
    cancelEdit,
    uploadAvatar: profileStore.uploadAvatar,
  }
}

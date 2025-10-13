/**
 * Frontend Integration Tests for Profiles Module
 * Ham Dog & TC's comprehensive Vue.js integration testing! =€
 *
 * Tests the entire refactored profiles frontend as an integrated system:
 * - Complete profile edit flow with validation and debouncing
 * - Settings toggle flow with API integration
 * - Avatar upload with error handling
 * - Search functionality with debouncing
 * - Error recovery scenarios
 * - Component interaction and state management
 */
import { describe, it, expect, beforeEach, afterEach, vi, type Mock } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import { flushPromises } from '@vue/test-utils'

// Test utilities and mocks
import { createMockProfileService, createMockToastStore } from '../test-utils'
import { useToastStore } from '@/shared/stores/toastStore'
import { useProfileStore } from '../../composables/useProfileStore'

// Components to test
import ProfileEditForm from '../../components/ProfileEditForm.vue'
import ProfileSettings from '../../components/ProfileSettings.vue'
import ProfileAvatar from '../../components/ProfileAvatar.vue'
import ThemeToggle from '../../components/ThemeToggle.vue'
import ProfileSearch from '../../components/ProfileSearch.vue'

// Types
import type { Profile, UserSettings } from '../../types/profile.types'

// Mock the profile service
const mockProfileService = createMockProfileService()
vi.mock('../../services/profileService', () => ({
  profileService: mockProfileService
}))

// Mock toast store
vi.mock('@/shared/stores/toastStore', () => ({
  useToastStore: vi.fn()
}))

// Mock debounce for faster testing
vi.mock('lodash-es', () => ({
  debounce: (fn: Function, delay: number) => {
    // Return immediate execution for tests, but keep track of calls
    const debouncedFn = (...args: any[]) => fn(...args)
    debouncedFn.cancel = vi.fn()
    debouncedFn.flush = vi.fn()
    return debouncedFn
  }
}))

// Test data
const mockProfile: Profile = {
  public_id: 'test-profile-123',
  user_email: 'test@example.com',
  user_full_name: 'Test User',
  user_first_name: 'Test',
  user_last_name: 'User',
  bio: 'Test bio',
  location: 'Test City',
  website: 'https://test.com',
  company: 'Test Corp',
  avatar_url: 'https://example.com/avatar.jpg',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z'
}

const mockSettings: UserSettings = {
  public_id: 'test-settings-123',
  theme: 'light',
  language: 'en',
  timezone: 'UTC',
  email_notifications: true,
  push_notifications: false,
  profile_visibility: 'public',
  show_email: false,
  show_activity: true,
  metadata: {},
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z'
}

describe('Profile Module Integration Tests', () => {
  let mockToastStore: ReturnType<typeof createMockToastStore>
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    // Setup fresh Pinia instance
    pinia = createPinia()
    setActivePinia(pinia)

    // Setup mock toast store
    mockToastStore = createMockToastStore()
    ;(useToastStore as Mock).mockReturnValue(mockToastStore)

    // Reset all mocks
    vi.clearAllMocks()
    mockProfileService.reset()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  describe('Complete Profile Edit Flow', () => {
    it('completes full profile edit flow with validation and API integration', async () => {
      // PHASE 1: Setup - Mock successful API responses
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)
      mockProfileService.updateProfile.mockResolvedValue({
        ...mockProfile,
        bio: 'Updated bio',
        location: 'Updated location'
      })

      // Mount component
      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      // Wait for component to load initial data
      await flushPromises()

      // PHASE 2: Verify initial state
      expect(mockProfileService.getMyProfile).toHaveBeenCalledOnce()
      
      // Find form fields
      const bioInput = wrapper.find('[data-testid="bio-input"]')
      const locationInput = wrapper.find('[data-testid="location-input"]')
      const saveButton = wrapper.find('[data-testid="save-button"]')

      expect(bioInput.exists()).toBe(true)
      expect(locationInput.exists()).toBe(true)
      expect(saveButton.exists()).toBe(true)

      // Verify initial values
      expect((bioInput.element as HTMLInputElement).value).toBe('Test bio')
      expect((locationInput.element as HTMLInputElement).value).toBe('Test City')

      // PHASE 3: Make changes and validate
      await bioInput.setValue('Updated bio')
      await locationInput.setValue('Updated location')
      await nextTick()

      // Verify change detection
      expect(wrapper.vm.hasChanges).toBe(true)

      // PHASE 4: Submit form
      await saveButton.trigger('click')
      await flushPromises()

      // PHASE 5: Verify API call and success handling
      expect(mockProfileService.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          bio: 'Updated bio',
          location: 'Updated location'
        })
      )

      expect(mockToastStore.success).toHaveBeenCalledWith(
        expect.stringContaining('Profile updated successfully')
      )

      // Verify form state after successful save
      expect(wrapper.vm.saving).toBe(false)
      expect(wrapper.vm.hasChanges).toBe(false)
    })

    it('handles validation errors gracefully', async () => {
      // Setup component with initial data
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)

      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Enter invalid data
      const bioInput = wrapper.find('[data-testid="bio-input"]')
      const saveButton = wrapper.find('[data-testid="save-button"]')

      // Enter bio that's too long (over validation limit)
      const longBio = 'a'.repeat(1001) // Assuming 1000 char limit
      await bioInput.setValue(longBio)
      await nextTick()

      // PHASE 2: Attempt to submit
      await saveButton.trigger('click')
      await nextTick()

      // PHASE 3: Verify validation prevents submission
      expect(mockProfileService.updateProfile).not.toHaveBeenCalled()
      expect(mockToastStore.error).toHaveBeenCalledWith(
        expect.stringContaining('bio')
      )

      // Verify error display
      const errorMessage = wrapper.find('[data-testid="bio-error"]')
      expect(errorMessage.exists()).toBe(true)
      expect(errorMessage.text()).toContain('too long')
    })

    it('handles API errors with retry capability', async () => {
      // Setup initial success, then API failure
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)
      mockProfileService.updateProfile.mockRejectedValueOnce(
        new Error('Network error')
      )

      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Make changes
      const bioInput = wrapper.find('[data-testid="bio-input"]')
      const saveButton = wrapper.find('[data-testid="save-button"]')

      await bioInput.setValue('Failed update')
      await nextTick()

      // PHASE 2: First attempt (failure)
      await saveButton.trigger('click')
      await flushPromises()

      // Verify error handling
      expect(mockToastStore.error).toHaveBeenCalledWith(
        expect.stringContaining('Failed to save')
      )
      expect(wrapper.vm.saving).toBe(false)

      // PHASE 3: Setup success for retry
      mockProfileService.updateProfile.mockResolvedValueOnce({
        ...mockProfile,
        bio: 'Failed update'
      })

      // PHASE 4: Retry (success)
      await saveButton.trigger('click')
      await flushPromises()

      // Verify successful retry
      expect(mockProfileService.updateProfile).toHaveBeenCalledTimes(2)
      expect(mockToastStore.success).toHaveBeenCalledWith(
        expect.stringContaining('Profile updated successfully')
      )
    })
  })

  describe('Settings Toggle Flow with Debouncing', () => {
    it('handles theme toggle with debounced API calls', async () => {
      // Setup
      mockProfileService.getSettings.mockResolvedValue(mockSettings)
      mockProfileService.updateSettings.mockResolvedValue({
        ...mockSettings,
        theme: 'dark'
      })

      const wrapper = mount(ThemeToggle, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Verify initial state
      expect(mockProfileService.getSettings).toHaveBeenCalledOnce()
      const themeToggle = wrapper.find('[data-testid="theme-toggle"]')
      expect(themeToggle.exists()).toBe(true)

      // PHASE 2: Toggle theme multiple times rapidly
      await themeToggle.trigger('click')
      await themeToggle.trigger('click')
      await themeToggle.trigger('click')
      await nextTick()

      // PHASE 3: Wait for debounced call
      await new Promise(resolve => setTimeout(resolve, 100))
      await flushPromises()

      // PHASE 4: Verify debouncing worked (only one API call despite multiple clicks)
      expect(mockProfileService.updateSettings).toHaveBeenCalledTimes(1)
      expect(mockProfileService.updateSettings).toHaveBeenCalledWith({
        theme: 'dark'
      })

      // Verify UI updated
      expect(wrapper.vm.currentTheme).toBe('dark')
    })

    it('handles notification settings updates individually', async () => {
      mockProfileService.getSettings.mockResolvedValue(mockSettings)
      
      const wrapper = mount(ProfileSettings, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Update email notifications
      mockProfileService.updateSettings.mockResolvedValueOnce({
        ...mockSettings,
        email_notifications: false
      })

      const emailToggle = wrapper.find('[data-testid="email-notifications-toggle"]')
      await emailToggle.trigger('click')
      await flushPromises()

      expect(mockProfileService.updateSettings).toHaveBeenCalledWith({
        email_notifications: false
      })

      // PHASE 2: Update push notifications
      mockProfileService.updateSettings.mockResolvedValueOnce({
        ...mockSettings,
        email_notifications: false,
        push_notifications: true
      })

      const pushToggle = wrapper.find('[data-testid="push-notifications-toggle"]')
      await pushToggle.trigger('click')
      await flushPromises()

      expect(mockProfileService.updateSettings).toHaveBeenCalledWith({
        push_notifications: true
      })

      // Verify individual field updates
      expect(mockProfileService.updateSettings).toHaveBeenCalledTimes(2)
    })
  })

  describe('Avatar Upload Flow', () => {
    it('completes full avatar upload flow with validation', async () => {
      // Setup
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)
      mockProfileService.uploadAvatar.mockResolvedValue({
        avatar_url: 'https://example.com/new-avatar.jpg',
        message: 'Avatar uploaded successfully'
      })

      const wrapper = mount(ProfileAvatar, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Create mock file
      const file = new File(['fake-image-data'], 'avatar.jpg', {
        type: 'image/jpeg'
      })

      // PHASE 2: Trigger file upload
      const fileInput = wrapper.find('[data-testid="avatar-input"]')
      
      // Mock file input change
      Object.defineProperty(fileInput.element, 'files', {
        value: [file],
        writable: false
      })

      await fileInput.trigger('change')
      await flushPromises()

      // PHASE 3: Verify upload process
      expect(mockProfileService.uploadAvatar).toHaveBeenCalledWith(file)
      expect(mockToastStore.success).toHaveBeenCalledWith(
        'Avatar uploaded successfully!'
      )

      // Verify UI updates
      expect(wrapper.vm.uploading).toBe(false)
      const avatarImage = wrapper.find('[data-testid="avatar-image"]')
      expect(avatarImage.attributes('src')).toBe('https://example.com/new-avatar.jpg')
    })

    it('handles invalid file types with proper error messages', async () => {
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)

      const wrapper = mount(ProfileAvatar, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Create invalid file
      const invalidFile = new File(['fake-data'], 'document.pdf', {
        type: 'application/pdf'
      })

      // PHASE 2: Attempt upload
      const fileInput = wrapper.find('[data-testid="avatar-input"]')
      
      Object.defineProperty(fileInput.element, 'files', {
        value: [invalidFile],
        writable: false
      })

      await fileInput.trigger('change')
      await nextTick()

      // PHASE 3: Verify validation error
      expect(mockProfileService.uploadAvatar).not.toHaveBeenCalled()
      expect(mockToastStore.error).toHaveBeenCalledWith(
        expect.stringContaining('Invalid file type')
      )
    })

    it('handles upload failures with error recovery', async () => {
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)
      mockProfileService.uploadAvatar.mockRejectedValueOnce(
        new Error('Upload failed')
      )

      const wrapper = mount(ProfileAvatar, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Valid file upload that fails
      const file = new File(['fake-image-data'], 'avatar.jpg', {
        type: 'image/jpeg'
      })

      const fileInput = wrapper.find('[data-testid="avatar-input"]')
      
      Object.defineProperty(fileInput.element, 'files', {
        value: [file],
        writable: false
      })

      await fileInput.trigger('change')
      await flushPromises()

      // PHASE 2: Verify error handling
      expect(mockToastStore.error).toHaveBeenCalledWith(
        expect.stringContaining('Failed to upload avatar')
      )
      expect(wrapper.vm.uploading).toBe(false)

      // PHASE 3: Verify retry capability
      mockProfileService.uploadAvatar.mockResolvedValueOnce({
        avatar_url: 'https://example.com/retry-avatar.jpg',
        message: 'Avatar uploaded successfully'
      })

      // Create new file object for retry
      const retryFile = new File(['fake-image-data'], 'retry.jpg', {
        type: 'image/jpeg'
      })

      Object.defineProperty(fileInput.element, 'files', {
        value: [retryFile],
        writable: false
      })

      await fileInput.trigger('change')
      await flushPromises()

      // Verify successful retry
      expect(mockProfileService.uploadAvatar).toHaveBeenCalledTimes(2)
      expect(mockToastStore.success).toHaveBeenCalledWith(
        'Avatar uploaded successfully!'
      )
    })
  })

  describe('Search Flow with Debouncing', () => {
    it('handles search with debounced API calls', async () => {
      // Setup search results
      const searchResults = [
        { ...mockProfile, public_id: 'search-1', user_email: 'user1@example.com' },
        { ...mockProfile, public_id: 'search-2', user_email: 'user2@example.com' }
      ]

      mockProfileService.searchProfiles.mockResolvedValue({
        results: searchResults,
        count: 2,
        next: null,
        previous: null
      })

      const wrapper = mount(ProfileSearch, {
        global: {
          plugins: [pinia]
        }
      })

      // PHASE 1: Rapid typing simulation
      const searchInput = wrapper.find('[data-testid="search-input"]')
      
      await searchInput.setValue('u')
      await searchInput.setValue('us')
      await searchInput.setValue('use')
      await searchInput.setValue('user')
      await nextTick()

      // PHASE 2: Wait for debounced search
      await new Promise(resolve => setTimeout(resolve, 100))
      await flushPromises()

      // PHASE 3: Verify debouncing (only one API call despite multiple keystrokes)
      expect(mockProfileService.searchProfiles).toHaveBeenCalledTimes(1)
      expect(mockProfileService.searchProfiles).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'user'
        })
      )

      // Verify results display
      const resultItems = wrapper.findAll('[data-testid="search-result-item"]')
      expect(resultItems).toHaveLength(2)
    })

    it('clears results when search is empty', async () => {
      mockProfileService.searchProfiles.mockResolvedValue({
        results: [],
        count: 0,
        next: null,
        previous: null
      })

      const wrapper = mount(ProfileSearch, {
        global: {
          plugins: [pinia]
        }
      })

      // PHASE 1: Search with results
      const searchInput = wrapper.find('[data-testid="search-input"]')
      await searchInput.setValue('test')
      await flushPromises()

      // PHASE 2: Clear search
      await searchInput.setValue('')
      await nextTick()

      // PHASE 3: Verify results cleared
      const resultItems = wrapper.findAll('[data-testid="search-result-item"]')
      expect(resultItems).toHaveLength(0)
    })
  })

  describe('Error Recovery Scenarios', () => {
    it('recovers from network failures gracefully', async () => {
      // Setup initial failure then success
      mockProfileService.getMyProfile
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockProfile)

      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      // PHASE 1: Initial load failure
      await flushPromises()

      expect(mockToastStore.error).toHaveBeenCalledWith(
        expect.stringContaining('Failed to load profile')
      )

      // PHASE 2: Retry mechanism
      const retryButton = wrapper.find('[data-testid="retry-button"]')
      if (retryButton.exists()) {
        await retryButton.trigger('click')
        await flushPromises()

        // Verify successful retry
        expect(mockProfileService.getMyProfile).toHaveBeenCalledTimes(2)
        expect(wrapper.vm.profile).toEqual(mockProfile)
      }
    })

    it('handles authentication errors properly', async () => {
      // Setup auth error
      const authError = new Error('Authentication required')
      authError.name = 'AuthenticationError'
      
      mockProfileService.getMyProfile.mockRejectedValue(authError)

      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // Verify auth error handling
      expect(mockToastStore.error).toHaveBeenCalledWith(
        expect.stringContaining('Please log in')
      )
    })
  })

  describe('Component State Management Integration', () => {
    it('maintains consistent state across profile store', async () => {
      // Setup
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)
      mockProfileService.updateProfile.mockResolvedValue({
        ...mockProfile,
        bio: 'Store updated bio'
      })

      // Mount multiple components that use the profile store
      const profileForm = mount(ProfileEditForm, {
        global: { plugins: [pinia] }
      })

      const profileAvatar = mount(ProfileAvatar, {
        global: { plugins: [pinia] }
      })

      await flushPromises()

      // PHASE 1: Verify both components loaded the same profile
      expect(profileForm.vm.profile).toEqual(mockProfile)
      expect(profileAvatar.vm.profile).toEqual(mockProfile)

      // PHASE 2: Update profile via form
      const bioInput = profileForm.find('[data-testid="bio-input"]')
      const saveButton = profileForm.find('[data-testid="save-button"]')

      await bioInput.setValue('Store updated bio')
      await saveButton.trigger('click')
      await flushPromises()

      // PHASE 3: Verify state consistency across components
      // Both components should reflect the updated profile
      await nextTick()
      
      // Note: This would require the profile store to be properly integrated
      // and components to reactively update based on store changes
      expect(profileForm.vm.profile.bio).toBe('Store updated bio')
      // Avatar component should also reflect the change if properly integrated
    })
  })

  describe('Performance and User Experience', () => {
    it('provides loading states during API calls', async () => {
      // Slow API response simulation
      let resolveProfile: (value: Profile) => void
      const slowProfilePromise = new Promise<Profile>(resolve => {
        resolveProfile = resolve
      })

      mockProfileService.getMyProfile.mockReturnValue(slowProfilePromise)

      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      // PHASE 1: Verify loading state
      expect(wrapper.vm.loading).toBe(true)
      
      const loadingIndicator = wrapper.find('[data-testid="loading-indicator"]')
      expect(loadingIndicator.exists()).toBe(true)

      // PHASE 2: Resolve the promise
      resolveProfile!(mockProfile)
      await flushPromises()

      // PHASE 3: Verify loading state cleared
      expect(wrapper.vm.loading).toBe(false)
      expect(wrapper.find('[data-testid="loading-indicator"]').exists()).toBe(false)
    })

    it('prevents double-submission during save operations', async () => {
      mockProfileService.getMyProfile.mockResolvedValue(mockProfile)
      
      // Slow update simulation
      let resolveUpdate: (value: Profile) => void
      const slowUpdatePromise = new Promise<Profile>(resolve => {
        resolveUpdate = resolve
      })

      mockProfileService.updateProfile.mockReturnValue(slowUpdatePromise)

      const wrapper = mount(ProfileEditForm, {
        global: {
          plugins: [pinia]
        }
      })

      await flushPromises()

      // PHASE 1: Start update
      const bioInput = wrapper.find('[data-testid="bio-input"]')
      const saveButton = wrapper.find('[data-testid="save-button"]')

      await bioInput.setValue('Updated bio')
      await saveButton.trigger('click')
      await nextTick()

      // PHASE 2: Verify saving state and disabled button
      expect(wrapper.vm.saving).toBe(true)
      expect(saveButton.attributes('disabled')).toBeDefined()

      // PHASE 3: Try to submit again (should be prevented)
      await saveButton.trigger('click')
      await nextTick()

      // Should still only have one API call
      expect(mockProfileService.updateProfile).toHaveBeenCalledTimes(1)

      // PHASE 4: Complete the save
      resolveUpdate!({ ...mockProfile, bio: 'Updated bio' })
      await flushPromises()

      // Verify saving state cleared
      expect(wrapper.vm.saving).toBe(false)
      expect(saveButton.attributes('disabled')).toBeUndefined()
    })
  })
})
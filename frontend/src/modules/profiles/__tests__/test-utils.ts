/**
 * Test Utilities for Profiles Module
 * Ham Dog & TC's testing helper functions! >ê
 * 
 * Provides mock services and utilities for testing profile components
 */
import { vi } from 'vitest'
import type { Profile, UserSettings, ProfileSearchResult } from '../types/profile.types'

/**
 * Mock Profile Service
 * Provides all the methods that the real profileService has
 */
export function createMockProfileService() {
  const mockService = {
    // Profile methods
    getMyProfile: vi.fn(),
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
    searchProfiles: vi.fn(),
    
    // Settings methods
    getSettings: vi.fn(),
    updateSettings: vi.fn(),
    
    // Avatar methods
    uploadAvatar: vi.fn(),
    
    // Utility to reset all mocks
    reset: () => {
      Object.values(mockService).forEach(mock => {
        if (typeof mock === 'function' && 'mockReset' in mock) {
          mock.mockReset()
        }
      })
    }
  }
  
  return mockService
}

/**
 * Mock Toast Store
 * Provides success, error, info, warning methods
 */
export function createMockToastStore() {
  return {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    clear: vi.fn()
  }
}

/**
 * Factory function for creating test profiles
 */
export function createTestProfile(overrides: Partial<Profile> = {}): Profile {
  return {
    public_id: 'test-profile-' + Math.random().toString(36).substr(2, 9),
    user_email: 'test@example.com',
    user_full_name: 'Test User',
    user_first_name: 'Test',
    user_last_name: 'User',
    bio: 'Test bio',
    location: 'Test City',
    website: 'https://test.com',
    company: 'Test Corp',
    avatar_url: 'https://example.com/avatar.jpg',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides
  }
}

/**
 * Factory function for creating test user settings
 */
export function createTestSettings(overrides: Partial<UserSettings> = {}): UserSettings {
  return {
    public_id: 'test-settings-' + Math.random().toString(36).substr(2, 9),
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    email_notifications: true,
    push_notifications: false,
    profile_visibility: 'public',
    show_email: false,
    show_activity: true,
    metadata: {},
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides
  }
}

/**
 * Factory function for creating test search results
 */
export function createTestSearchResult(
  profiles: Profile[] = [],
  count?: number
): ProfileSearchResult {
  return {
    results: profiles,
    count: count ?? profiles.length,
    next: null,
    previous: null
  }
}

/**
 * Utility to mock successful API responses
 */
export function mockSuccessfulAPI(mockService: any) {
  const testProfile = createTestProfile()
  const testSettings = createTestSettings()
  
  mockService.getMyProfile.mockResolvedValue(testProfile)
  mockService.getProfile.mockResolvedValue(testProfile)
  mockService.updateProfile.mockResolvedValue(testProfile)
  mockService.getSettings.mockResolvedValue(testSettings)
  mockService.updateSettings.mockResolvedValue(testSettings)
  mockService.uploadAvatar.mockResolvedValue({
    avatar_url: 'https://example.com/new-avatar.jpg',
    message: 'Avatar uploaded successfully'
  })
  mockService.searchProfiles.mockResolvedValue(
    createTestSearchResult([testProfile])
  )
  
  return { testProfile, testSettings }
}

/**
 * Utility to create validation error responses
 */
export function createValidationError(field: string, message: string) {
  const error = new Error('Validation Error')
  error.name = 'ValidationError'
  ;(error as any).response = {
    data: {
      [field]: [message]
    }
  }
  return error
}

/**
 * Utility to create authentication error
 */
export function createAuthError() {
  const error = new Error('Authentication required')
  error.name = 'AuthenticationError'
  ;(error as any).response = {
    status: 401,
    data: {
      detail: 'Authentication credentials were not provided.'
    }
  }
  return error
}
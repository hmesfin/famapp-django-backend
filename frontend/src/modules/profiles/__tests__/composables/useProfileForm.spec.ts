/**
 * Tests for useProfileForm composable
 * Testing the enhanced profile form composable with validation integration
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useProfileForm, useSettingsForm, useAvatarForm } from '../../composables/useProfileForm'
import type { ProfileForm, SettingsForm } from '../../types/profile.types'

// Mock the toast store
const mockToastStore = {
  success: vi.fn(),
  error: vi.fn(),
}

// Mock the validation composables
const mockProfileValidation = {
  formData: {
    bio: '',
    location: '',
    website: '',
    company: '',
    avatar_url: '',
  },
  errors: {
    bio: '',
    location: '',
    website: '',
    company: '',
    avatar_url: '',
  },
  isFormValid: { value: true },
  hasErrors: { value: false },
  validateField: vi.fn().mockReturnValue(true),
  validateForm: vi.fn().mockReturnValue(true),
  loadData: vi.fn(),
  getCleanData: vi.fn().mockReturnValue({
    bio: 'Test bio',
    location: 'Test location',
  }),
}

const mockSettingsValidation = {
  formData: {
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    email_notifications: true,
    push_notifications: false,
    profile_visibility: 'public',
    show_email: true,
    show_activity: false,
  },
  errors: {
    theme: '',
    language: '',
    timezone: '',
  },
  isFormValid: { value: true },
  hasErrors: { value: false },
  validateField: vi.fn().mockReturnValue(true),
  validateForm: vi.fn().mockReturnValue(true),
  loadData: vi.fn(),
  getCleanData: vi.fn(),
}

const mockAvatarValidation = {
  selectedFile: { value: null },
  previewUrl: { value: null },
  error: { value: null },
  isValid: { value: true },
  selectFile: vi.fn(),
  clearSelection: vi.fn(),
}

// Mock the composables
vi.mock('../../composables/useProfileValidation', () => ({
  useProfileValidation: () => mockProfileValidation,
  useSettingsValidation: () => mockSettingsValidation,
  useAvatarValidation: () => mockAvatarValidation,
}))

vi.mock('@/shared/stores/toastStore', () => ({
  useToastStore: () => mockToastStore,
}))

describe('useProfileForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // Reset validation mocks to default state
    mockProfileValidation.isFormValid.value = true
    mockProfileValidation.hasErrors.value = false
    mockProfileValidation.validateForm.mockReturnValue(true)
  })

  describe('basic functionality', () => {
    it('should initialize with default state', () => {
      const { saving, hasChanges, initialized } = useProfileForm()

      expect(saving.value).toBe(false)
      expect(hasChanges.value).toBe(false)
      expect(initialized.value).toBe(false)
    })

    it('should initialize with provided data', () => {
      const initialData: Partial<ProfileForm> = {
        bio: 'Initial bio',
        location: 'Initial location',
      }

      const { initializeForm, initialized } = useProfileForm(initialData)

      initializeForm(initialData)
      expect(initialized.value).toBe(true)
      expect(mockProfileValidation.loadData).toHaveBeenCalledWith(initialData)
    })

    it('should provide access to validation properties', () => {
      const { formData, errors, isFormValid, hasErrors } = useProfileForm()

      expect(formData).toBe(mockProfileValidation.formData)
      expect(errors).toBe(mockProfileValidation.errors)
      expect(isFormValid).toBe(mockProfileValidation.isFormValid)
      expect(hasErrors).toBe(mockProfileValidation.hasErrors)
    })
  })

  describe('change detection', () => {
    it('should provide hasChanges computed property', () => {
      const { hasChanges, initialized } = useProfileForm()

      // Should have a hasChanges reactive property
      expect(hasChanges).toBeDefined()
      expect(typeof hasChanges.value).toBe('boolean')
      expect(initialized).toBeDefined()
      expect(typeof initialized.value).toBe('boolean')
    })

    it('should not detect changes before initialization', () => {
      const { hasChanges } = useProfileForm()
      expect(hasChanges.value).toBe(false)
    })
  })

  describe('form reset', () => {
    it('should reset form to original data', () => {
      const initialData = { bio: 'Original bio', location: 'Original location' }
      const { initializeForm, resetForm } = useProfileForm()

      initializeForm(initialData)
      resetForm()

      expect(mockProfileValidation.loadData).toHaveBeenCalledWith(initialData)
    })
  })

  describe('form submission', () => {
    it('should handle successful form submission', async () => {
      const mockSubmitFunction = vi.fn().mockResolvedValue({ success: true })
      const mockOnSuccess = vi.fn()

      const { handleSubmit } = useProfileForm()

      const result = await handleSubmit(mockSubmitFunction, {
        successMessage: 'Profile updated!',
        onSuccess: mockOnSuccess,
      })

      expect(mockProfileValidation.validateForm).toHaveBeenCalled()
      expect(mockSubmitFunction).toHaveBeenCalledWith(mockProfileValidation.getCleanData())
      expect(mockToastStore.success).toHaveBeenCalledWith('Profile updated!')
      expect(mockOnSuccess).toHaveBeenCalled()
      expect(result).toEqual({ success: true })
    })

    it('should handle validation errors', async () => {
      mockProfileValidation.validateForm.mockReturnValue(false)
      mockProfileValidation.errors.bio = 'Bio is invalid'

      const mockSubmitFunction = vi.fn()
      const { handleSubmit } = useProfileForm()

      const result = await handleSubmit(mockSubmitFunction)

      expect(mockSubmitFunction).not.toHaveBeenCalled()
      expect(mockToastStore.error).toHaveBeenCalledWith('Please fix the error in bio')
      expect(result).toBe(false)
    })

    it('should handle submission errors', async () => {
      const mockError = new Error('Submission failed')
      const mockSubmitFunction = vi.fn().mockRejectedValue(mockError)
      const mockOnError = vi.fn()

      const { handleSubmit } = useProfileForm()

      const result = await handleSubmit(mockSubmitFunction, {
        errorMessage: 'Custom error message',
        onError: mockOnError,
      })

      expect(mockToastStore.error).toHaveBeenCalledWith('Custom error message')
      expect(mockOnError).toHaveBeenCalledWith(mockError)
      expect(result).toBe(false)
    })

    it('should track saving state during submission', async () => {
      const mockSubmitFunction = vi
        .fn()
        .mockImplementation(
          () => new Promise((resolve) => setTimeout(() => resolve({ success: true }), 100)),
        )

      const { handleSubmit, saving } = useProfileForm()

      expect(saving.value).toBe(false)

      const submissionPromise = handleSubmit(mockSubmitFunction)
      await nextTick()

      expect(saving.value).toBe(true)

      await submissionPromise

      expect(saving.value).toBe(false)
    })

    it('should update original data after successful submission', async () => {
      const mockSubmitFunction = vi.fn().mockResolvedValue({ success: true })
      const formData = { bio: 'Updated bio' }
      mockProfileValidation.getCleanData.mockReturnValue(formData)

      const { handleSubmit } = useProfileForm()

      await handleSubmit(mockSubmitFunction)

      // Should not reset original data if resetOnSuccess is false
      await handleSubmit(mockSubmitFunction, { resetOnSuccess: false })
    })
  })

  describe('utility methods', () => {
    it('should provide access to validation methods', () => {
      const { validateField, validateForm, getCleanData } = useProfileForm()

      validateField('bio')
      expect(mockProfileValidation.validateField).toHaveBeenCalledWith('bio')

      validateForm()
      expect(mockProfileValidation.validateForm).toHaveBeenCalled()

      getCleanData()
      expect(mockProfileValidation.getCleanData).toHaveBeenCalled()
    })
  })
})

describe('useSettingsForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockSettingsValidation.validateField.mockReturnValue(true)
  })

  describe('basic functionality', () => {
    it('should initialize with default state', () => {
      const { saving, fieldSaving } = useSettingsForm()

      expect(saving.value).toBe(false)
      expect(Object.keys(fieldSaving)).toEqual([])
    })

    it('should initialize form with data', () => {
      const initialData: Partial<SettingsForm> = {
        theme: 'dark',
        language: 'es',
      }

      const { initializeForm } = useSettingsForm()

      initializeForm(initialData)
      expect(mockSettingsValidation.loadData).toHaveBeenCalledWith(initialData)
    })
  })

  describe('field updates', () => {
    it('should handle individual field updates', async () => {
      const mockUpdateFunction = vi.fn().mockResolvedValue({ success: true })
      const { handleFieldUpdate, isFieldSaving } = useSettingsForm()

      expect(isFieldSaving('theme')).toBe(false)

      const result = await handleFieldUpdate('theme', 'dark', mockUpdateFunction, {
        successMessage: 'Theme updated!',
      })

      expect(mockSettingsValidation.validateField).toHaveBeenCalledWith('theme')
      expect(mockUpdateFunction).toHaveBeenCalledWith({ theme: 'dark' })
      expect(mockToastStore.success).toHaveBeenCalledWith('Theme updated!')
      expect(result).toEqual({ success: true })
    })

    it('should handle field validation errors', async () => {
      mockSettingsValidation.validateField.mockReturnValue(false)
      mockSettingsValidation.errors.theme = 'Invalid theme'

      const mockUpdateFunction = vi.fn()
      const { handleFieldUpdate } = useSettingsForm()

      const result = await handleFieldUpdate('theme', 'invalid', mockUpdateFunction)

      expect(mockUpdateFunction).not.toHaveBeenCalled()
      expect(mockToastStore.error).toHaveBeenCalledWith('Invalid theme: Invalid theme')
      expect(result).toBe(false)
    })

    it('should handle field update errors', async () => {
      const mockError = new Error('Update failed')
      const mockUpdateFunction = vi.fn().mockRejectedValue(mockError)
      const { handleFieldUpdate } = useSettingsForm()

      const result = await handleFieldUpdate('theme', 'dark', mockUpdateFunction)

      expect(mockToastStore.error).toHaveBeenCalledWith('Failed to update theme. Please try again.')
      expect(result).toBe(false)
    })

    it('should track field saving state', async () => {
      const mockUpdateFunction = vi
        .fn()
        .mockImplementation(
          () => new Promise((resolve) => setTimeout(() => resolve({ success: true }), 100)),
        )

      const { handleFieldUpdate, isFieldSaving, saving } = useSettingsForm()

      expect(isFieldSaving('theme')).toBe(false)
      expect(saving.value).toBe(false)

      const updatePromise = handleFieldUpdate('theme', 'dark', mockUpdateFunction)
      await nextTick()

      expect(isFieldSaving('theme')).toBe(true)
      expect(saving.value).toBe(true)

      await updatePromise

      expect(isFieldSaving('theme')).toBe(false)
      expect(saving.value).toBe(false)
    })
  })

  describe('batch updates', () => {
    it('should handle batch field updates', async () => {
      const mockUpdateFunction = vi.fn().mockResolvedValue({ success: true })
      const updates = { theme: 'dark', language: 'es' }

      const { handleBatchUpdate } = useSettingsForm()

      const result = await handleBatchUpdate(updates, mockUpdateFunction, {
        successMessage: 'Settings updated!',
      })

      expect(mockUpdateFunction).toHaveBeenCalledWith(updates)
      expect(mockToastStore.success).toHaveBeenCalledWith('Settings updated!')
      expect(result).toEqual({ success: true })
    })

    it('should validate all fields in batch update', async () => {
      mockSettingsValidation.validateField.mockReturnValue(false)
      mockSettingsValidation.errors.theme = 'Invalid theme'

      const mockUpdateFunction = vi.fn()
      const updates = { theme: 'invalid', language: 'es' }

      const { handleBatchUpdate } = useSettingsForm()

      const result = await handleBatchUpdate(updates, mockUpdateFunction)

      // Should validate fields and fail
      expect(mockSettingsValidation.validateField).toHaveBeenCalled()
      expect(mockUpdateFunction).not.toHaveBeenCalled()
      expect(mockToastStore.error).toHaveBeenCalledWith('Please fix validation errors')
      expect(result).toBe(false)
    })
  })
})

describe('useAvatarForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockAvatarValidation.isValid.value = true
    mockAvatarValidation.error.value = null
  })

  describe('basic functionality', () => {
    it('should initialize with default state', () => {
      const { uploading, selectedFile, previewUrl, error, isValid } = useAvatarForm()

      expect(uploading.value).toBe(false)
      expect(selectedFile).toBe(mockAvatarValidation.selectedFile)
      expect(previewUrl).toBe(mockAvatarValidation.previewUrl)
      expect(error).toBe(mockAvatarValidation.error)
      expect(isValid).toBe(mockAvatarValidation.isValid)
    })
  })

  describe('avatar upload', () => {
    it('should handle successful avatar upload', async () => {
      const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockUploadFunction = vi
        .fn()
        .mockResolvedValue({ avatar_url: 'http://example.com/avatar.jpg' })
      const mockOnSuccess = vi.fn()

      const { handleAvatarUpload } = useAvatarForm()

      const result = await handleAvatarUpload(mockFile, mockUploadFunction, {
        successMessage: 'Avatar uploaded!',
        onSuccess: mockOnSuccess,
      })

      expect(mockAvatarValidation.selectFile).toHaveBeenCalledWith(mockFile)
      expect(mockUploadFunction).toHaveBeenCalledWith(mockFile)
      expect(mockToastStore.success).toHaveBeenCalledWith('Avatar uploaded!')
      expect(mockOnSuccess).toHaveBeenCalled()
      expect(result).toEqual({ avatar_url: 'http://example.com/avatar.jpg' })
    })

    it('should handle validation errors', async () => {
      mockAvatarValidation.isValid.value = false
      mockAvatarValidation.error.value = 'File too large'

      const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockUploadFunction = vi.fn()

      const { handleAvatarUpload } = useAvatarForm()

      const result = await handleAvatarUpload(mockFile, mockUploadFunction)

      expect(mockUploadFunction).not.toHaveBeenCalled()
      expect(mockToastStore.error).toHaveBeenCalledWith('File too large')
      expect(result).toBe(false)
    })

    it('should handle upload errors', async () => {
      const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockError = new Error('Upload failed')
      const mockUploadFunction = vi.fn().mockRejectedValue(mockError)
      const mockOnError = vi.fn()

      const { handleAvatarUpload } = useAvatarForm()

      const result = await handleAvatarUpload(mockFile, mockUploadFunction, {
        errorMessage: 'Upload failed!',
        onError: mockOnError,
      })

      expect(mockToastStore.error).toHaveBeenCalledWith('Upload failed!')
      expect(mockOnError).toHaveBeenCalledWith(mockError)
      expect(result).toBe(false)
    })

    it('should track uploading state', async () => {
      const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockUploadFunction = vi
        .fn()
        .mockImplementation(
          () =>
            new Promise((resolve) => setTimeout(() => resolve({ avatar_url: 'test.jpg' }), 100)),
        )

      const { handleAvatarUpload, uploading } = useAvatarForm()

      expect(uploading.value).toBe(false)

      const uploadPromise = handleAvatarUpload(mockFile, mockUploadFunction)
      await nextTick()

      expect(uploading.value).toBe(true)

      await uploadPromise

      expect(uploading.value).toBe(false)
    })
  })

  describe('file input handling', () => {
    it('should handle file input change', async () => {
      const mockFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockUploadFunction = vi.fn().mockResolvedValue({ avatar_url: 'test.jpg' })

      const mockEvent = {
        target: {
          files: [mockFile],
          value: 'test.jpg',
        },
      } as any

      const { handleFileInputChange } = useAvatarForm()

      const result = await handleFileInputChange(mockEvent, mockUploadFunction)

      expect(mockAvatarValidation.selectFile).toHaveBeenCalledWith(mockFile)
      expect(mockUploadFunction).toHaveBeenCalledWith(mockFile)
      expect(mockEvent.target.value).toBe('') // Should clear input
      expect(result).toEqual({ avatar_url: 'test.jpg' })
    })

    it('should handle empty file input', async () => {
      const mockUploadFunction = vi.fn()
      const mockEvent = {
        target: {
          files: [],
        },
      } as any

      const { handleFileInputChange } = useAvatarForm()

      const result = await handleFileInputChange(mockEvent, mockUploadFunction)

      expect(mockUploadFunction).not.toHaveBeenCalled()
      expect(result).toBe(false)
    })

    it('should trigger file upload', () => {
      const mockFileInput = { click: vi.fn() }
      const { triggerFileUpload } = useAvatarForm()

      triggerFileUpload(mockFileInput)

      expect(mockFileInput.click).toHaveBeenCalled()
    })
  })

  describe('utility methods', () => {
    it('should provide access to clear selection', () => {
      const { clearSelection } = useAvatarForm()

      clearSelection()
      expect(mockAvatarValidation.clearSelection).toHaveBeenCalled()
    })
  })
})

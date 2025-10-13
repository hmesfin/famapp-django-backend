/**
 * Tests for useProfileValidation composable
 * Testing the profile validation rules and form validation logic
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import {
  useProfileValidation,
  useSettingsValidation,
  useAvatarValidation,
  validationRules,
} from '../../composables/useProfileValidation'
import type { ProfileForm, SettingsForm } from '../../types/profile.types'

// Mock the debounce composable
vi.mock('@/composables/useDebounce', () => ({
  useDebounce: (fn: Function, delay: number) => {
    const mockDebounced = vi.fn((...args: any[]) => fn(...args))
    return Object.assign(mockDebounced, {
      cancel: vi.fn(),
      flush: vi.fn(),
      pending: { value: false },
    })
  },
  DEBOUNCE_DELAYS: {
    SEARCH: 300,
    VALIDATION: 500,
    SETTINGS: 200,
    API_CALLS: 500,
    FILE_UPLOAD: 1000,
  },
}))

describe('validationRules', () => {
  describe('required rule', () => {
    it('should return error for empty values', () => {
      const rule = validationRules.required()

      expect(rule('')).toBe('This field is required')
      expect(rule('   ')).toBe('This field is required')
      expect(rule(null)).toBe('This field is required')
      expect(rule(undefined)).toBe('This field is required')
    })

    it('should return true for non-empty values', () => {
      const rule = validationRules.required()

      expect(rule('valid')).toBe(true)
      expect(rule('0')).toBe(true)
      expect(rule(0)).toBe(true)
      expect(rule(false)).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.required('Custom message')

      expect(rule('')).toBe('Custom message')
    })
  })

  describe('minLength rule', () => {
    it('should return error for strings too short', () => {
      const rule = validationRules.minLength(5)

      expect(rule('abc')).toBe('Must be at least 5 characters')
    })

    it('should return true for strings long enough', () => {
      const rule = validationRules.minLength(5)

      expect(rule('abcde')).toBe(true)
      expect(rule('abcdef')).toBe(true)
    })

    it('should return true for empty strings (optional)', () => {
      const rule = validationRules.minLength(5)

      expect(rule('')).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.minLength(5, 'Too short!')

      expect(rule('abc')).toBe('Too short!')
    })
  })

  describe('maxLength rule', () => {
    it('should return error for strings too long', () => {
      const rule = validationRules.maxLength(5)

      expect(rule('abcdef')).toBe('Must be 5 characters or less')
    })

    it('should return true for strings short enough', () => {
      const rule = validationRules.maxLength(5)

      expect(rule('abc')).toBe(true)
      expect(rule('abcde')).toBe(true)
    })

    it('should return true for empty strings', () => {
      const rule = validationRules.maxLength(5)

      expect(rule('')).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.maxLength(5, 'Too long!')

      expect(rule('abcdef')).toBe('Too long!')
    })
  })

  describe('url rule', () => {
    it('should return true for valid URLs', () => {
      const rule = validationRules.url()

      expect(rule('https://example.com')).toBe(true)
      expect(rule('http://example.com')).toBe(true)
      expect(rule('example.com')).toBe(true) // Should add https://
      expect(rule('www.example.com')).toBe(true)
    })

    it('should return error for invalid URLs', () => {
      const rule = validationRules.url()

      expect(rule('not-a-url')).toBe('Please enter a valid URL')
      expect(rule('ftp://example.com')).toBe('Please enter a valid URL')
      expect(rule('javascript:alert(1)')).toBe('Please enter a valid URL')
    })

    it('should return true for empty strings (optional)', () => {
      const rule = validationRules.url()

      expect(rule('')).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.url('Invalid URL!')

      expect(rule('not-a-url')).toBe('Invalid URL!')
    })
  })

  describe('fileSize rule', () => {
    it('should return true for files within size limit', () => {
      const rule = validationRules.fileSize(5) // 5MB

      const smallFile = new File(['x'.repeat(1024 * 1024)], 'test.jpg') // 1MB
      expect(rule(smallFile)).toBe(true)
    })

    it('should return error for files too large', () => {
      const rule = validationRules.fileSize(1) // 1MB

      const largeFile = new File(['x'.repeat(2 * 1024 * 1024)], 'test.jpg') // 2MB
      expect(rule(largeFile)).toBe('File size must be less than 1MB')
    })

    it('should return true for null/undefined files', () => {
      const rule = validationRules.fileSize(5)

      expect(rule(null as any)).toBe(true)
      expect(rule(undefined as any)).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.fileSize(1, 'File too big!')

      const largeFile = new File(['x'.repeat(2 * 1024 * 1024)], 'test.jpg')
      expect(rule(largeFile)).toBe('File too big!')
    })
  })

  describe('fileType rule', () => {
    it('should return true for allowed file types', () => {
      const rule = validationRules.fileType(['image/jpeg', 'image/png'])

      const jpegFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const pngFile = new File([''], 'test.png', { type: 'image/png' })

      expect(rule(jpegFile)).toBe(true)
      expect(rule(pngFile)).toBe(true)
    })

    it('should return error for disallowed file types', () => {
      const rule = validationRules.fileType(['image/jpeg', 'image/png'])

      const pdfFile = new File([''], 'test.pdf', { type: 'application/pdf' })
      expect(rule(pdfFile)).toBe('File type must be one of: image/jpeg, image/png')
    })

    it('should return true for null/undefined files', () => {
      const rule = validationRules.fileType(['image/jpeg'])

      expect(rule(null as any)).toBe(true)
      expect(rule(undefined as any)).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.fileType(['image/jpeg'], 'Wrong file type!')

      const pdfFile = new File([''], 'test.pdf', { type: 'application/pdf' })
      expect(rule(pdfFile)).toBe('Wrong file type!')
    })
  })

  describe('email rule', () => {
    it('should return true for valid emails', () => {
      const rule = validationRules.email()

      expect(rule('test@example.com')).toBe(true)
      expect(rule('user.name+tag@domain.co.uk')).toBe(true)
    })

    it('should return error for invalid emails', () => {
      const rule = validationRules.email()

      expect(rule('invalid-email')).toBe('Please enter a valid email address')
      expect(rule('@example.com')).toBe('Please enter a valid email address')
      expect(rule('test@')).toBe('Please enter a valid email address')
    })

    it('should return true for empty strings (optional)', () => {
      const rule = validationRules.email()

      expect(rule('')).toBe(true)
    })

    it('should use custom error message', () => {
      const rule = validationRules.email('Bad email!')

      expect(rule('invalid')).toBe('Bad email!')
    })
  })
})

describe('useProfileValidation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initialization', () => {
    it('should initialize with default empty form data', () => {
      const { formData, errors } = useProfileValidation()

      expect(formData.bio).toBe('')
      expect(formData.location).toBe('')
      expect(formData.website).toBe('')
      expect(formData.company).toBe('')
      expect(formData.avatar_url).toBe('')

      expect(errors.bio).toBe('')
      expect(errors.location).toBe('')
      expect(errors.website).toBe('')
      expect(errors.company).toBe('')
      expect(errors.avatar_url).toBe('')
    })

    it('should initialize with provided data', () => {
      const initialData: Partial<ProfileForm> = {
        bio: 'Test bio',
        location: 'Test location',
        website: 'https://example.com',
      }

      const { formData } = useProfileValidation(initialData)

      expect(formData.bio).toBe('Test bio')
      expect(formData.location).toBe('Test location')
      expect(formData.website).toBe('https://example.com')
      expect(formData.company).toBe('')
      expect(formData.avatar_url).toBe('')
    })
  })

  describe('computed properties', () => {
    it('should compute isFormValid correctly', () => {
      const { isFormValid, errors } = useProfileValidation()

      expect(isFormValid.value).toBe(true)

      // Add an error
      errors.bio = 'Bio is required'
      expect(isFormValid.value).toBe(false)

      // Clear error
      errors.bio = ''
      expect(isFormValid.value).toBe(true)
    })

    it('should compute hasErrors correctly', () => {
      const { hasErrors, errors } = useProfileValidation()

      expect(hasErrors.value).toBe(false)

      // Add an error
      errors.location = 'Invalid location'
      expect(hasErrors.value).toBe(true)

      // Clear error
      errors.location = ''
      expect(hasErrors.value).toBe(false)
    })
  })

  describe('field validation', () => {
    it('should validate bio field', () => {
      const { validateField, formData, errors } = useProfileValidation()

      // Valid bio
      formData.bio = 'This is a valid bio'
      expect(validateField('bio')).toBe(true)
      expect(errors.bio).toBe('')

      // Bio too long
      formData.bio = 'x'.repeat(501)
      expect(validateField('bio')).toBe(false)
      expect(errors.bio).toBe('Bio must be 500 characters or less')
    })

    it('should validate location field', () => {
      const { validateField, formData, errors } = useProfileValidation()

      // Valid location
      formData.location = 'New York'
      expect(validateField('location')).toBe(true)
      expect(errors.location).toBe('')

      // Location too long
      formData.location = 'x'.repeat(101)
      expect(validateField('location')).toBe(false)
      expect(errors.location).toBe('Location must be 100 characters or less')
    })

    it('should validate website field', () => {
      const { validateField, formData, errors } = useProfileValidation()

      // Valid website
      formData.website = 'https://example.com'
      expect(validateField('website')).toBe(true)
      expect(errors.website).toBe('')

      // Invalid website
      formData.website = 'not-a-url'
      expect(validateField('website')).toBe(false)
      expect(errors.website).toBe('Please enter a valid website URL')

      // Website too long
      formData.website = 'https://' + 'x'.repeat(200)
      expect(validateField('website')).toBe(false)
      expect(errors.website).toBe('Website URL must be 200 characters or less')
    })

    it('should validate company field', () => {
      const { validateField, formData, errors } = useProfileValidation()

      // Valid company
      formData.company = 'ACME Corp'
      expect(validateField('company')).toBe(true)
      expect(errors.company).toBe('')

      // Company too long
      formData.company = 'x'.repeat(101)
      expect(validateField('company')).toBe(false)
      expect(errors.company).toBe('Company name must be 100 characters or less')
    })

    it('should handle unknown fields', () => {
      const { validateField } = useProfileValidation()

      // Should return true for unknown fields
      expect(validateField('unknown_field' as any)).toBe(true)
    })
  })

  describe('form validation', () => {
    it('should validate entire form', () => {
      const { validateForm, formData } = useProfileValidation()

      // Valid form
      formData.bio = 'Valid bio'
      formData.location = 'Valid location'
      formData.website = 'https://example.com'
      formData.company = 'Valid company'

      expect(validateForm()).toBe(true)

      // Invalid form
      formData.bio = 'x'.repeat(501)
      expect(validateForm()).toBe(false)
    })

    it('should set errors for all invalid fields', () => {
      const { validateForm, formData, errors } = useProfileValidation()

      formData.bio = 'x'.repeat(501)
      formData.location = 'x'.repeat(101)
      formData.website = 'invalid-url'

      expect(validateForm()).toBe(false)
      expect(errors.bio).toBe('Bio must be 500 characters or less')
      expect(errors.location).toBe('Location must be 100 characters or less')
      expect(errors.website).toBe('Please enter a valid website URL')
    })
  })

  describe('data management', () => {
    it('should load data correctly', () => {
      const { loadData, formData } = useProfileValidation()

      const newData: Partial<ProfileForm> = {
        bio: 'New bio',
        location: 'New location',
        website: 'https://newsite.com',
      }

      loadData(newData)

      expect(formData.bio).toBe('New bio')
      expect(formData.location).toBe('New location')
      expect(formData.website).toBe('https://newsite.com')
      expect(formData.company).toBe('') // Should remain empty
    })

    it('should reset form correctly', () => {
      const { resetForm, formData, errors } = useProfileValidation()

      // Set some data and errors
      formData.bio = 'Some bio'
      formData.location = 'Some location'
      errors.bio = 'Some error'

      resetForm()

      expect(formData.bio).toBe('')
      expect(formData.location).toBe('')
      expect(formData.website).toBe('')
      expect(formData.company).toBe('')
      expect(formData.avatar_url).toBe('')

      expect(errors.bio).toBe('')
      expect(errors.location).toBe('')
      expect(errors.website).toBe('')
      expect(errors.company).toBe('')
      expect(errors.avatar_url).toBe('')
    })

    it('should get clean data correctly', () => {
      const { getCleanData, formData } = useProfileValidation()

      formData.bio = 'Valid bio'
      formData.location = ''
      formData.website = 'https://example.com'
      formData.company = ''
      formData.avatar_url = ''

      const cleanData = getCleanData()

      expect(cleanData).toEqual({
        bio: 'Valid bio',
        website: 'https://example.com',
      })
    })
  })

  describe('debounced validation', () => {
    it('should provide debounced field validation', () => {
      const { debouncedValidateField } = useProfileValidation()

      expect(debouncedValidateField).toBeDefined()
      expect(typeof debouncedValidateField).toBe('function')

      // Should be callable
      debouncedValidateField('bio')
      expect(debouncedValidateField).toHaveBeenCalledWith('bio')
    })
  })
})

describe('useSettingsValidation', () => {
  it('should initialize with default empty form data', () => {
    const { formData, errors } = useSettingsValidation()

    expect(formData.theme).toBe('')
    expect(formData.language).toBe('')
    expect(formData.timezone).toBe('')
    expect(formData.email_notifications).toBe(false)
    expect(formData.push_notifications).toBe(false)
    expect(formData.profile_visibility).toBe('public')
    expect(formData.show_email).toBe(false)
    expect(formData.show_activity).toBe(false)

    expect(errors.theme).toBe('')
    expect(errors.language).toBe('')
    expect(errors.timezone).toBe('')
  })

  it('should initialize with provided data', () => {
    const initialData: Partial<SettingsForm> = {
      theme: 'dark',
      language: 'es',
      email_notifications: true,
    }

    const { formData } = useSettingsValidation(initialData)

    expect(formData.theme).toBe('dark')
    expect(formData.language).toBe('es')
    expect(formData.email_notifications).toBe(true)
    expect(formData.timezone).toBe('') // Should remain default
  })

  it('should validate settings fields', () => {
    const { validateField, formData } = useSettingsValidation()

    // Settings validation rules are minimal - should mostly pass
    formData.theme = 'dark'
    expect(validateField('theme')).toBe(true)

    formData.language = 'en'
    expect(validateField('language')).toBe(true)

    formData.timezone = 'UTC'
    expect(validateField('timezone')).toBe(true)
  })
})

describe('useAvatarValidation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with default state', () => {
    const { selectedFile, previewUrl, error, isValid } = useAvatarValidation()

    expect(selectedFile.value).toBeNull()
    expect(previewUrl.value).toBeNull()
    expect(error.value).toBeNull()
    expect(isValid.value).toBe(true)
  })

  it('should select valid image file', () => {
    const { selectFile, selectedFile, isValid, error } = useAvatarValidation()

    const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    
    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test-url')

    selectFile(validFile)

    expect(selectedFile.value).toBe(validFile)
    expect(isValid.value).toBe(true)
    expect(error.value).toBeNull()
  })

  it('should reject invalid file type', () => {
    const { selectFile, selectedFile, isValid, error } = useAvatarValidation()

    const invalidFile = new File([''], 'test.pdf', { type: 'application/pdf' })
    
    selectFile(invalidFile)

    expect(selectedFile.value).toBeNull()
    expect(isValid.value).toBe(false)
    expect(error.value).toContain('File type must be one of')
  })

  it('should reject oversized file', () => {
    const { selectFile, selectedFile, isValid, error } = useAvatarValidation()

    // Create a large file (6MB)
    const largeFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' })
    
    selectFile(largeFile)

    expect(selectedFile.value).toBeNull()
    expect(isValid.value).toBe(false)
    expect(error.value).toContain('File size must be less than')
  })

  it('should clear selection', () => {
    const { selectFile, clearSelection, selectedFile, previewUrl, error, isValid } = useAvatarValidation()

    // Mock URL.createObjectURL and revokeObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test-url')
    global.URL.revokeObjectURL = vi.fn()

    // First select a file
    const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    selectFile(validFile)

    expect(selectedFile.value).toBe(validFile)

    // Then clear selection
    clearSelection()

    expect(selectedFile.value).toBeNull()
    expect(previewUrl.value).toBeNull()
    expect(error.value).toBeNull()
    expect(isValid.value).toBe(true)
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url')
  })
})
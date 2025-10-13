/**
 * Profile Validation Composable
 * Reusable validation logic for profile forms
 */
import { computed, reactive, ref } from 'vue'
import { useDebounce, DEBOUNCE_DELAYS } from '@/composables/useDebounce'
import type { ProfileForm, SettingsForm } from '../types/profile.types'

// Internal form interfaces with string types for v-model compatibility
interface InternalProfileForm {
  bio: string
  location: string
  website: string
  company: string
  avatar_url: string
}

// Validation rule types
type ValidationRule<T = any> = (value: T) => boolean | string

interface ProfileValidationRules {
  bio?: ValidationRule<string>[]
  location?: ValidationRule<string>[]
  website?: ValidationRule<string>[]
  company?: ValidationRule<string>[]
  avatar_url?: ValidationRule<string>[]
}

interface SettingsValidationRules {
  theme?: ValidationRule<string>[]
  language?: ValidationRule<string>[]
  timezone?: ValidationRule<string>[]
}

// Common validation functions
export const validationRules = {
  // Required field
  required: (message = 'This field is required'): ValidationRule<any> => {
    return (value: any) => {
      if (!value || (typeof value === 'string' && !value.trim())) {
        return message
      }
      return true
    }
  },

  // Minimum length
  minLength: (min: number, message?: string): ValidationRule<string> => {
    return (value: string) => {
      if (!value) return true // Optional field
      if (value.length < min) {
        return message || `Must be at least ${min} characters`
      }
      return true
    }
  },

  // Maximum length
  maxLength: (max: number, message?: string): ValidationRule<string> => {
    return (value: string) => {
      if (!value) return true // Optional field
      if (value.length > max) {
        return message || `Must be ${max} characters or less`
      }
      return true
    }
  },

  // URL validation
  url: (message = 'Please enter a valid URL'): ValidationRule<string> => {
    return (value: string) => {
      if (!value) return true // Optional field

      try {
        // Add protocol if missing
        const urlToTest =
          value.startsWith('http://') || value.startsWith('https://') ? value : `https://${value}`

        const url = new URL(urlToTest)
        return url.protocol === 'http:' || url.protocol === 'https:' ? true : message
      } catch {
        return message
      }
    }
  },

  // File size validation (in MB)
  fileSize: (maxMB: number, message?: string): ValidationRule<File> => {
    return (file: File) => {
      if (!file) return true
      const maxBytes = maxMB * 1024 * 1024
      if (file.size > maxBytes) {
        return message || `File size must be less than ${maxMB}MB`
      }
      return true
    }
  },

  // File type validation
  fileType: (allowedTypes: string[], message?: string): ValidationRule<File> => {
    return (file: File) => {
      if (!file) return true
      if (!allowedTypes.includes(file.type)) {
        return message || `File type must be one of: ${allowedTypes.join(', ')}`
      }
      return true
    }
  },

  // Email validation (if needed)
  email: (message = 'Please enter a valid email address'): ValidationRule<string> => {
    return (value: string) => {
      if (!value) return true
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value) ? true : message
    }
  },
}

/**
 * Profile Form Validation Composable
 */
export function useProfileValidation(initialData?: Partial<ProfileForm>) {
  // Form data
  const formData = reactive<InternalProfileForm>({
    bio: initialData?.bio || '',
    location: initialData?.location || '',
    website: initialData?.website || '',
    company: initialData?.company || '',
    avatar_url: initialData?.avatar_url || '',
  })

  // Validation errors
  const errors = reactive<Record<keyof InternalProfileForm, string>>({
    bio: '',
    location: '',
    website: '',
    company: '',
    avatar_url: '',
  })

  // Validation rules for profile form with personality! 🎭
  const rules: ProfileValidationRules = {
    bio: [
      validationRules.maxLength(
        500,
        "📝 Your bio is longer than a Tolkien novel! Let's trim it to 500 characters - save some mystery for conversation!",
      ),
    ],
    location: [
      validationRules.maxLength(
        100,
        "🗺️ That location description could span continents! Let's keep it under 100 characters.",
      ),
    ],
    website: [
      validationRules.url(
        "🔗 That URL doesn't look quite right. Try something like 'https://example.com' (don't forget the https!)",
      ),
      validationRules.maxLength(
        200,
        "🌐 That's one looong URL! Let's trim it to under 200 characters.",
      ),
    ],
    company: [
      validationRules.maxLength(
        100,
        "🏢 That company name could be a business plan! Let's keep it under 100 characters.",
      ),
    ],
  }

  // Validate a single field
  const validateField = (field: keyof InternalProfileForm): boolean => {
    const fieldRules = (rules as any)[field]
    if (!fieldRules) return true

    const value = formData[field]

    for (const rule of fieldRules) {
      const result = rule(value as any)
      if (result !== true) {
        errors[field] = typeof result === 'string' ? result : 'Validation failed'
        return false
      }
    }

    errors[field] = ''
    return true
  }

  // Validate all fields
  const validateForm = (): boolean => {
    let isValid = true

    for (const field of Object.keys(rules) as (keyof InternalProfileForm)[]) {
      if (!validateField(field)) {
        isValid = false
      }
    }

    return isValid
  }

  // Debounced field validation for real-time feedback
  const debouncedValidateField = useDebounce((field: keyof InternalProfileForm) => {
    validateField(field)
  }, DEBOUNCE_DELAYS.VALIDATION)

  // Reset form
  const resetForm = () => {
    Object.assign(formData, {
      bio: '',
      location: '',
      website: '',
      company: '',
      avatar_url: '',
    })

    // Clear errors
    for (const key of Object.keys(errors) as (keyof InternalProfileForm)[]) {
      errors[key] = ''
    }
  }

  // Load initial data
  const loadData = (data: Partial<ProfileForm>) => {
    Object.assign(formData, {
      bio: data.bio || '',
      location: data.location || '',
      website: data.website || '',
      company: data.company || '',
      avatar_url: data.avatar_url || '',
    })
  }

  // Get clean form data (remove empty strings)
  const getCleanData = (): ProfileForm => {
    const cleanData: ProfileForm = {}

    for (const [key, value] of Object.entries(formData)) {
      if (value !== '' && value !== null && value !== undefined) {
        ;(cleanData as any)[key] = value || null
      }
    }

    return cleanData
  }

  // Computed properties
  const isFormValid = computed(() => {
    return Object.values(errors).every((error) => error === '')
  })

  const hasErrors = computed(() => {
    return Object.values(errors).some((error) => error !== '')
  })

  return {
    formData,
    errors,
    isFormValid,
    hasErrors,
    validateField,
    validateForm,
    debouncedValidateField,
    resetForm,
    loadData,
    getCleanData,
  }
}

/**
 * Settings Form Validation Composable
 */
export function useSettingsValidation(initialData?: Partial<SettingsForm>) {
  // Form data
  const formData = reactive<SettingsForm>({
    theme: initialData?.theme || 'auto',
    language: initialData?.language || 'en',
    timezone: initialData?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone,
    email_notifications: initialData?.email_notifications ?? true,
    push_notifications: initialData?.push_notifications ?? true,
    profile_visibility: initialData?.profile_visibility || 'public',
    show_email: initialData?.show_email ?? false,
    show_activity: initialData?.show_activity ?? true,
    metadata: initialData?.metadata || null,
  })

  // Validation errors
  const errors = reactive<Record<string, string>>({
    theme: '',
    language: '',
    timezone: '',
  })

  // Validation rules for settings form with personality! ⚙️
  const rules: SettingsValidationRules = {
    theme: [
      (value: string) => ['light', 'dark', 'auto'].includes(value) || '🌈 That theme option doesn\'t exist in our universe. Stick to Light, Dark, or Auto!',
    ],
    language: [validationRules.required('🎭 Please pick a language - even if you\'re the strong, silent type!')],
    timezone: [validationRules.required('⌚ Time is precious! Please select your timezone so we can sync up.')],
  }

  // Validate a single field
  const validateField = (field: string): boolean => {
    const fieldRules = (rules as any)[field]
    if (!fieldRules) return true

    const value = (formData as any)[field]

    for (const rule of fieldRules) {
      const result = rule(value)
      if (result !== true) {
        errors[field] = result
        return false
      }
    }

    errors[field] = ''
    return true
  }

  // Validate form
  const validateForm = (): boolean => {
    let isValid = true

    for (const field of Object.keys(rules)) {
      if (!validateField(field)) {
        isValid = false
      }
    }

    return isValid
  }

  // Load initial data
  const loadData = (data: Partial<SettingsForm>) => {
    Object.assign(formData, data)
  }

  // Computed properties
  const isFormValid = computed(() => {
    return Object.values(errors).every((error) => error === '')
  })

  const hasErrors = computed(() => {
    return Object.values(errors).some((error) => error !== '')
  })

  return {
    formData,
    errors,
    isFormValid,
    hasErrors,
    validateField,
    validateForm,
    loadData,
  }
}

/**
 * Avatar Upload Validation Composable
 */
export function useAvatarValidation() {
  const selectedFile = ref<File | null>(null)
  const previewUrl = ref<string | null>(null)
  const error = ref<string>('')

  // Validation rules for avatar with personality! 📸
  const avatarRules = [
    validationRules.fileSize(
      5,
      '📸 Whoa! That image is bigger than a movie poster! Please choose something under 5MB.',
    ),
    validationRules.fileType(
      ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
      "🎨 That file type isn't quite right. We love JPEG, PNG, WebP, or GIF images!",
    ),
  ]

  // Validate avatar file
  const validateAvatar = (file: File): boolean => {
    for (const rule of avatarRules) {
      const result = rule(file)
      if (result !== true) {
        error.value = typeof result === 'string' ? result : 'Validation failed'
        return false
      }
    }

    error.value = ''
    return true
  }

  // Debounced avatar validation for file size checks
  const debouncedValidateAvatar = useDebounce((file: File) => {
    validateAvatar(file)
  }, DEBOUNCE_DELAYS.FILE_UPLOAD)

  // Handle file selection
  const selectFile = (file: File | null) => {
    if (!file) {
      selectedFile.value = null
      previewUrl.value = null
      error.value = ''
      return
    }

    if (validateAvatar(file)) {
      selectedFile.value = file

      // Create preview URL
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
      }
      previewUrl.value = URL.createObjectURL(file)
    } else {
      selectedFile.value = null
      previewUrl.value = null
    }
  }

  // Clear selection
  const clearSelection = () => {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
    }
    selectedFile.value = null
    previewUrl.value = null
    error.value = ''
  }

  return {
    selectedFile,
    previewUrl,
    error,
    selectFile,
    clearSelection,
    validateAvatar,
    debouncedValidateAvatar,
    isValid: computed(() => error.value === ''),
  }
}

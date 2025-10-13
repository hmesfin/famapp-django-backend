/**
 * Enhanced Profile Form Composable
 * Consolidates common form patterns for profile and settings forms
 */
import { ref, computed, reactive, nextTick } from 'vue'
import {
  useProfileValidation,
  useSettingsValidation,
  useAvatarValidation,
} from './useProfileValidation'
import { useToastStore } from '@/shared/stores/toastStore'
import { ERROR_MESSAGES, SUCCESS_MESSAGES, FIELD_NAMES } from '../constants/index'
import type { ProfileForm, SettingsForm } from '../types/profile.types'

export interface FormSubmissionOptions {
  successMessage?: string
  errorMessage?: string
  onSuccess?: () => void | Promise<void>
  onError?: (error: any) => void
  resetOnSuccess?: boolean
  redirectOnSuccess?: boolean | string
}

/**
 * Enhanced Profile Form Composable
 * Consolidates form state, validation, submission, and common patterns
 */
export function useProfileForm(initialData?: Partial<ProfileForm>) {
  const toastStore = useToastStore()
  const validation = useProfileValidation(initialData)

  // Form state management
  const saving = ref(false)
  const originalData = ref<ProfileForm>({})
  const initialized = ref(false)

  // Change detection
  const hasChanges = computed(() => {
    if (!initialized.value) return false

    const current = validation.getCleanData()
    const original = originalData.value

    return Object.keys({ ...current, ...original }).some((key) => {
      const currentValue = (current as any)[key] || ''
      const originalValue = (original as any)[key] || ''
      return currentValue !== originalValue
    })
  })

  // Initialize form with data
  const initializeForm = (data: Partial<ProfileForm>) => {
    validation.loadData(data)
    originalData.value = validation.getCleanData()
    initialized.value = true
  }

  // Reset form to original state
  const resetForm = () => {
    if (originalData.value) {
      validation.loadData(originalData.value)
    }
  }

  // Form submission handler
  const handleSubmit = async (
    submitFunction: (data: ProfileForm) => Promise<any>,
    options: FormSubmissionOptions = {},
  ) => {
    // Validate form
    if (!validation.validateForm()) {
      const firstErrorField = Object.keys(validation.errors).find(
        (field) => validation.errors[field as keyof ProfileForm] !== '',
      )
      if (firstErrorField) {
        const friendlyFieldName =
          FIELD_NAMES[firstErrorField as keyof typeof FIELD_NAMES] || firstErrorField
        toastStore.error(`🔍 ${friendlyFieldName} needs some attention! Check the field below.`)
      } else {
        toastStore.error(ERROR_MESSAGES.VALIDATION_ERROR)
      }
      return false
    }

    saving.value = true

    try {
      const formData = validation.getCleanData()
      const result = await submitFunction(formData)

      // Update original data to reflect successful save
      if (options.resetOnSuccess !== false) {
        originalData.value = { ...formData }
      }

      // Show success message
      if (options.successMessage) {
        toastStore.success(options.successMessage)
      }

      // Call success callback
      if (options.onSuccess) {
        await options.onSuccess()
      }

      return result
    } catch (error: any) {
      console.error('Form submission error:', error)

      // Show error message with personality
      const errorMessage = options.errorMessage || ERROR_MESSAGES.PROFILE_SAVE_FAILED
      toastStore.error(errorMessage)

      // Call error callback
      if (options.onError) {
        options.onError(error)
      }

      return false
    } finally {
      saving.value = false
    }
  }

  return {
    // Form data and validation
    formData: validation.formData,
    errors: validation.errors,
    isFormValid: validation.isFormValid,
    hasErrors: validation.hasErrors,

    // Form state
    saving,
    hasChanges,
    initialized,

    // Form actions
    initializeForm,
    resetForm,
    handleSubmit,
    validateField: validation.validateField,
    validateForm: validation.validateForm,

    // Utilities
    getCleanData: validation.getCleanData,
  }
}

/**
 * Enhanced Settings Form Composable
 * Specialized version for settings forms with individual field updates
 */
export function useSettingsForm(initialData?: Partial<SettingsForm>) {
  const toastStore = useToastStore()
  const validation = useSettingsValidation(initialData)

  // Form state management
  const saving = ref(false)
  const fieldSaving = reactive<Record<string, boolean>>({})

  // Initialize form with data
  const initializeForm = (data: Partial<SettingsForm>) => {
    validation.loadData(data)
  }

  // Handle individual field updates (common pattern in settings)
  const handleFieldUpdate = async <K extends keyof SettingsForm>(
    field: K,
    value: SettingsForm[K],
    updateFunction: (data: Partial<SettingsForm>) => Promise<any>,
    options: Omit<FormSubmissionOptions, 'resetOnSuccess'> = {},
  ) => {
    // Validate the field
    if (!validation.validateField(field as string)) {
      const friendlyFieldName = FIELD_NAMES[field as keyof typeof FIELD_NAMES] || field
      const errorMessage = validation.errors[field as string]
      toastStore.error(`🔍 ${friendlyFieldName}: ${errorMessage}`)
      return false
    }

    // Set field saving state
    fieldSaving[field as string] = true
    saving.value = true

    try {
      // Update form data
      ;(validation.formData as any)[field] = value

      // Call update function with just the changed field
      const updateData = { [field]: value } as Partial<SettingsForm>
      const result = await updateFunction(updateData)

      // Show success message if provided
      if (options.successMessage) {
        toastStore.success(options.successMessage)
      }

      // Call success callback
      if (options.onSuccess) {
        await options.onSuccess()
      }

      return result
    } catch (error: any) {
      console.error(`Failed to update ${field}:`, error)

      // Revert the form data
      ;(validation.formData as any)[field] = (validation.formData as any)[field]

      // Show error message with personality
      const errorMessage = options.errorMessage || ERROR_MESSAGES.SETTINGS_SAVE_FAILED
      toastStore.error(errorMessage)

      // Call error callback
      if (options.onError) {
        options.onError(error)
      }

      return false
    } finally {
      fieldSaving[field as string] = false
      saving.value = false
    }
  }

  // Batch update multiple fields
  const handleBatchUpdate = async (
    updates: Partial<SettingsForm>,
    updateFunction: (data: Partial<SettingsForm>) => Promise<any>,
    options: FormSubmissionOptions = {},
  ) => {
    saving.value = true

    try {
      // Update form data
      Object.assign(validation.formData, updates)

      // Validate affected fields
      const fieldsToValidate = Object.keys(updates)
      const hasValidationErrors = fieldsToValidate.some((field) => !validation.validateField(field))

      if (hasValidationErrors) {
        toastStore.error(ERROR_MESSAGES.VALIDATION_ERROR)
        return false
      }

      // Call update function
      const result = await updateFunction(updates)

      // Show success message
      if (options.successMessage) {
        toastStore.success(options.successMessage)
      }

      // Call success callback
      if (options.onSuccess) {
        await options.onSuccess()
      }

      return result
    } catch (error: any) {
      console.error('Batch update error:', error)

      // Show error message with personality
      const errorMessage = options.errorMessage || ERROR_MESSAGES.SETTINGS_SAVE_FAILED
      toastStore.error(errorMessage)

      // Call error callback
      if (options.onError) {
        options.onError(error)
      }

      return false
    } finally {
      saving.value = false
    }
  }

  // Check if a specific field is saving
  const isFieldSaving = (field: string) => fieldSaving[field] || false

  return {
    // Form data and validation
    formData: validation.formData,
    errors: validation.errors,
    isFormValid: validation.isFormValid,
    hasErrors: validation.hasErrors,

    // Form state
    saving,
    fieldSaving,

    // Form actions
    initializeForm,
    handleFieldUpdate,
    handleBatchUpdate,
    isFieldSaving,
    validateField: validation.validateField,
    validateForm: validation.validateForm,
  }
}

/**
 * Enhanced Avatar Upload Composable
 * Consolidates avatar upload logic with form integration
 */
export function useAvatarForm() {
  const toastStore = useToastStore()
  const avatarValidation = useAvatarValidation()

  const uploading = ref(false)
  const uploadProgress = ref(0)

  // Handle file upload with validation and error handling
  const handleAvatarUpload = async (
    file: File,
    uploadFunction: (file: File) => Promise<{ avatar_url: string }>,
    options: FormSubmissionOptions = {},
  ) => {
    // Select and validate file
    avatarValidation.selectFile(file)

    if (!avatarValidation.isValid.value) {
      toastStore.error(avatarValidation.error.value)
      return false
    }

    uploading.value = true
    uploadProgress.value = 0

    try {
      // Simulate progress for better UX (real progress would come from upload function)
      const progressInterval = setInterval(() => {
        if (uploadProgress.value < 90) {
          uploadProgress.value += Math.random() * 20
        }
      }, 100)

      const result = await uploadFunction(file)

      // Complete progress
      clearInterval(progressInterval)
      uploadProgress.value = 100

      // Show success message with personality
      const successMessage = options.successMessage || SUCCESS_MESSAGES.AVATAR_UPLOADED
      toastStore.success(successMessage)

      // Call success callback
      if (options.onSuccess) {
        await options.onSuccess()
      }

      return result
    } catch (error: any) {
      console.error('Avatar upload error:', error)

      // Show error message with personality
      const errorMessage = options.errorMessage || ERROR_MESSAGES.AVATAR_UPLOAD_FAILED
      toastStore.error(errorMessage)

      // Call error callback
      if (options.onError) {
        options.onError(error)
      }

      return false
    } finally {
      uploading.value = false
      // Reset progress after a short delay to show completion
      setTimeout(() => {
        uploadProgress.value = 0
      }, 1000)
    }
  }

  // Trigger file input
  const triggerFileUpload = (fileInputRef: { click: () => void }) => {
    fileInputRef.click()
  }

  // Handle file input change
  const handleFileInputChange = async (
    event: Event,
    uploadFunction: (file: File) => Promise<{ avatar_url: string }>,
    options: FormSubmissionOptions = {},
  ) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]

    if (file) {
      const result = await handleAvatarUpload(file, uploadFunction, options)
      target.value = '' // Clear input
      return result
    }

    return false
  }

  return {
    // Validation state
    selectedFile: avatarValidation.selectedFile,
    previewUrl: avatarValidation.previewUrl,
    error: avatarValidation.error,
    isValid: avatarValidation.isValid,

    // Upload state
    uploading,
    uploadProgress,

    // Actions
    handleAvatarUpload,
    handleFileInputChange,
    triggerFileUpload,
    clearSelection: avatarValidation.clearSelection,
  }
}

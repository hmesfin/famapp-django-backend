/**
 * Invitation Form Store - Focused on form state and submission
 * Ham Dog & TC's specialized store for invitation form operations!
 */
import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import invitationService from '../services/invitationService'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'
import type {
  InvitationCreateForm,
  InvitationCreateResponse,
  BulkInvitationForm,
  BulkInvitationResult,
  SystemRole,
} from '../types/invitation.types'

// Form validation interface
interface FormErrors {
  first_name?: string
  last_name?: string
  email?: string
  role?: string
  organization_name?: string
  message?: string
  general?: string
}

// Single invitation form state
interface SingleInvitationForm {
  email: string
  first_name: string
  last_name: string
  role: SystemRole
  organization_name: string
  message: string
}

export const useInvitationFormStore = defineStore('invitationForm', () => {
  const toastStore = useToastStore()
  const authStore = useAuthStore()

  // State - form management
  const loading = ref(false)
  const submitting = ref(false)
  const error = ref<string | null>(null)
  const isBulkMode = ref(false)

  // Single invitation form
  const singleForm = reactive<SingleInvitationForm>({
    email: '',
    first_name: '',
    last_name: '',
    role: 'member',
    organization_name: '',
    message: '',
  })

  // Form validation errors
  const errors = reactive<FormErrors>({})

  // Bulk invitation form (placeholder for future CSV implementation)
  const bulkForm = reactive<BulkInvitationForm>({
    emails: [],
    role: 'member',
    organization_name: '',
    message: '',
  })

  // Computed - form validation
  const isFormValid = computed(() => {
    if (isBulkMode.value) {
      return bulkForm.emails.length > 0 && bulkForm.role
    } else {
      return (
        singleForm.email &&
        singleForm.first_name &&
        singleForm.last_name &&
        singleForm.role &&
        validateEmail(singleForm.email)
      )
    }
  })

  const hasErrors = computed(() => {
    return Object.keys(errors).some((key) => errors[key as keyof FormErrors])
  })

  // Available roles for current user
  const availableRoles = computed(() => {
    const user = authStore.user
    const userRoles = user?.roles || []
    const roles: SystemRole[] = ['member', 'viewer']

    if (userRoles.includes('admin') || userRoles.includes('manager')) {
      roles.push('manager')
    }

    if (userRoles.includes('admin')) {
      roles.push('admin')
    }

    return roles
  })

  // Permission to send invitations
  const canSendInvitations = computed(() => {
    const user = authStore.user
    const userRoles = user?.roles || []
    return userRoles.includes('admin') || userRoles.includes('manager')
  })

  // Validation helpers
  function validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  function validateSingleForm(): boolean {
    clearErrors()
    let isValid = true

    // Required field validation
    if (!singleForm.first_name.trim()) {
      errors.first_name = 'First name is required'
      isValid = false
    }

    if (!singleForm.last_name.trim()) {
      errors.last_name = 'Last name is required'
      isValid = false
    }

    if (!singleForm.email.trim()) {
      errors.email = 'Email is required'
      isValid = false
    } else if (!validateEmail(singleForm.email)) {
      errors.email = 'Please enter a valid email address'
      isValid = false
    }

    if (!singleForm.role) {
      errors.role = 'Role is required'
      isValid = false
    }

    return isValid
  }

  function validateBulkForm(): boolean {
    clearErrors()
    let isValid = true

    if (bulkForm.emails.length === 0) {
      errors.general = 'At least one email is required for bulk invitations'
      isValid = false
    }

    if (!bulkForm.role) {
      errors.role = 'Role is required'
      isValid = false
    }

    return isValid
  }

  // Form actions
  function clearErrors() {
    Object.keys(errors).forEach((key) => {
      delete errors[key as keyof FormErrors]
    })
    error.value = null
  }

  function resetSingleForm() {
    singleForm.email = ''
    singleForm.first_name = ''
    singleForm.last_name = ''
    singleForm.role = 'member'
    singleForm.organization_name = ''
    singleForm.message = ''
    clearErrors()
  }

  function resetBulkForm() {
    bulkForm.emails = []
    bulkForm.role = 'member'
    bulkForm.organization_name = ''
    bulkForm.message = ''
    clearErrors()
  }

  function resetForms() {
    resetSingleForm()
    resetBulkForm()
    isBulkMode.value = false
  }

  function toggleMode(mode: 'single' | 'bulk') {
    isBulkMode.value = mode === 'bulk'
    clearErrors()
  }

  // Submission actions
  async function submitSingleInvitation(): Promise<InvitationCreateResponse> {
    if (!validateSingleForm()) {
      return Promise.reject(new Error('Form validation failed'))
    }

    submitting.value = true
    error.value = null

    try {
      // Check if email already has pending invitation
      const emailExists = await invitationService.checkEmailExists(singleForm.email)
      if (emailExists) {
        errors.email = 'This email already has a pending invitation'
        throw new Error('Email already has pending invitation')
      }

      // Create invitation data
      const invitationData: InvitationCreateForm = {
        email: singleForm.email,
        first_name: singleForm.first_name,
        last_name: singleForm.last_name,
        role: singleForm.role,
        organization_name: singleForm.organization_name || undefined,
        message: singleForm.message || undefined,
      }

      const response = await invitationService.createInvitation(invitationData)
      toastStore.success('Invitation sent successfully!')

      // Reset form on successful submission
      resetSingleForm()

      return response
    } catch (err: any) {
      let errorMessage = 'Failed to send invitation'

      if (err.response?.data) {
        const data = err.response.data

        if (data.email) {
          errors.email = Array.isArray(data.email) ? data.email[0] : data.email
          errorMessage = errors.email || errorMessage
        } else if (data.first_name) {
          errors.first_name = Array.isArray(data.first_name) ? data.first_name[0] : data.first_name
        } else if (data.last_name) {
          errors.last_name = Array.isArray(data.last_name) ? data.last_name[0] : data.last_name
        } else if (data.non_field_errors) {
          errorMessage = Array.isArray(data.non_field_errors)
            ? data.non_field_errors[0]
            : data.non_field_errors
        } else if (data.detail) {
          errorMessage = data.detail
        }
      }

      error.value = errorMessage
      if (!errors.email && !errors.first_name && !errors.last_name) {
        toastStore.error(errorMessage)
      }

      throw new Error(errorMessage)
    } finally {
      submitting.value = false
    }
  }

  async function submitBulkInvitations(): Promise<BulkInvitationResult> {
    if (!validateBulkForm()) {
      return Promise.reject(new Error('Form validation failed'))
    }

    submitting.value = true
    error.value = null

    try {
      const result = await invitationService.createBulkInvitations(bulkForm)

      if (result.successful.length > 0) {
        toastStore.success(`Successfully sent ${result.successful.length} invitation(s)`)
      }

      if (result.failed.length > 0) {
        const failedEmails = result.failed.map((f) => f.email).join(', ')
        toastStore.warning(`Failed to send invitations to: ${failedEmails}`)
      }

      // Reset form on successful submission
      resetBulkForm()

      return result
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to send bulk invitations'
      error.value = errorMessage
      toastStore.error(errorMessage)
      throw err
    } finally {
      submitting.value = false
    }
  }

  async function checkEmailAvailability(email: string): Promise<boolean> {
    if (!email || !validateEmail(email)) {
      return true // Don't check invalid emails
    }

    try {
      loading.value = true
      const exists = await invitationService.checkEmailExists(email)
      return !exists
    } catch {
      return true // Assume available on error
    } finally {
      loading.value = false
    }
  }

  // Utility functions for form preview
  function getFormPreview() {
    if (isBulkMode.value) {
      return {
        mode: 'bulk',
        count: bulkForm.emails.length,
        role: bulkForm.role,
        organization: bulkForm.organization_name,
        hasMessage: !!bulkForm.message,
      }
    } else {
      return {
        mode: 'single',
        fullName: `${singleForm.first_name} ${singleForm.last_name}`.trim(),
        email: singleForm.email,
        role: singleForm.role,
        organization: singleForm.organization_name,
        hasMessage: !!singleForm.message,
      }
    }
  }

  // Reset store
  function resetStore() {
    resetForms()
    loading.value = false
    submitting.value = false
    error.value = null
  }

  return {
    // State
    loading,
    submitting,
    error,
    isBulkMode,
    singleForm,
    bulkForm,
    errors,

    // Computed
    isFormValid,
    hasErrors,
    availableRoles,
    canSendInvitations,

    // Validation
    validateEmail,
    validateSingleForm,
    validateBulkForm,

    // Form Management
    clearErrors,
    resetSingleForm,
    resetBulkForm,
    resetForms,
    toggleMode,

    // Submission
    submitSingleInvitation,
    submitBulkInvitations,
    checkEmailAvailability,

    // Utilities
    getFormPreview,
    resetStore,
  }
})

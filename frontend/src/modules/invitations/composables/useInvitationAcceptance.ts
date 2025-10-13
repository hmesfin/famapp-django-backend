/**
 * Invitation Acceptance Composable
 * Ham Dog & TC's composable for handling public invitation acceptance!
 */
import { ref } from 'vue'
import invitationService from '../services/invitationService'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'
import type {
  Invitation,
  InvitationAcceptForm,
  InvitationAcceptResponse,
} from '../types/invitation.types'

export function useInvitationAcceptance() {
  const toastStore = useToastStore()
  const authStore = useAuthStore()

  // State
  const invitation = ref<Invitation | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Verify invitation token
  async function verifyInvitationToken(token: string): Promise<Invitation | null> {
    loading.value = true
    error.value = null

    try {
      const response = await invitationService.verifyToken(token)
      invitation.value = response
      return response
    } catch (err: any) {
      error.value = 'Invalid or expired invitation token'
      toastStore.error('This invitation is invalid or has expired')
      invitation.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  // Accept invitation
  async function acceptInvitation(formData: InvitationAcceptForm): Promise<InvitationAcceptResponse> {
    loading.value = true
    error.value = null

    try {
      const response = await invitationService.acceptInvitation(formData)

      // Store the JWT tokens
      if (response.access && response.refresh) {
        authStore.setTokens({
          access: response.access,
          refresh: response.refresh
        })
        authStore.setUser(response.user)
      }

      toastStore.success('Invitation accepted successfully! Welcome aboard!')
      return response
    } catch (err: any) {
      let errorMessage = 'Failed to accept invitation'

      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.response?.data?.non_field_errors) {
        errorMessage = err.response.data.non_field_errors[0]
      }

      error.value = errorMessage
      toastStore.error(errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset state
  function reset() {
    invitation.value = null
    loading.value = false
    error.value = null
  }

  return {
    // State
    invitation,
    loading,
    error,

    // Actions
    verifyInvitationToken,
    acceptInvitation,
    reset,
  }
}

/**
 * Invitation List Store - Focused on list management and filtering
 * Ham Dog & TC's specialized store for invitation list operations!
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import invitationService from '../services/invitationService'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'
import type {
  Invitation,
  InvitationFilters,
  InvitationPermissions,
} from '../types/invitation.types'

export const useInvitationListStore = defineStore('invitationList', () => {
  const toastStore = useToastStore()
  const authStore = useAuthStore()

  // State - focused on list management
  const invitations = ref<Invitation[]>([])
  const myInvitations = ref<Invitation[]>([])
  const loading = ref(false)
  const actionLoading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<InvitationFilters>({})

  // Permissions based on user role
  const permissions = computed<InvitationPermissions>(() => {
    const user = authStore.user
    const userRoles = user?.roles || []
    return {
      canSend: userRoles.includes('admin') || userRoles.includes('manager'),
      canViewAll: userRoles.includes('admin') || userRoles.includes('manager'),
      canManage: userRoles.includes('admin'),
      canResend: userRoles.includes('admin') || userRoles.includes('manager'),
      canCancel: userRoles.includes('admin') || userRoles.includes('manager'),
    }
  })

  // Computed - list filtering and categorization
  const pendingInvitations = computed(() => invitations.value.filter((i) => i.status === 'pending'))

  const acceptedInvitations = computed(() =>
    invitations.value.filter((i) => i.status === 'accepted'),
  )

  const expiredInvitations = computed(() =>
    invitations.value.filter((i) => i.status === 'expired' || i.is_expired),
  )

  const invitationCount = computed(() => invitations.value.length)

  // Actions - List Operations
  async function fetchInvitations(appliedFilters?: InvitationFilters) {
    loading.value = true
    error.value = null

    try {
      const response = await invitationService.listInvitations(appliedFilters)
      console.log('Invitations API Response:', response)

      // Handle both paginated and non-paginated responses
      if (Array.isArray(response)) {
        invitations.value = response
      } else if (response && response.results) {
        invitations.value = response.results
      } else {
        invitations.value = []
      }

      filters.value = appliedFilters || {}
      console.log('Invitations stored:', invitations.value)
    } catch (err: any) {
      console.error('Failed to fetch invitations:', err)
      error.value = err.message || 'Failed to fetch invitations'
      toastStore.error('Failed to load invitations')
      invitations.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchMyInvitations() {
    try {
      myInvitations.value = await invitationService.getMyInvitations()
    } catch (err: any) {
      console.error('Failed to fetch my invitations:', err)
      myInvitations.value = []
    }
  }

  // Actions - Individual Invitation Management
  async function resendInvitation(publicId: string, customMessage?: string) {
    actionLoading.value = true
    error.value = null

    try {
      const response = await invitationService.resendInvitation(
        publicId,
        customMessage ? { invitation_id: publicId, message: customMessage } : undefined,
      )

      toastStore.success('Invitation resent successfully!')

      // Update the invitation in our list - resend returns the updated invitation data
      const index = invitations.value.findIndex((i) => i.public_id === publicId)
      if (index !== -1) {
        // The response extends Invitation, so we can use it directly
        invitations.value[index] = response
      }

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to resend invitation'
      toastStore.error('Failed to resend invitation')
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  async function cancelInvitation(publicId: string) {
    actionLoading.value = true
    error.value = null

    try {
      const invitation = await invitationService.cancelInvitation(publicId)

      toastStore.success('Invitation cancelled')

      // Update the invitation in our list
      const index = invitations.value.findIndex((i) => i.public_id === publicId)
      if (index !== -1) {
        invitations.value[index] = invitation
      }

      return invitation
    } catch (err: any) {
      error.value = err.message || 'Failed to cancel invitation'
      toastStore.error('Failed to cancel invitation')
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  async function extendInvitationExpiry(publicId: string, days: number = 7) {
    actionLoading.value = true
    error.value = null

    try {
      const invitation = await invitationService.extendExpiry(publicId, days)

      toastStore.success(`Invitation expiry extended by ${days} days`)

      // Update the invitation in our list
      const index = invitations.value.findIndex((i) => i.public_id === publicId)
      if (index !== -1) {
        invitations.value[index] = invitation
      }

      return invitation
    } catch (err: any) {
      error.value = err.message || 'Failed to extend invitation expiry'
      toastStore.error('Failed to extend invitation expiry')
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  async function deleteInvitation(publicId: string) {
    actionLoading.value = true
    error.value = null

    try {
      await invitationService.deleteInvitation(publicId)

      toastStore.success('Invitation deleted')

      // Remove from our list
      invitations.value = invitations.value.filter((i) => i.public_id !== publicId)
    } catch (err: any) {
      error.value = err.message || 'Failed to delete invitation'
      toastStore.error('Failed to delete invitation')
      throw err
    } finally {
      actionLoading.value = false
    }
  }

  // Filter helpers
  function applyFilters(newFilters: InvitationFilters) {
    return fetchInvitations(newFilters)
  }

  function resetFilters() {
    filters.value = {}
    return fetchInvitations()
  }

  function hasActiveFilters() {
    return !!(filters.value.status || filters.value.role || filters.value.search)
  }

  function getActiveFilterCount() {
    let count = 0
    if (filters.value.status) count++
    if (filters.value.role) count++
    if (filters.value.search) count++
    return count
  }

  // Refresh - useful for after form submissions
  async function refreshInvitations() {
    if (permissions.value.canViewAll) {
      await fetchInvitations(filters.value)
    }
    await fetchMyInvitations()
  }

  // Permission helpers
  function canPerformAction(
    invitation: Invitation,
    action: 'resend' | 'cancel' | 'extend' | 'delete',
  ) {
    switch (action) {
      case 'resend':
        return (
          invitation.status === 'pending' && !invitation.is_expired && permissions.value.canResend
        )
      case 'cancel':
        return invitation.status === 'pending' && permissions.value.canCancel
      case 'extend':
        return invitation.status === 'pending' && permissions.value.canManage
      case 'delete':
        return permissions.value.canManage
      default:
        return false
    }
  }

  // Reset store
  function resetStore() {
    invitations.value = []
    myInvitations.value = []
    loading.value = false
    actionLoading.value = false
    error.value = null
    filters.value = {}
  }

  return {
    // State
    invitations,
    myInvitations,
    loading,
    actionLoading,
    error,
    filters,

    // Computed
    permissions,
    pendingInvitations,
    acceptedInvitations,
    expiredInvitations,
    invitationCount,

    // Actions - List Management
    fetchInvitations,
    fetchMyInvitations,
    refreshInvitations,

    // Actions - Individual Operations
    resendInvitation,
    cancelInvitation,
    extendInvitationExpiry,
    deleteInvitation,

    // Filter Actions
    applyFilters,
    resetFilters,
    hasActiveFilters,
    getActiveFilterCount,

    // Permission Helpers
    canPerformAction,

    // Utilities
    resetStore,
  }
})

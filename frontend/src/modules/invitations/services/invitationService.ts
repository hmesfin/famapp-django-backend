/**
 * Invitation Service Layer
 * Ham Dog & TC's API communication hub for invitations!
 */
import api from '@/services/api'
import type {
  Invitation,
  InvitationCreateForm,
  InvitationAcceptForm,
  InvitationResendForm,
  InvitationFilters,
  InvitationListResponse,
  InvitationCreateResponse,
  InvitationAcceptResponse,
  BulkInvitationForm,
  BulkInvitationResult,
  InvitationStats,
} from '../types/invitation.types'

class InvitationService {
  // List invitations with filters
  async listInvitations(filters?: InvitationFilters): Promise<InvitationListResponse> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.role) params.append('role', filters.role)
    if (filters?.email) params.append('email', filters.email)
    if (filters?.search) params.append('search', filters.search)
    if (filters?.expired !== undefined) params.append('expired', filters.expired.toString())

    const response = await api.get(`/invitations/?${params}`)
    return response
  }

  // Get a single invitation by ID
  async getInvitation(publicId: string): Promise<Invitation> {
    const response = await api.get(`/invitations/${publicId}/`)
    return response
  }

  // Create a new invitation
  async createInvitation(data: InvitationCreateForm): Promise<InvitationCreateResponse> {
    const response = await api.post(`/invitations/`, data)
    return response
  }

  // Bulk create invitations
  async createBulkInvitations(data: BulkInvitationForm): Promise<BulkInvitationResult> {
    const response = await api.post(`/invitations/bulk_invite/`, data)
    return response
  }

  // Accept an invitation
  async acceptInvitation(data: InvitationAcceptForm): Promise<InvitationAcceptResponse> {
    const response = await api.post(`/invitations/accept/`, data)
    return response
  }

  // Verify invitation token (check if valid before showing accept form)
  async verifyToken(token: string): Promise<Invitation> {
    const response = await api.get(`/invitations/verify/?token=${token}`)
    return response
  }

  // Resend an invitation
  async resendInvitation(
    publicId: string,
    data?: InvitationResendForm,
  ): Promise<InvitationCreateResponse> {
    const response = await api.post(`/invitations/${publicId}/resend/`, data || {})
    return response
  }

  // Cancel an invitation
  async cancelInvitation(publicId: string): Promise<Invitation> {
    const response = await api.post(`/invitations/${publicId}/cancel/`)
    return response
  }

  // Extend invitation expiry
  async extendExpiry(publicId: string, days: number = 7): Promise<Invitation> {
    const response = await api.post(`/invitations/${publicId}/extend_expiry/`, { days })
    return response
  }

  // Get invitation statistics
  async getStats(): Promise<InvitationStats> {
    const response = await api.get(`/invitations/stats/`)
    return response
  }

  // Get pending invitations count for current user
  async getPendingCount(): Promise<number> {
    const response = await api.get(`/invitations/pending_count/`)
    return response.count || 0
  }

  // Check if email already has pending invitation
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await api.get(`/invitations/check_email/?email=${encodeURIComponent(email)}`)
      return response.exists || false
    } catch {
      return false
    }
  }

  // Get invitations sent by current user
  async getMyInvitations(): Promise<Invitation[]> {
    const response = await api.get(`/invitations/my_invitations/`)
    // Handle both paginated and non-paginated responses
    if (Array.isArray(response)) {
      return response
    }
    return response?.results || []
  }

  // Delete/soft-delete an invitation
  async deleteInvitation(publicId: string): Promise<void> {
    await api.delete(`/invitations/${publicId}/`)
  }

  // Helper to format invitation URL for display
  formatInvitationUrl(token: string): string {
    const baseUrl = window.location.origin
    return `${baseUrl}/invitations/accept?token=${token}`
  }

  // Helper to check if invitation is still valid
  isInvitationValid(invitation: Invitation): boolean {
    if (invitation.status !== 'pending') return false
    if (invitation.is_expired) return false

    const expiryDate = new Date(invitation.expires_at)
    return expiryDate > new Date()
  }

  // Helper to calculate time until expiry
  getTimeUntilExpiry(invitation: Invitation): string {
    const now = new Date()
    const expiry = new Date(invitation.expires_at)
    const diff = expiry.getTime() - now.getTime()

    if (diff <= 0) return 'Expired'

    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

    if (days > 0) {
      return `${days} day${days > 1 ? 's' : ''} ${hours} hour${hours > 1 ? 's' : ''}`
    }
    return `${hours} hour${hours > 1 ? 's' : ''}`
  }
}

export default new InvitationService()

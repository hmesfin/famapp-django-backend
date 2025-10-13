/**
 * Invitation Management Types
 * Ham Dog & TC's TypeScript definitions for the invitation system!
 */

import type { UserSummary } from '@/modules/projects/types/project.types'
import type { User } from '@/stores/auth'

// Role types matching backend
export type SystemRole = 'admin' | 'manager' | 'member' | 'viewer' | 'guest'

// Invitation status types
export type InvitationStatus = 'pending' | 'accepted' | 'expired' | 'cancelled'

// Main Invitation interface
export interface Invitation {
  public_id: string
  email: string
  first_name?: string
  last_name?: string
  full_name?: string
  role: SystemRole
  status: InvitationStatus
  organization_name?: string
  message?: string
  invited_by: UserSummary
  accepted_by?: UserSummary
  expires_at: string
  accepted_at?: string
  is_expired?: boolean
  created_at: string
  updated_at?: string
}

// Form types for creating/accepting invitations
export interface InvitationCreateForm {
  email: string
  first_name?: string
  last_name?: string
  role: SystemRole
  organization_name?: string
  message?: string
}

export interface InvitationAcceptForm {
  token: string
  first_name: string
  last_name: string
  password: string
  password_confirm: string
}

export interface InvitationResendForm {
  invitation_id: string
  message?: string
}

// API response types
export interface InvitationListResponse {
  results: Invitation[]
  count: number
  next?: string
  previous?: string
}

export interface InvitationCreateResponse extends Invitation {
  invitation_url: string
}

export interface InvitationAcceptResponse {
  user: User
  access: string
  refresh: string
  message: string
}

// Filter types
export interface InvitationFilters {
  status?: InvitationStatus
  role?: SystemRole
  email?: string
  search?: string
  expired?: boolean
}

// Bulk invitation types
export interface BulkInvitationForm {
  emails: string[]
  role: SystemRole
  organization_name?: string
  message?: string
}

export interface BulkInvitationResult {
  successful: InvitationCreateResponse[]
  failed: Array<{
    email: string
    error: string
  }>
}

// Permission check types
export interface InvitationPermissions {
  canSend: boolean
  canViewAll: boolean
  canManage: boolean
  canResend: boolean
  canCancel: boolean
}

// Statistics types
export interface InvitationStats {
  total: number
  pending: number
  accepted: number
  expired: number
  cancelled: number
  acceptance_rate: number
  average_acceptance_time: number // in hours
}

// Role display information
export const ROLE_DISPLAY_NAMES: Record<SystemRole, string> = {
  admin: 'Administrator',
  manager: 'Manager',
  member: 'Member',
  viewer: 'Viewer',
  guest: 'Guest',
}

export const ROLE_DESCRIPTIONS: Record<SystemRole, string> = {
  admin: 'Full system access with all permissions',
  manager: 'Can manage projects, users, and send invitations',
  member: 'Can create and participate in projects',
  viewer: 'Read-only access to projects',
  guest: 'Limited access, no default permissions',
}

export const STATUS_COLORS: Record<InvitationStatus, string> = {
  pending: 'yellow',
  accepted: 'green',
  expired: 'red',
  cancelled: 'gray',
}

export const STATUS_ICONS: Record<InvitationStatus, string> = {
  pending: 'clock',
  accepted: 'check-circle',
  expired: 'x-circle',
  cancelled: 'ban',
}

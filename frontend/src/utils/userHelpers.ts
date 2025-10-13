/**
 * User utility functions
 * Ham Dog & TC's defensive user data handling arsenal! 🛡️
 * Define it once, use it everywhere - that's the TC way!
 */
import type { UserSummary } from '@/modules/projects/types/project.types'
import type { User } from '@/stores/auth'

/**
 * Safely get a user's display name with fallback hierarchy:
 * 1. full_name (if provided by serializer)
 * 2. "first_name last_name" (if both exist)
 * 3. first_name or last_name (if only one exists)  
 * 4. email (as ultimate fallback)
 * 5. "Unknown User" (if somehow everything is missing)
 */
export function getUserDisplayName(user: UserSummary | User | null | undefined): string {
  if (!user) return 'Unknown User'

  // If we have full_name from serializer, use it
  if (user.full_name?.trim()) {
    return user.full_name.trim()
  }

  // Build from first_name + last_name
  const firstName = user.first_name?.trim() || ''
  const lastName = user.last_name?.trim() || ''
  
  if (firstName && lastName) {
    return `${firstName} ${lastName}`
  }
  
  if (firstName) {
    return firstName
  }
  
  if (lastName) {
    return lastName
  }

  // Fall back to email
  if (user.email?.trim()) {
    return user.email.trim()
  }

  // Ultimate fallback
  return 'Unknown User'
}

/**
 * Get user initials for avatars with defensive programming
 */
export function getUserInitials(user: UserSummary | User | null | undefined): string {
  if (!user) return 'UN'

  const firstName = user.first_name?.trim() || ''
  const lastName = user.last_name?.trim() || ''
  
  if (firstName && lastName) {
    return `${firstName[0]}${lastName[0]}`.toUpperCase()
  }
  
  if (firstName && firstName.length >= 2) {
    return firstName.slice(0, 2).toUpperCase()
  }
  
  if (lastName && lastName.length >= 2) {
    return lastName.slice(0, 2).toUpperCase()
  }
  
  if (firstName) {
    return `${firstName[0]}${firstName[0]}`.toUpperCase()
  }
  
  if (lastName) {
    return `${lastName[0]}${lastName[0]}`.toUpperCase()
  }

  // Fall back to email initials
  if (user.email?.trim() && user.email.length >= 2) {
    return user.email.slice(0, 2).toUpperCase()
  }

  return 'UN'
}

/**
 * Get user short name (first name or email)
 */
export function getUserShortName(user: UserSummary | User | null | undefined): string {
  if (!user) return 'Unknown'

  if (user.first_name?.trim()) {
    return user.first_name.trim()
  }

  if (user.email?.trim()) {
    return user.email.trim()
  }

  return 'Unknown'
}

/**
 * Get user's avatar URL with fallbacks
 * Returns null if no avatar - components should use initials as fallback
 */
export function getUserAvatarUrl(user: UserSummary | User | null | undefined): string | null {
  if (!user) return null
  
  // Check for avatar field (if we add it later)
  if ('avatar' in user && user.avatar) {
    return user.avatar
  }
  
  // Check for profile_image field (common in many systems)
  if ('profile_image' in user && user.profile_image) {
    return user.profile_image
  }
  
  return null
}

/**
 * Check if user has a complete profile (both first and last name)
 */
export function hasCompleteProfile(user: UserSummary | User | null | undefined): boolean {
  if (!user) return false
  
  const firstName = user.first_name?.trim()
  const lastName = user.last_name?.trim()
  
  return !!(firstName && lastName)
}

/**
 * Get user's email domain for grouping/filtering
 */
export function getUserEmailDomain(user: UserSummary | User | null | undefined): string | null {
  if (!user?.email?.trim()) return null
  
  const emailParts = user.email.trim().split('@')
  return emailParts.length === 2 ? emailParts[1] : null
}

/**
 * Generate user mention string for comments/notifications
 * @example "@john.doe" or "@john" or "@user@example.com"
 */
export function getUserMention(user: UserSummary | User | null | undefined): string {
  if (!user) return '@unknown'
  
  const firstName = user.first_name?.trim()
  const lastName = user.last_name?.trim()
  
  if (firstName && lastName) {
    // Create a clean mention like "@john.doe"
    const mention = `${firstName}.${lastName}`.toLowerCase().replace(/[^a-z0-9.]/g, '')
    return `@${mention}`
  }
  
  if (firstName) {
    const mention = firstName.toLowerCase().replace(/[^a-z0-9]/g, '')
    return `@${mention}`
  }
  
  if (user.email?.trim()) {
    return `@${user.email.trim()}`
  }
  
  return '@unknown'
}

/**
 * Check if user is likely a real person vs system/bot account
 * Heuristic based on having human-like name
 */
export function isLikelyHumanUser(user: UserSummary | User | null | undefined): boolean {
  if (!user) return false
  
  const firstName = user.first_name?.trim()
  const lastName = user.last_name?.trim()
  const email = user.email?.trim()
  
  // Has both first and last name
  if (firstName && lastName && firstName.length > 1 && lastName.length > 1) {
    return true
  }
  
  // Email doesn't look like a system account
  if (email && !email.match(/(noreply|no-reply|system|admin|bot|automated|service)@/i)) {
    return true
  }
  
  return false
}

/**
 * Sort users by display name for consistent ordering
 */
export function compareUsersByDisplayName(
  a: UserSummary | User | null | undefined, 
  b: UserSummary | User | null | undefined
): number {
  const nameA = getUserDisplayName(a).toLowerCase()
  const nameB = getUserDisplayName(b).toLowerCase()
  
  return nameA.localeCompare(nameB)
}

/**
 * Filter out null/undefined users and return only valid ones
 * Useful for cleaning arrays of possibly null users
 */
export function filterValidUsers<T extends UserSummary | User>(
  users: (T | null | undefined)[]
): T[] {
  return users.filter((user): user is T => user != null)
}

/**
 * Group users by email domain
 */
export function groupUsersByDomain(users: (UserSummary | User)[]): Record<string, (UserSummary | User)[]> {
  const groups: Record<string, (UserSummary | User)[]> = {}
  
  users.forEach(user => {
    const domain = getUserEmailDomain(user) || 'unknown'
    if (!groups[domain]) {
      groups[domain] = []
    }
    groups[domain].push(user)
  })
  
  return groups
}

/**
 * Find user in array by email (case-insensitive)
 */
export function findUserByEmail(
  users: (UserSummary | User)[], 
  email: string | null | undefined
): UserSummary | User | null {
  if (!email?.trim()) return null
  
  const searchEmail = email.trim().toLowerCase()
  return users.find(user => user.email?.trim().toLowerCase() === searchEmail) || null
}

/**
 * Find user in array by public_id
 */
export function findUserById(
  users: (UserSummary | User)[], 
  publicId: string | null | undefined
): UserSummary | User | null {
  if (!publicId?.trim()) return null
  
  return users.find(user => user.public_id === publicId.trim()) || null
}
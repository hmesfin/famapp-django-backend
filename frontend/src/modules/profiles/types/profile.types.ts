/**
 * Profile & Settings Types - TypeScript Interfaces
 * Defines the data structures for user profiles and settings
 */

export interface Profile {
  public_id: string
  user_email: string
  user_full_name: string
  bio: string | null
  location: string | null
  website: string | null
  company: string | null
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface UserSettings {
  public_id: string
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  email_notifications: boolean
  push_notifications: boolean
  profile_visibility: 'public' | 'private' | 'friends'
  show_email: boolean
  show_activity: boolean
  metadata: Record<string, any> | null
}

export interface ProfileForm {
  bio?: string | null
  location?: string | null
  website?: string | null
  company?: string | null
  avatar_url?: string | null
}

export interface SettingsForm {
  theme?: 'light' | 'dark' | 'auto'
  language?: string
  timezone?: string
  email_notifications?: boolean
  push_notifications?: boolean
  profile_visibility?: 'public' | 'private' | 'friends'
  show_email?: boolean
  show_activity?: boolean
  metadata?: Record<string, any> | null
}

export interface ProfileFilters {
  search?: string
  location?: string
  company?: string
}

// API Response types
export interface ProfileResponse {
  count: number
  next: string | null
  previous: string | null
  results: Profile[]
}

// Avatar size variants for ProfileAvatar component
export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

// Profile visibility states
export type ProfileVisibility = 'public' | 'private' | 'friends'

// Theme options
export type ThemeOption = 'light' | 'dark' | 'auto'

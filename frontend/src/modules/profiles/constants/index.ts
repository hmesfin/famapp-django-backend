/**
 * Profile Module Constants
 * Centralized configuration following RefactorA's recommendations
 */

// API Endpoints
export const PROFILE_ENDPOINTS = {
  LIST: '/profiles/',
  DETAIL: (id: string) => `/profiles/${id}/`,
  ME: '/profiles/me/',
  UPLOAD_AVATAR: '/profiles/upload-avatar/',
  SETTINGS: '/settings/current_settings/',
} as const

// Avatar constraints (must match backend)
export const AVATAR_CONSTRAINTS = {
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  MAX_FILE_SIZE_MB: 5,
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.webp'],
} as const

// Profile field constraints (must match backend)
export const PROFILE_CONSTRAINTS = {
  BIO_MAX_LENGTH: 500,
  LOCATION_MAX_LENGTH: 100,
  COMPANY_MAX_LENGTH: 100,
  WEBSITE_MAX_LENGTH: 200,
} as const

// Settings defaults
export const SETTINGS_DEFAULTS = {
  THEME: 'light' as const,
  LANGUAGE: 'en',
  TIMEZONE: 'UTC',
  EMAIL_NOTIFICATIONS: true,
  PUSH_NOTIFICATIONS: false,
  PROFILE_VISIBILITY: 'public' as const,
  SHOW_EMAIL: false,
  SHOW_ACTIVITY: true,
} as const

// Theme options
export const THEME_OPTIONS = ['light', 'dark', 'auto'] as const
export type ThemeOption = (typeof THEME_OPTIONS)[number]

// Profile visibility options
export const VISIBILITY_OPTIONS = ['public', 'private', 'friends'] as const
export type ProfileVisibility = (typeof VISIBILITY_OPTIONS)[number]

// Cache durations (ms)
export const CACHE_DURATIONS = {
  PROFILE: 60 * 60 * 1000, // 1 hour
  SETTINGS: 2 * 60 * 60 * 1000, // 2 hours
  AVATAR: 24 * 60 * 60 * 1000, // 24 hours
} as const

// Debounce delays (ms)
export const DEBOUNCE_DELAYS = {
  SEARCH: 300,
  VALIDATION: 500,
  SAVE: 1000,
} as const

// Success messages with personality! 🎉
export const SUCCESS_MESSAGES = {
  PROFILE_UPDATED: '🎉 Profile updated successfully! Looking good!',
  AVATAR_UPLOADED: "📸 New avatar uploaded! You're looking fresh!",
  SETTINGS_UPDATED: "⚙️ Settings updated! We're all synced up now.",
  PROFILE_CREATED: '✨ Profile created successfully! Welcome to the community!',
  THEME_CHANGED: '🎨 Theme switched! Hope you like the new look!',
  NOTIFICATIONS_UPDATED:
    "🔔 Notification preferences saved! We'll keep you posted (or not, as you prefer).",
  PRIVACY_UPDATED: '🛡️ Privacy settings updated! Your secrets are safe with us.',
} as const

// Error messages with personality and helpfulness! 💡
export const ERROR_MESSAGES = {
  // Profile form errors
  PROFILE_LOAD_FAILED:
    "🕵️ We couldn't find that profile. It might have vanished into the digital ether!",
  PROFILE_SAVE_FAILED:
    "💾 Something went sideways while saving. Don't worry, your changes are safe - just hit save again!",
  PROFILE_SAVE_NETWORK:
    '📶 Your internet seems a bit wobbly. Check your connection and try saving again.',
  PROFILE_SAVE_PERMISSIONS:
    "🔒 Looks like you don't have permission for that action. Try refreshing the page or contact support if this keeps happening.",
  PROFILE_ALREADY_EXISTS:
    '🎬 Déjà vu! You already have a profile. How about editing it instead of creating another?',
  PROFILE_ACCESS_DENIED: '🚫 That profile is off-limits to you. Respect the privacy boundaries!',

  // Avatar upload errors
  AVATAR_UPLOAD_FAILED:
    '📷 Oops! Something went wrong with your avatar upload. Give it another shot?',
  AVATAR_TOO_LARGE:
    '📸 Whoa! That image is bigger than a movie poster! Please choose something under 5MB.',
  AVATAR_INVALID_TYPE:
    "🎨 That file type isn't quite right. We love JPEG, PNG, WebP, or GIF images!",
  AVATAR_UPLOAD_NETWORK:
    '📡 Looks like your connection hiccupped during upload. Mind trying again?',

  // Settings errors
  SETTINGS_LOAD_FAILED:
    "⚙️ Couldn't load your settings right now. We'll keep trying in the background!",
  SETTINGS_SAVE_FAILED:
    '🔧 Settings update got a bit twisted. Your current preferences are still active though!',
  THEME_UPDATE_FAILED:
    "🎨 Couldn't switch themes right now. Your current theme is still looking good though!",
  LANGUAGE_UPDATE_FAILED:
    "🗣️ Language update hit a snag. We're still speaking the same language though!",
  TIMEZONE_UPDATE_FAILED:
    "⏰ Time got a bit twisted there! Couldn't update your timezone, but we're still in sync.",
  NOTIFICATION_UPDATE_FAILED:
    "🔔 Couldn't update your notification preferences. Your current settings are still active!",
  PRIVACY_UPDATE_FAILED:
    '🔐 Privacy settings update got a bit bashful. Your current privacy is still protected!',

  // Validation errors
  VALIDATION_ERROR: '🔍 Looks like a few fields need some love! Check the highlighted areas below.',
  BIO_TOO_LONG:
    "📝 Your bio is longer than a Tolkien novel! Let's trim it to 500 characters - save some mystery for conversation!",
  LOCATION_TOO_LONG:
    "🗺️ That location description could span continents! Let's keep it under 100 characters.",
  COMPANY_TOO_LONG:
    "🏢 That company name could be a business plan! Let's keep it under 100 characters.",
  WEBSITE_INVALID:
    "🔗 That URL doesn't look quite right. Try something like 'https://example.com' (don't forget the https!)",
  WEBSITE_TOO_LONG: "🌐 That's one looong URL! Let's trim it to under 200 characters.",

  // Generic errors
  NETWORK_ERROR:
    '📡 Your internet connection seems to be playing hide and seek. Check your connection and try again!',
  TIMEOUT_ERROR:
    '⏱️ That took longer than watching paint dry! The request timed out - give it another shot.',
  UNKNOWN_ERROR:
    "🤷 Something mysterious happened that we can't quite explain. The tech team is on it!",

  // HTTP status errors
  UNAUTHORIZED:
    '🔐 Looks like you need to log in again. Your session might have expired while you were away!',
  FORBIDDEN:
    "🚫 You don't have permission to do that. If you think this is a mistake, contact support!",
  NOT_FOUND:
    "🕵️ We searched everywhere but couldn't find what you're looking for. It might have moved or been deleted!",
  CONFLICT:
    "⚔️ There's a conflict with your request. Someone else might have made changes - try refreshing!",
  UNPROCESSABLE:
    "🔧 Your request looks good, but something doesn't quite fit. Check the highlighted fields!",
  TOO_MANY_REQUESTS:
    "🐌 Whoa there, speed racer! You're making requests faster than we can handle. Take a breather and try again in a moment.",
  SERVER_ERROR:
    "🤖 Our servers are having a bit of a moment. Don't worry, it's not you - it's us! Try again in a few seconds.",
  BAD_GATEWAY:
    "🌉 There's a traffic jam on our digital highway. Give us a moment to clear the path!",
  SERVICE_UNAVAILABLE:
    "🔧 We're doing some quick maintenance. Grab a coffee and we'll be right back!",
} as const

// Helper function to get friendly field names
export const FIELD_NAMES = {
  bio: 'Bio',
  location: 'Location', 
  website: 'Website',
  company: 'Company',
  avatar_url: 'Avatar',
  theme: 'Theme',
  language: 'Language',
  timezone: 'Timezone',
  email_notifications: 'Email Notifications',
  push_notifications: 'Push Notifications',
  profile_visibility: 'Profile Visibility',
  show_email: 'Show Email',
  show_activity: 'Show Activity',
} as const

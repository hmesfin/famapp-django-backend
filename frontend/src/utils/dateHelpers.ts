/**
 * Date formatting utilities
 * Extracted by RefactorX from duplicated date logic across components
 */

/**
 * Format a date string to a human-readable format
 * @param dateString - ISO date string or Date object
 * @param options - Formatting options
 * @returns Formatted date string
 */
export function formatDate(
  dateString: string | Date | null | undefined,
  options: {
    includeTime?: boolean
    includeYear?: boolean
    shortMonth?: boolean
  } = {}
): string {
  if (!dateString) return 'N/A'
  
  const {
    includeTime = false,
    includeYear = true,
    shortMonth = true
  } = options

  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    
    // Check for invalid date
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }

    const dateOptions: Intl.DateTimeFormatOptions = {
      month: shortMonth ? 'short' : 'long',
      day: 'numeric',
      ...(includeYear && { year: 'numeric' })
    }

    if (includeTime) {
      dateOptions.hour = '2-digit'
      dateOptions.minute = '2-digit'
    }

    return date.toLocaleDateString('en-US', dateOptions)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid date'
  }
}

/**
 * Format a date with relative time information
 * Shows "2 hours ago", "yesterday", etc. with the actual date
 * @param dateString - ISO date string or Date object
 * @returns Formatted date with relative time
 */
export function formatDateWithRelative(dateString: string | Date | undefined): string {
  if (!dateString) return 'N/A'
  
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    const formatted = formatDate(date)
    
    // Add relative time for recent dates
    if (diffDays === 0) {
      const hours = Math.floor(diffTime / (1000 * 60 * 60))
      if (hours === 0) {
        const minutes = Math.floor(diffTime / (1000 * 60))
        if (minutes === 0) {
          return `${formatted} (just now)`
        }
        return `${formatted} (${minutes} min ago)`
      }
      return `${formatted} (${hours} hours ago)`
    } else if (diffDays === 1) {
      return `${formatted} (yesterday)`
    } else if (diffDays < 7) {
      return `${formatted} (${diffDays} days ago)`
    }
    
    return formatted
  } catch (error) {
    console.error('Error formatting date with relative:', error)
    return 'Invalid date'
  }
}

/**
 * Format relative time only (e.g., "2 hours ago", "in 3 days")
 * @param dateString - ISO date string or Date object
 * @returns Relative time string
 */
export function formatRelativeTime(dateString: string | Date): string {
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const absDiffTime = Math.abs(diffTime)
    const isPast = diffTime > 0
    
    const diffMinutes = Math.floor(absDiffTime / (1000 * 60))
    const diffHours = Math.floor(absDiffTime / (1000 * 60 * 60))
    const diffDays = Math.floor(absDiffTime / (1000 * 60 * 60 * 24))
    const diffWeeks = Math.floor(diffDays / 7)
    const diffMonths = Math.floor(diffDays / 30)
    
    if (diffMinutes < 1) {
      return 'just now'
    } else if (diffMinutes < 60) {
      return isPast ? `${diffMinutes} min ago` : `in ${diffMinutes} min`
    } else if (diffHours < 24) {
      const unit = diffHours === 1 ? 'hour' : 'hours'
      return isPast ? `${diffHours} ${unit} ago` : `in ${diffHours} ${unit}`
    } else if (diffDays < 7) {
      const unit = diffDays === 1 ? 'day' : 'days'
      return isPast ? `${diffDays} ${unit} ago` : `in ${diffDays} ${unit}`
    } else if (diffWeeks < 4) {
      const unit = diffWeeks === 1 ? 'week' : 'weeks'
      return isPast ? `${diffWeeks} ${unit} ago` : `in ${diffWeeks} ${unit}`
    } else if (diffMonths < 12) {
      const unit = diffMonths === 1 ? 'month' : 'months'
      return isPast ? `${diffMonths} ${unit} ago` : `in ${diffMonths} ${unit}`
    } else {
      const diffYears = Math.floor(diffDays / 365)
      const unit = diffYears === 1 ? 'year' : 'years'
      return isPast ? `${diffYears} ${unit} ago` : `in ${diffYears} ${unit}`
    }
  } catch (error) {
    console.error('Error formatting relative time:', error)
    return ''
  }
}

/**
 * Format a due date with smart relative text
 * @param dateString - ISO date string or Date object
 * @returns Smart due date text (e.g., "Due today", "3 days overdue")
 */
export function formatDueDate(dateString: string | Date | null | undefined): string {
  if (!dateString) return 'No due date'
  
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    const today = new Date()
    
    // Reset time portion for accurate day comparison
    today.setHours(0, 0, 0, 0)
    const dueDate = new Date(date)
    dueDate.setHours(0, 0, 0, 0)
    
    const diffTime = dueDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return 'Due today'
    } else if (diffDays === 1) {
      return 'Due tomorrow'
    } else if (diffDays === -1) {
      return 'Due yesterday'
    } else if (diffDays < -1) {
      return `${Math.abs(diffDays)} days overdue`
    } else if (diffDays <= 7) {
      return `Due in ${diffDays} days`
    } else if (diffDays <= 14) {
      return `Due in ${Math.ceil(diffDays / 7)} weeks`
    } else {
      return formatDate(date, { includeYear: diffDays > 365, shortMonth: true })
    }
  } catch (error) {
    console.error('Error formatting due date:', error)
    return 'Invalid date'
  }
}

/**
 * Check if a date is in the past
 * @param dateString - ISO date string or Date object
 * @returns True if the date is in the past
 */
export function isPastDate(dateString: string | Date | null | undefined): boolean {
  if (!dateString) return false
  
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    return date.getTime() < new Date().getTime()
  } catch {
    return false
  }
}

/**
 * Check if a date is today
 * @param dateString - ISO date string or Date object
 * @returns True if the date is today
 */
export function isToday(dateString: string | Date | null | undefined): boolean {
  if (!dateString) return false
  
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    const today = new Date()
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  } catch {
    return false
  }
}

/**
 * Get days until a date
 * @param dateString - ISO date string or Date object
 * @returns Number of days (negative if in past)
 */
export function getDaysUntil(dateString: string | Date | null | undefined): number | null {
  if (!dateString) return null
  
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    date.setHours(0, 0, 0, 0)
    
    const diffTime = date.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  } catch {
    return null
  }
}

/**
 * Format a date range
 * @param startDate - Start date
 * @param endDate - End date
 * @returns Formatted date range
 */
export function formatDateRange(
  startDate: string | Date | null | undefined,
  endDate: string | Date | null | undefined
): string {
  const start = formatDate(startDate)
  const end = formatDate(endDate)
  
  if (start === 'N/A' && end === 'N/A') {
    return 'Dates not set'
  } else if (start === 'N/A') {
    return `Until ${end}`
  } else if (end === 'N/A') {
    return `From ${start}`
  } else {
    return `${start} - ${end}`
  }
}
/**
 * Shared Error Handler Utility
 * Centralized error parsing and formatting for consistency across the application
 * 
 * Eliminates duplication of error handling logic across stores
 */

export interface ParsedError {
  message: string
  fieldErrors?: Record<string, string>
  statusCode?: number
  isNetworkError?: boolean
}

/**
 * Parse API error responses into a consistent format
 * @param error - The error object from API call
 * @returns Parsed error with user-friendly message and field errors
 */
export function parseApiError(error: any): ParsedError {
  const result: ParsedError = {
    message: 'An unexpected error occurred',
    fieldErrors: {},
    statusCode: error?.response?.status,
    isNetworkError: false
  }

  // Handle network errors
  if (error.code === 'ERR_NETWORK' || !error.response) {
    result.message = 'Network error. Please check your connection and try again.'
    result.isNetworkError = true
    return result
  }

  // Extract error data from response
  const errorData = error.response?.data

  if (!errorData) {
    if (error.message) {
      result.message = error.message
    }
    return result
  }

  // Handle different error response formats from DRF
  
  // Simple detail message
  if (typeof errorData === 'string') {
    result.message = errorData
    return result
  }

  // Detail field (most common DRF format)
  if (errorData.detail) {
    result.message = Array.isArray(errorData.detail) 
      ? errorData.detail[0] 
      : errorData.detail
    return result
  }

  // Non-field errors
  if (errorData.non_field_errors) {
    result.message = Array.isArray(errorData.non_field_errors)
      ? errorData.non_field_errors[0]
      : errorData.non_field_errors
    return result
  }

  // Field-specific errors
  const fieldErrors: Record<string, string> = {}
  let hasFieldErrors = false

  // Check for field-specific errors
  for (const field of Object.keys(errorData)) {
    if (field === 'detail' || field === 'non_field_errors') {
      continue
    }

    const fieldError = errorData[field]
    if (fieldError) {
      const errorMessage = Array.isArray(fieldError) ? fieldError[0] : fieldError
      fieldErrors[field] = errorMessage
      hasFieldErrors = true
    }
  }

  if (hasFieldErrors) {
    result.fieldErrors = fieldErrors
    
    // Create a summary message from field errors
    const errorMessages = Object.entries(fieldErrors)
      .map(([field, message]) => `${formatFieldName(field)}: ${message}`)
    
    result.message = errorMessages.length === 1 
      ? errorMessages[0]
      : errorMessages.join('; ')
  }

  // Check for HTTP status code messages (last resort)
  if (!hasFieldErrors && result.message === 'An unexpected error occurred') {
    result.message = getMessageForStatusCode(result.statusCode)
  }

  return result
}

/**
 * Format field name to be human-readable
 * @param field - Field name from API
 * @returns Human-readable field name
 */
export function formatFieldName(field: string): string {
  // Special cases
  const specialCases: Record<string, string> = {
    'email': 'Email',
    'bio': 'Bio',
    'url': 'URL',
    'api': 'API',
    'id': 'ID'
  }

  if (specialCases[field.toLowerCase()]) {
    return specialCases[field.toLowerCase()]
  }

  // Convert snake_case to Title Case
  return field
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

/**
 * Get user-friendly message for HTTP status code
 * @param statusCode - HTTP status code
 * @returns User-friendly error message
 */
export function getMessageForStatusCode(statusCode?: number): string {
  if (!statusCode) {
    return 'An unexpected error occurred'
  }

  const messages: Record<number, string> = {
    400: 'The information provided is invalid. Please check and try again.',
    401: 'You need to log in to perform this action.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    405: 'This action is not allowed.',
    409: 'This conflicts with existing data. Please try a different value.',
    413: 'The file is too large. Please choose a smaller file.',
    422: 'The data provided could not be processed. Please check your input.',
    429: 'Too many requests. Please wait a moment and try again.',
    500: 'A server error occurred. Please try again later.',
    502: 'The server is temporarily unavailable. Please try again later.',
    503: 'The service is temporarily unavailable. Please try again later.',
    504: 'The request took too long. Please try again.'
  }

  return messages[statusCode] || `An error occurred (${statusCode})`
}

/**
 * Format error message for display in toast notifications
 * @param error - Parsed error object
 * @param maxLength - Maximum message length for toast
 * @returns Formatted message for toast
 */
export function formatErrorForToast(error: ParsedError, maxLength: number = 100): string {
  let message = error.message

  // Remove "HTTP XXX" prefixes
  message = message.replace(/^HTTP \d{3}:\s*/i, '')

  // Truncate if too long
  if (message.length > maxLength) {
    message = message.substring(0, maxLength - 3) + '...'
  }

  return message
}

/**
 * Default error handler for consistency
 * @param error - Raw error from API
 * @param context - Optional context for better error messages
 * @returns Parsed error ready for display
 */
export function handleApiError(error: any, context?: string): ParsedError {
  const parsedError = parseApiError(error)
  
  // Add context if provided
  if (context && !parsedError.message.toLowerCase().includes(context.toLowerCase())) {
    parsedError.message = `${context}: ${parsedError.message}`
  }
  
  // Log error for debugging (in development only)
  if (import.meta.env.DEV) {
    console.error(`API Error${context ? ` (${context})` : ''}:`, {
      original: error,
      parsed: parsedError
    })
  }
  
  return parsedError
}
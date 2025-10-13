/**
 * Composable for managing form field classes with validation states
 * Extracted by RefactorX from duplicated form validation logic
 */

import { computed, type ComputedRef, type Ref } from 'vue'

interface FieldClassOptions {
  baseClasses?: string
  errorClasses?: string
  normalClasses?: string
  darkModeSupport?: boolean
}

/**
 * Returns reactive classes for form fields based on validation state
 */
export function useFormFieldClasses(
  fieldError: Ref<string | undefined> | ComputedRef<string | undefined>,
  options: FieldClassOptions = {}
) {
  const {
    baseClasses = '',
    errorClasses = 'border-red-500 focus:border-red-500 focus:ring-red-500',
    normalClasses = 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
    darkModeSupport = true,
  } = options

  const fieldClasses = computed(() => {
    const classes: Record<string, boolean> = {}
    
    // Always apply base classes
    if (baseClasses) {
      baseClasses.split(' ').forEach(cls => {
        classes[cls] = true
      })
    }

    // Apply error or normal classes based on validation state
    if (fieldError.value) {
      errorClasses.split(' ').forEach(cls => {
        classes[cls] = true
      })
    } else {
      normalClasses.split(' ').forEach(cls => {
        classes[cls] = true
      })
      // Add dark mode border if enabled
      if (darkModeSupport) {
        classes['dark:border-gray-600'] = true
      }
    }

    return classes
  })

  return {
    fieldClasses,
    hasError: computed(() => !!fieldError.value),
  }
}

/**
 * Helper function for static field class generation (non-reactive)
 * Useful for one-time class generation in templates
 */
export function getFieldClasses(
  fieldError: string | undefined,
  baseClasses: string = '',
  options: Omit<FieldClassOptions, 'baseClasses'> = {}
): Record<string, boolean> {
  const {
    errorClasses = 'border-red-500 focus:border-red-500 focus:ring-red-500',
    normalClasses = 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
    darkModeSupport = true,
  } = options

  const classes: Record<string, boolean> = {}
  
  // Always apply base classes
  if (baseClasses) {
    baseClasses.split(' ').forEach(cls => {
      classes[cls] = true
    })
  }

  // Apply error or normal classes based on validation state
  if (fieldError) {
    errorClasses.split(' ').forEach(cls => {
      classes[cls] = true
    })
  } else {
    normalClasses.split(' ').forEach(cls => {
      classes[cls] = true
    })
    // Add dark mode border if enabled
    if (darkModeSupport) {
      classes['dark:border-gray-600'] = true
    }
  }

  return classes
}

/**
 * Preset for slightly different error styling (used in TaskFormModal)
 * Uses border-red-300 instead of border-red-500 for a softer error indication
 */
export function getFieldClassesSoft(
  fieldError: string | undefined,
  baseClasses: string = ''
): Record<string, boolean> {
  return getFieldClasses(fieldError, baseClasses, {
    errorClasses: 'border-red-300 focus:border-red-500 focus:ring-red-500',
  })
}
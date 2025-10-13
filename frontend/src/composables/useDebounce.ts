/**
 * Debounce Composable
 * Provides reusable debouncing functionality for API calls and user interactions
 */
import { ref, type Ref } from 'vue'

export interface DebouncedFunction<T extends (...args: any[]) => any> {
  (...args: Parameters<T>): void
  cancel: () => void
  flush: () => void
  pending: Ref<boolean>
}

/**
 * Creates a debounced version of a function
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function with cancel/flush methods and pending state
 */
export function useDebounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): DebouncedFunction<T> {
  const pending = ref(false)
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastArgs: Parameters<T> | null = null

  const debouncedFn = (...args: Parameters<T>) => {
    lastArgs = args
    
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    pending.value = true
    
    timeoutId = setTimeout(() => {
      pending.value = false
      timeoutId = null
      fn(...args)
    }, delay)
  }

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
      pending.value = false
    }
  }

  const flush = () => {
    if (timeoutId && lastArgs) {
      clearTimeout(timeoutId)
      timeoutId = null
      pending.value = false
      fn(...lastArgs)
    }
  }

  return Object.assign(debouncedFn, {
    cancel,
    flush,
    pending
  }) as DebouncedFunction<T>
}

/**
 * Creates a debounced ref value that triggers a callback when changed
 * @param initialValue - Initial value
 * @param callback - Function to call when value changes (debounced)
 * @param delay - Delay in milliseconds
 * @returns Reactive ref with debounced updates
 */
export function useDebouncedRef<T>(
  initialValue: T,
  callback: (value: T) => void,
  delay: number = 300
) {
  const value = ref<T>(initialValue)
  const debouncedCallback = useDebounce(callback, delay)
  
  const setValue = (newValue: T) => {
    value.value = newValue
    debouncedCallback(newValue)
  }

  return {
    value,
    setValue,
    pending: debouncedCallback.pending,
    cancel: debouncedCallback.cancel,
    flush: debouncedCallback.flush
  }
}

/**
 * Creates a debounced API call function with loading state
 * @param apiCall - Async function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced API call with loading state
 */
export function useDebouncedApiCall<T extends (...args: any[]) => Promise<any>>(
  apiCall: T,
  delay: number = 500
) {
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const debouncedCall = useDebounce(async (...args: Parameters<T>) => {
    try {
      loading.value = true
      error.value = null
      const result = await apiCall(...args)
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }, delay)

  return {
    call: debouncedCall,
    loading,
    error,
    pending: debouncedCall.pending,
    cancel: debouncedCall.cancel,
    flush: debouncedCall.flush
  }
}

/**
 * Debounce delays for different types of interactions
 */
export const DEBOUNCE_DELAYS = {
  SEARCH: 300,          // Search inputs
  VALIDATION: 500,      // Form validation
  SETTINGS: 200,        // Settings toggles  
  API_CALLS: 500,       // General API calls
  FILE_UPLOAD: 1000     // File upload validation
} as const
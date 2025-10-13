/**
 * Tests for useDebounce composable
 * Testing the refactored debouncing utility functions
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import {
  useDebounce,
  useDebouncedRef,
  useDebouncedApiCall,
  DEBOUNCE_DELAYS,
} from '@/composables/useDebounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  describe('useDebounce basic functionality', () => {
    it('should create a debounced function', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      expect(typeof debouncedFn).toBe('function')
      expect(debouncedFn.cancel).toBeDefined()
      expect(debouncedFn.flush).toBeDefined()
      expect(debouncedFn.pending).toBeDefined()
    })

    it('should delay function execution', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('test')
      expect(mockFn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(299)
      expect(mockFn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(1)
      expect(mockFn).toHaveBeenCalledWith('test')
    })

    it('should reset delay on subsequent calls', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('first')
      vi.advanceTimersByTime(200)

      debouncedFn('second')
      vi.advanceTimersByTime(200)
      expect(mockFn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(100)
      expect(mockFn).toHaveBeenCalledWith('second')
      expect(mockFn).toHaveBeenCalledTimes(1)
    })

    it('should handle multiple arguments correctly', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('arg1', 'arg2', 123, { key: 'value' })
      vi.advanceTimersByTime(300)

      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2', 123, { key: 'value' })
    })

    it('should use default delay when not specified', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn) // No delay specified

      debouncedFn()
      vi.advanceTimersByTime(299)
      expect(mockFn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(1)
      expect(mockFn).toHaveBeenCalled()
    })
  })

  describe('useDebounce pending state', () => {
    it('should track pending state correctly', async () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      expect(debouncedFn.pending.value).toBe(false)

      debouncedFn('test')
      await nextTick()
      expect(debouncedFn.pending.value).toBe(true)

      vi.advanceTimersByTime(300)
      await nextTick()
      expect(debouncedFn.pending.value).toBe(false)
    })

    it('should maintain pending state during delay resets', async () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('first')
      await nextTick()
      expect(debouncedFn.pending.value).toBe(true)

      vi.advanceTimersByTime(200)
      debouncedFn('second')
      await nextTick()
      expect(debouncedFn.pending.value).toBe(true)

      vi.advanceTimersByTime(300)
      await nextTick()
      expect(debouncedFn.pending.value).toBe(false)
    })
  })

  describe('useDebounce cancel functionality', () => {
    it('should cancel pending execution', async () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('test')
      await nextTick()
      expect(debouncedFn.pending.value).toBe(true)

      debouncedFn.cancel()
      await nextTick()
      expect(debouncedFn.pending.value).toBe(false)

      vi.advanceTimersByTime(300)
      expect(mockFn).not.toHaveBeenCalled()
    })

    it('should handle cancel when no execution is pending', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      expect(() => debouncedFn.cancel()).not.toThrow()
    })
  })

  describe('useDebounce flush functionality', () => {
    it('should immediately execute pending function', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('test')
      expect(mockFn).not.toHaveBeenCalled()

      debouncedFn.flush()
      expect(mockFn).toHaveBeenCalledWith('test')
    })

    it('should clear pending state after flush', async () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('test')
      await nextTick()
      expect(debouncedFn.pending.value).toBe(true)

      debouncedFn.flush()
      await nextTick()
      expect(debouncedFn.pending.value).toBe(false)
    })

    it('should handle flush when no execution is pending', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      expect(() => debouncedFn.flush()).not.toThrow()
      expect(mockFn).not.toHaveBeenCalled()
    })

    it('should use latest arguments for flush', () => {
      const mockFn = vi.fn()
      const debouncedFn = useDebounce(mockFn, 300)

      debouncedFn('first')
      debouncedFn('second')
      debouncedFn('third')

      debouncedFn.flush()
      expect(mockFn).toHaveBeenCalledWith('third')
      expect(mockFn).toHaveBeenCalledTimes(1)
    })
  })
})

describe('useDebouncedRef', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('should create reactive ref with debounced callback', async () => {
    const callback = vi.fn()
    const { value, setValue } = useDebouncedRef('initial', callback, 300)

    expect(value.value).toBe('initial')
    expect(callback).not.toHaveBeenCalled()

    setValue('new value')
    expect(value.value).toBe('new value')
    expect(callback).not.toHaveBeenCalled()

    vi.advanceTimersByTime(300)
    expect(callback).toHaveBeenCalledWith('new value')
  })

  it('should provide access to debounced function methods', async () => {
    const callback = vi.fn()
    const { setValue, pending, cancel, flush } = useDebouncedRef('initial', callback, 300)

    expect(pending.value).toBe(false)

    setValue('test')
    await nextTick()
    expect(pending.value).toBe(true)

    cancel()
    await nextTick()
    expect(pending.value).toBe(false)
    expect(callback).not.toHaveBeenCalled()
  })

  it('should handle flush correctly', () => {
    const callback = vi.fn()
    const { setValue, flush } = useDebouncedRef('initial', callback, 300)

    setValue('flushed value')
    flush()
    expect(callback).toHaveBeenCalledWith('flushed value')
  })

  it('should support different types', () => {
    const stringCallback = vi.fn()
    const numberCallback = vi.fn()
    const objectCallback = vi.fn()

    const stringRef = useDebouncedRef('', stringCallback, 100)
    const numberRef = useDebouncedRef(0, numberCallback, 100)
    const objectRef = useDebouncedRef({}, objectCallback, 100)

    stringRef.setValue('test')
    numberRef.setValue(42)
    objectRef.setValue({ key: 'value' })

    vi.advanceTimersByTime(100)

    expect(stringCallback).toHaveBeenCalledWith('test')
    expect(numberCallback).toHaveBeenCalledWith(42)
    expect(objectCallback).toHaveBeenCalledWith({ key: 'value' })
  })
})

describe('useDebouncedApiCall', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('should create debounced API call with initial state', () => {
    const mockApiCall = vi.fn().mockResolvedValue({ data: 'success' })
    const { loading, error, pending } = useDebouncedApiCall(mockApiCall, 300)

    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
    expect(pending.value).toBe(false)
  })

  it('should debounce API calls correctly', async () => {
    const mockApiCall = vi.fn().mockResolvedValue({ data: 'success' })
    const { call, pending } = useDebouncedApiCall(mockApiCall, 300)

    call('arg1', 'arg2')
    await nextTick()
    expect(pending.value).toBe(true)
    expect(mockApiCall).not.toHaveBeenCalled()

    vi.advanceTimersByTime(300)
    expect(mockApiCall).toHaveBeenCalledWith('arg1', 'arg2')
  })

  it('should provide access to debounced function methods', () => {
    const mockApiCall = vi.fn().mockResolvedValue({})
    const { call, cancel, flush } = useDebouncedApiCall(mockApiCall, 300)

    call('test')
    cancel()
    expect(mockApiCall).not.toHaveBeenCalled()

    call('test2')
    flush()
    expect(mockApiCall).toHaveBeenCalledWith('test2')
  })

  it('should use default delay when not specified', () => {
    const mockApiCall = vi.fn().mockResolvedValue({})
    const { call } = useDebouncedApiCall(mockApiCall) // No delay specified

    call('test')
    vi.advanceTimersByTime(499)
    expect(mockApiCall).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(mockApiCall).toHaveBeenCalledWith('test')
  })
  
  it('should track loading state during API calls', () => {
    const mockApiCall = vi.fn().mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve({ data: 'success' }), 100)
      })
    })
    const { call, loading } = useDebouncedApiCall(mockApiCall, 300)

    expect(loading.value).toBe(false)
    
    call('test')
    vi.advanceTimersByTime(300)
    
    // Should be loading immediately after debounce triggers
    expect(loading.value).toBe(true)
    expect(mockApiCall).toHaveBeenCalledWith('test')
  })
})

describe('DEBOUNCE_DELAYS constants', () => {
  it('should define proper delay constants', () => {
    expect(DEBOUNCE_DELAYS.SEARCH).toBe(300)
    expect(DEBOUNCE_DELAYS.VALIDATION).toBe(500)
    expect(DEBOUNCE_DELAYS.SETTINGS).toBe(200)
    expect(DEBOUNCE_DELAYS.API_CALLS).toBe(500)
    expect(DEBOUNCE_DELAYS.FILE_UPLOAD).toBe(1000)
  })

  it('should have reasonable delay values', () => {
    // Ensure all delays are positive and reasonable
    Object.values(DEBOUNCE_DELAYS).forEach((delay) => {
      expect(delay).toBeGreaterThan(0)
      expect(delay).toBeLessThanOrEqual(2000) // Max 2 seconds seems reasonable
    })
  })
})

describe('useDebounce edge cases and advanced usage', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('should handle function that throws an error', () => {
    const mockFn = vi.fn().mockImplementation(() => {
      throw new Error('Function error')
    })
    const debouncedFn = useDebounce(mockFn, 300)

    debouncedFn('test')
    expect(() => {
      vi.advanceTimersByTime(300)
    }).toThrow('Function error')
  })

  it('should handle async functions correctly', async () => {
    const mockAsyncFn = vi.fn().mockResolvedValue('result')
    const debouncedFn = useDebounce(mockAsyncFn, 300)

    debouncedFn('test')
    vi.advanceTimersByTime(300)

    expect(mockAsyncFn).toHaveBeenCalledWith('test')

    // The debounced function doesn't await the async function
    // but it should still call it
    await nextTick()
    expect(mockAsyncFn).toHaveBeenCalledTimes(1)
  })

  it('should handle zero delay', () => {
    const mockFn = vi.fn()
    const debouncedFn = useDebounce(mockFn, 0)

    debouncedFn('test')
    vi.advanceTimersByTime(0)
    expect(mockFn).toHaveBeenCalledWith('test')
  })

  it('should handle very large delays', () => {
    const mockFn = vi.fn()
    const debouncedFn = useDebounce(mockFn, 10000) // 10 seconds

    debouncedFn('test')
    vi.advanceTimersByTime(9999)
    expect(mockFn).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(mockFn).toHaveBeenCalledWith('test')
  })

  it('should handle rapid successive calls efficiently', () => {
    const mockFn = vi.fn()
    const debouncedFn = useDebounce(mockFn, 300)

    // Simulate rapid typing
    for (let i = 0; i < 100; i++) {
      debouncedFn(`call-${i}`)
      vi.advanceTimersByTime(10) // 10ms between each call
    }

    // Should not have been called yet
    expect(mockFn).not.toHaveBeenCalled()

    // Advance to complete the debounce
    vi.advanceTimersByTime(300)

    // Should only be called once with the last value
    expect(mockFn).toHaveBeenCalledTimes(1)
    expect(mockFn).toHaveBeenCalledWith('call-99')
  })
})

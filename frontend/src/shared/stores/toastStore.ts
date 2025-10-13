/**
 * Toast Notification Store
 * Ham Dog & TC's notification system for user feedback
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<Toast[]>([])
  let nextId = 1

  function addToast(toast: Omit<Toast, 'id'>) {
    const id = `toast-${nextId++}`
    const newToast: Toast = {
      id,
      duration: 5000, // Default 5 seconds
      ...toast
    }
    
    toasts.value.push(newToast)
    
    // Auto-remove after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }
    
    return id
  }

  function removeToast(id: string) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index >= 0) {
      toasts.value.splice(index, 1)
    }
  }

  function success(title: string, message?: string) {
    return addToast({
      type: 'success',
      title,
      message,
      duration: 3000 // Success messages disappear faster
    })
  }

  function error(title: string, message?: string) {
    return addToast({
      type: 'error',
      title,
      message,
      duration: 7000 // Error messages stay longer
    })
  }

  function warning(title: string, message?: string) {
    return addToast({
      type: 'warning',
      title,
      message,
      duration: 5000
    })
  }

  function info(title: string, message?: string) {
    return addToast({
      type: 'info',
      title,
      message,
      duration: 4000
    })
  }

  function clearAll() {
    toasts.value = []
  }

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
    clearAll
  }
})
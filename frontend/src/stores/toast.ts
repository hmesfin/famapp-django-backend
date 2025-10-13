import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastAction {
  label: string
  onClick: () => void
}

export interface Toast {
  id: string
  type: ToastType
  title?: string
  message: string
  duration?: number
  action?: ToastAction
  persistent?: boolean
  createdAt: number
}

export interface ToastOptions {
  title?: string
  duration?: number
  action?: ToastAction
  persistent?: boolean
}

const DEFAULT_DURATION = 4000

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<Toast[]>([])
  const maxToasts = ref(5)

  const addToast = (type: ToastType, message: string, options: ToastOptions = {}) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    const toast: Toast = {
      id,
      type,
      message,
      title: options.title,
      duration: options.persistent ? undefined : (options.duration ?? DEFAULT_DURATION),
      action: options.action,
      persistent: options.persistent,
      createdAt: Date.now()
    }

    // Remove oldest toasts if we exceed max
    if (toasts.value.length >= maxToasts.value) {
      const nonPersistent = toasts.value.filter(t => !t.persistent)
      if (nonPersistent.length > 0) {
        removeToast(nonPersistent[0].id)
      }
    }

    toasts.value.push(toast)

    // Auto remove after duration
    if (!toast.persistent && toast.duration) {
      setTimeout(() => {
        removeToast(id)
      }, toast.duration)
    }

    return id
  }

  const removeToast = (id: string) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    toasts.value = []
  }

  const success = (message: string, options?: ToastOptions) => {
    return addToast('success', message, options)
  }

  const error = (message: string, options?: ToastOptions) => {
    return addToast('error', message, { duration: 6000, ...options })
  }

  const warning = (message: string, options?: ToastOptions) => {
    return addToast('warning', message, options)
  }

  const info = (message: string, options?: ToastOptions) => {
    return addToast('info', message, options)
  }

  return {
    toasts,
    maxToasts,
    addToast,
    removeToast,
    clearAll,
    success,
    error,
    warning,
    info
  }
})
import { useToastStore } from '@/stores/toast'
import type { ToastOptions } from '@/stores/toast'

/**
 * Composable for showing toast notifications
 * 
 * @example
 * const { toast } = useToast()
 * 
 * // Simple usage
 * toast.success('Changes saved!')
 * toast.error('Something went wrong')
 * 
 * // With options
 * toast.warning('Unsaved changes', {
 *   duration: 10000,
 *   action: {
 *     label: 'Save',
 *     onClick: () => saveChanges()
 *   }
 * })
 * 
 * // Persistent toast (won't auto-dismiss)
 * toast.info('New version available', {
 *   persistent: true,
 *   action: {
 *     label: 'Refresh',
 *     onClick: () => window.location.reload()
 *   }
 * })
 */
export function useToast() {
  const toastStore = useToastStore()

  const toast = {
    success: (message: string, options?: ToastOptions) => 
      toastStore.success(message, options),
    
    error: (message: string, options?: ToastOptions) => 
      toastStore.error(message, options),
    
    warning: (message: string, options?: ToastOptions) => 
      toastStore.warning(message, options),
    
    info: (message: string, options?: ToastOptions) => 
      toastStore.info(message, options),
    
    // Preset for email verification
    emailVerificationRequired: (email: string, onResend?: () => void) => {
      return toastStore.warning('Email verification required', {
        title: 'Verify Your Email',
        duration: 8000,
        action: onResend ? {
          label: 'Resend Email',
          onClick: onResend
        } : undefined
      })
    },
    
    // Preset for email sent
    emailSent: (email: string) => {
      return toastStore.success(`Verification email sent to ${email}`, {
        title: 'Email Sent',
        duration: 5000
      })
    },
    
    // Preset for login success
    loginSuccess: (userName?: string) => {
      return toastStore.success(
        userName ? `Welcome back, ${userName}!` : 'Login successful!',
        { duration: 3000 }
      )
    },
    
    // Preset for logout
    logoutSuccess: () => {
      return toastStore.info('You have been logged out', {
        duration: 3000
      })
    },
    
    // Clear all toasts
    clear: () => toastStore.clearAll()
  }

  return {
    toast,
    toasts: toastStore.toasts,
    removeToast: toastStore.removeToast,
    clearAll: toastStore.clearAll
  }
}
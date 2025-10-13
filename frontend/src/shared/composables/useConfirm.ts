import { ref, createApp, h } from 'vue'
import ConfirmDialog from '@/shared/components/ConfirmDialog.vue'
import type { ConfirmType } from '@/shared/components/ConfirmDialog.vue'

export interface ConfirmOptions {
  title?: string
  message: string
  description?: string
  type?: ConfirmType
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void | Promise<void>
  onCancel?: () => void
}

/**
 * Composable for showing confirmation dialogs
 * 
 * @example
 * const { confirm } = useConfirm()
 * 
 * // Basic usage
 * const result = await confirm({
 *   message: 'Are you sure you want to logout?'
 * })
 * 
 * // With async action
 * const result = await confirm({
 *   title: 'Delete Item',
 *   message: 'This action cannot be undone.',
 *   type: 'danger',
 *   confirmText: 'Delete',
 *   onConfirm: async () => {
 *     await api.deleteItem(id)
 *   }
 * })
 */
export function useConfirm() {
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      // Create container for the dialog
      const container = document.createElement('div')
      document.body.appendChild(container)

      let app: ReturnType<typeof createApp> | null = null
      const isOpen = ref(true)
      const loading = ref(false)

      const cleanup = () => {
        if (app) {
          app.unmount()
          document.body.removeChild(container)
          app = null
        }
      }

      const handleConfirm = async () => {
        try {
          loading.value = true
          
          // Execute onConfirm callback if provided
          if (options.onConfirm) {
            await options.onConfirm()
          }
          
          isOpen.value = false
          setTimeout(() => {
            cleanup()
            resolve(true)
          }, 300) // Wait for animation
        } catch (error) {
          // If onConfirm throws, keep dialog open
          loading.value = false
          console.error('Confirm action failed:', error)
          throw error
        }
      }

      const handleCancel = () => {
        // Execute onCancel callback if provided
        if (options.onCancel) {
          options.onCancel()
        }
        
        isOpen.value = false
        setTimeout(() => {
          cleanup()
          resolve(false)
        }, 300) // Wait for animation
      }

      // Create and mount the confirm dialog
      app = createApp({
        render() {
          return h(ConfirmDialog, {
            isOpen: isOpen.value,
            title: options.title,
            message: options.message,
            description: options.description,
            type: options.type || 'basic',
            confirmText: options.confirmText,
            cancelText: options.cancelText,
            loading: loading.value,
            onConfirm: handleConfirm,
            onCancel: handleCancel
          })
        }
      })

      app.mount(container)
    })
  }

  /**
   * Preset for logout confirmation
   */
  const confirmLogout = () => {
    return confirm({
      title: 'Logout',
      message: 'Are you sure you want to logout?',
      description: 'You will need to login again to access your account.',
      type: 'warning',
      confirmText: 'Logout',
      cancelText: 'Stay logged in'
    })
  }

  /**
   * Preset for delete confirmation
   */
  const confirmDelete = (itemName?: string) => {
    return confirm({
      title: 'Delete Item',
      message: itemName 
        ? `Are you sure you want to delete "${itemName}"?`
        : 'Are you sure you want to delete this item?',
      description: 'This action cannot be undone.',
      type: 'delete',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    })
  }

  /**
   * Preset for save confirmation
   */
  const confirmSave = () => {
    return confirm({
      title: 'Unsaved Changes',
      message: 'You have unsaved changes. Do you want to save them?',
      type: 'warning',
      confirmText: 'Save',
      cancelText: "Don't save"
    })
  }

  return {
    confirm,
    confirmLogout,
    confirmDelete,
    confirmSave
  }
}
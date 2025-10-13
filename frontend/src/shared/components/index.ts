/**
 * Shared Components
 *
 * Export all reusable components that can be used across different modules
 * All components follow consistent design system patterns with semantic colors,
 * proper accessibility, and TypeScript support.
 */

// ============================================================================
// BASE DESIGN SYSTEM COMPONENTS
// ============================================================================

// Form Components
export { default as BaseButton } from './BaseButton.vue'
export { default as BaseInput } from './BaseInput.vue'
export { default as BaseSelect } from './BaseSelect.vue'
export { default as BaseCheckbox } from './BaseCheckbox.vue'

// Layout Components
export { default as BaseCard } from './BaseCard.vue'
export { default as BaseModal } from './BaseModal.vue'

// UI Elements
export { default as BaseBadge } from './BaseBadge.vue'

// ============================================================================
// FEEDBACK COMPONENTS
// ============================================================================

// Loading & Status
export { default as LoadingSpinner } from './LoadingSpinner.vue'
export { default as SkeletonLoader } from './SkeletonLoader.vue'
export { default as EmptyState } from './EmptyState.vue'
export { default as ErrorMessage } from './ErrorMessage.vue'

// Dialogs & Confirmations
export { default as ConfirmDialog } from './ConfirmDialog.vue'

// Notifications (Toast System)
export { default as Toast } from './Toast.vue'
export { default as ToastContainer } from './ToastContainer.vue'
export { default as ToastNotifications } from './ToastNotifications.vue'

// ============================================================================
// UTILITY COMPONENTS
// ============================================================================

export { default as PlaceholderView } from './PlaceholderView.vue'

// ============================================================================
// TYPE EXPORTS
// ============================================================================

// Re-export types for better developer experience
export type { ConfirmType } from './ConfirmDialog.vue'

<template>
  <teleport to="body">
    <transition
      name="modal"
      enter-active-class="duration-300 ease-smooth"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-200 ease-smooth"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="show" 
        :class="overlayClasses"
        @click="handleOverlayClick"
        role="dialog"
        :aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="bodyId"
      >
        <div :class="containerClasses">
          <!-- Background overlay -->
          <div :class="backdropClasses" />

          <!-- Modal panel -->
          <transition
            name="modal-panel"
            enter-active-class="duration-300 ease-smooth"
            enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to-class="opacity-100 translate-y-0 sm:scale-100"
            leave-active-class="duration-200 ease-smooth"
            leave-from-class="opacity-100 translate-y-0 sm:scale-100"
            leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              v-if="show"
              ref="modalRef"
              :class="modalClasses"
              @click.stop
            >
              <!-- Header -->
              <div
                v-if="showHeader"
                :class="headerClasses"
              >
                <div class="flex items-center justify-between">
                  <slot name="header">
                    <h3 
                      :id="titleId"
                      :class="titleClasses"
                    >
                      {{ title }}
                    </h3>
                  </slot>
                  <button
                    v-if="showCloseButton"
                    ref="closeButtonRef"
                    type="button"
                    :class="closeButtonClasses"
                    @click="handleClose"
                    aria-label="Close modal"
                  >
                    <XMarkIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>

              <!-- Body -->
              <div 
                :id="bodyId"
                :class="bodyClasses"
              >
                <slot />
              </div>

              <!-- Footer -->
              <div
                v-if="$slots.footer"
                :class="footerClasses"
              >
                <div class="flex justify-end space-x-3">
                  <slot name="footer" />
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch, onMounted, onUnmounted, useSlots } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

type ModalSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'

interface Props {
  show: boolean
  title?: string
  size?: ModalSize
  showCloseButton?: boolean
  closeOnOverlayClick?: boolean
  persistent?: boolean
  padding?: boolean
  headerPadding?: boolean
  bodyPadding?: boolean
  footerPadding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showCloseButton: true,
  closeOnOverlayClick: true,
  persistent: false,
  padding: true,
  headerPadding: true,
  bodyPadding: true,
  footerPadding: true
})

const emit = defineEmits<{
  close: []
  opened: []
  closed: []
}>()

// Refs
const modalRef = ref<HTMLDivElement>()
const closeButtonRef = ref<HTMLButtonElement>()
const previousActiveElement = ref<HTMLElement | null>(null)

// Computed IDs
const titleId = computed(() => `modal-title-${Math.random().toString(36).substr(2, 9)}`)
const bodyId = computed(() => `modal-body-${Math.random().toString(36).substr(2, 9)}`)

// Show header
const showHeader = computed(() => props.title || props.showCloseButton || !!useSlots().header)

// Size classes
const sizeClasses = {
  xs: 'sm:max-w-xs sm:w-full',
  sm: 'sm:max-w-sm sm:w-full',
  md: 'sm:max-w-md sm:w-full',
  lg: 'sm:max-w-lg sm:w-full',
  xl: 'sm:max-w-xl sm:w-full',
  '2xl': 'sm:max-w-2xl sm:w-full',
  full: 'sm:max-w-full sm:w-full sm:h-full'
}

// Padding classes
const paddingClasses = {
  header: 'px-6 py-4',
  body: 'px-6 py-4',
  footer: 'px-6 py-4'
}

// Component classes
const overlayClasses = [
  'fixed',
  'inset-0',
  'z-50',
  'overflow-y-auto',
  'overflow-x-hidden'
]

const containerClasses = [
  'flex',
  'min-h-full',
  'items-center',
  'justify-center',
  'p-4',
  'text-center',
  'sm:p-0'
]

const backdropClasses = [
  'fixed',
  'inset-0',
  'bg-secondary-900',
  'bg-opacity-75',
  'transition-opacity',
  'dark:bg-secondary-900',
  'dark:bg-opacity-90'
]

const modalClasses = computed(() => [
  'relative',
  'inline-block',
  'align-bottom',
  'bg-white',
  'rounded-lg',
  'text-left',
  'overflow-hidden',
  'shadow-modal',
  'transform',
  'transition-all',
  'sm:my-8',
  'sm:align-middle',
  'w-full',
  sizeClasses[props.size],
  'dark:bg-secondary-800',
  {
    'sm:h-full': props.size === 'full'
  }
])

const headerClasses = computed(() => [
  'border-b',
  'border-secondary-200',
  'dark:border-secondary-700',
  {
    [paddingClasses.header]: props.padding && props.headerPadding
  }
])

const titleClasses = [
  'text-lg',
  'font-semibold',
  'text-secondary-900',
  'leading-6',
  'dark:text-secondary-100'
]

const closeButtonClasses = [
  'rounded-md',
  'p-2',
  'text-secondary-400',
  'hover:text-secondary-600',
  'hover:bg-secondary-100',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-primary-500',
  'focus:ring-offset-2',
  'transition-colors',
  'duration-200',
  'dark:text-secondary-500',
  'dark:hover:text-secondary-300',
  'dark:hover:bg-secondary-700',
  'dark:focus:ring-offset-secondary-800'
]

const bodyClasses = computed(() => [
  {
    [paddingClasses.body]: props.padding && props.bodyPadding
  }
])

const footerClasses = computed(() => [
  'border-t',
  'border-secondary-200',
  'bg-secondary-50',
  'dark:border-secondary-700',
  'dark:bg-secondary-800',
  {
    [paddingClasses.footer]: props.padding && props.footerPadding
  }
])

// Focus management
const focusableElementsSelector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'

const getFocusableElements = (): HTMLElement[] => {
  if (!modalRef.value) return []
  return Array.from(modalRef.value.querySelectorAll(focusableElementsSelector)) as HTMLElement[]
}

const trapFocus = (event: KeyboardEvent) => {
  if (event.key !== 'Tab') return

  const focusableElements = getFocusableElements()
  if (focusableElements.length === 0) return

  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  if (event.shiftKey) {
    if (document.activeElement === firstElement) {
      lastElement.focus()
      event.preventDefault()
    }
  } else {
    if (document.activeElement === lastElement) {
      firstElement.focus()
      event.preventDefault()
    }
  }
}

// Event handlers
const handleOverlayClick = () => {
  if (props.closeOnOverlayClick && !props.persistent) {
    handleClose()
  }
}

const handleClose = () => {
  emit('close')
}

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.show && !props.persistent) {
    handleClose()
  }
}

// Focus initial element when modal opens
const focusInitialElement = async () => {
  await nextTick()
  if (!modalRef.value) return

  // Try to focus close button first, then any focusable element
  if (closeButtonRef.value) {
    closeButtonRef.value.focus()
  } else {
    const focusableElements = getFocusableElements()
    if (focusableElements.length > 0) {
      focusableElements[0].focus()
    }
  }
}

// Watch for show changes
watch(() => props.show, async (isOpen) => {
  if (isOpen) {
    // Store the currently focused element
    previousActiveElement.value = document.activeElement as HTMLElement
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden'
    
    // Focus the modal
    await focusInitialElement()
    
    emit('opened')
  } else {
    // Restore body scroll
    document.body.style.overflow = ''
    
    // Return focus to previous element
    if (previousActiveElement.value) {
      previousActiveElement.value.focus()
    }
    
    emit('closed')
  }
})

// Keyboard event listeners
onMounted(() => {
  document.addEventListener('keydown', handleEscape)
  document.addEventListener('keydown', trapFocus)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('keydown', trapFocus)
  
  // Ensure body scroll is restored
  document.body.style.overflow = ''
})
</script>

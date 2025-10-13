<template>
  <transition
    name="alert"
    enter-active-class="transition-all duration-300 ease-smooth"
    enter-from-class="opacity-0 transform scale-95"
    enter-to-class="opacity-100 transform scale-100"
    leave-active-class="transition-all duration-200 ease-smooth"
    leave-from-class="opacity-100 transform scale-100"
    leave-to-class="opacity-0 transform scale-95"
  >
    <div v-if="show" :class="containerClasses" role="alert" :aria-live="ariaLive">
      <div class="flex">
        <div class="flex-shrink-0">
          <component :is="iconComponent" :class="iconClasses" />
        </div>
        
        <div class="ml-3 flex-1">
          <h3 v-if="title" :class="titleClasses">
            {{ title }}
          </h3>
          
          <div :class="messageClasses">
            <div v-if="message" v-html="message" />
            <slot v-else />
          </div>
          
          <!-- Action buttons using BaseButton -->
          <div v-if="$slots.actions || (dismissible && showDismissButton)" :class="actionsClasses">
            <slot name="actions" />
            <BaseButton
              v-if="dismissible && showDismissButton"
              :variant="dismissButtonVariant"
              size="xs"
              @click="handleDismiss"
            >
              {{ dismissText }}
            </BaseButton>
          </div>
        </div>
        
        <!-- Close button -->
        <div v-if="dismissible" class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              type="button"
              :class="closeButtonClasses"
              @click="handleDismiss"
              aria-label="Dismiss"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from './BaseButton.vue'
import {
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/vue/20/solid'

type AlertSeverity = 'error' | 'warning' | 'info' | 'success'
type AlertVariant = 'default' | 'filled' | 'outlined' | 'minimal'
type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'ghost' | 'outline'

interface Props {
  // Content
  type?: AlertSeverity
  title?: string
  message?: string
  
  // Behavior
  dismissible?: boolean
  show?: boolean
  showDismissButton?: boolean
  dismissText?: string
  persistent?: boolean
  
  // Styling
  variant?: AlertVariant
  
  // Accessibility
  ariaLive?: 'polite' | 'assertive' | 'off'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'error',
  dismissible: false,
  show: true,
  showDismissButton: true,
  dismissText: 'Dismiss',
  persistent: false,
  variant: 'default',
  ariaLive: 'polite'
})

const emit = defineEmits<{
  dismiss: []
}>()

// Icon mapping
const iconComponents = {
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
  success: CheckCircleIcon
}

const iconComponent = computed(() => iconComponents[props.type])

// Type styles using semantic colors
const typeStyles = {
  error: {
    container: {
      default: [
        'bg-danger-50',
        'border',
        'border-danger-200',
        'dark:bg-danger-900',
        'dark:bg-opacity-20',
        'dark:border-danger-800'
      ],
      filled: [
        'bg-danger-600',
        'border',
        'border-danger-600'
      ],
      outlined: [
        'bg-white',
        'border-2',
        'border-danger-300',
        'dark:bg-secondary-800',
        'dark:border-danger-700'
      ],
      minimal: [
        'bg-transparent',
        'border-l-4',
        'border-l-danger-400',
        'pl-4'
      ]
    },
    icon: [
      'text-danger-400',
      'h-5',
      'w-5',
      'dark:text-danger-400'
    ],
    title: [
      'text-danger-800',
      'dark:text-danger-200'
    ],
    message: [
      'text-danger-700',
      'dark:text-danger-300'
    ],
    closeButton: [
      'text-danger-500',
      'hover:text-danger-600',
      'hover:bg-danger-100',
      'focus:ring-danger-500',
      'dark:text-danger-400',
      'dark:hover:text-danger-300',
      'dark:hover:bg-danger-900',
      'dark:hover:bg-opacity-20'
    ]
  },
  warning: {
    container: {
      default: [
        'bg-warning-50',
        'border',
        'border-warning-200',
        'dark:bg-warning-900',
        'dark:bg-opacity-20',
        'dark:border-warning-800'
      ],
      filled: [
        'bg-warning-600',
        'border',
        'border-warning-600'
      ],
      outlined: [
        'bg-white',
        'border-2',
        'border-warning-300',
        'dark:bg-secondary-800',
        'dark:border-warning-700'
      ],
      minimal: [
        'bg-transparent',
        'border-l-4',
        'border-l-warning-400',
        'pl-4'
      ]
    },
    icon: [
      'text-warning-400',
      'h-5',
      'w-5',
      'dark:text-warning-400'
    ],
    title: [
      'text-warning-800',
      'dark:text-warning-200'
    ],
    message: [
      'text-warning-700',
      'dark:text-warning-300'
    ],
    closeButton: [
      'text-warning-500',
      'hover:text-warning-600',
      'hover:bg-warning-100',
      'focus:ring-warning-500',
      'dark:text-warning-400',
      'dark:hover:text-warning-300',
      'dark:hover:bg-warning-900',
      'dark:hover:bg-opacity-20'
    ]
  },
  info: {
    container: {
      default: [
        'bg-info-50',
        'border',
        'border-info-200',
        'dark:bg-info-900',
        'dark:bg-opacity-20',
        'dark:border-info-800'
      ],
      filled: [
        'bg-info-600',
        'border',
        'border-info-600'
      ],
      outlined: [
        'bg-white',
        'border-2',
        'border-info-300',
        'dark:bg-secondary-800',
        'dark:border-info-700'
      ],
      minimal: [
        'bg-transparent',
        'border-l-4',
        'border-l-info-400',
        'pl-4'
      ]
    },
    icon: [
      'text-info-400',
      'h-5',
      'w-5',
      'dark:text-info-400'
    ],
    title: [
      'text-info-800',
      'dark:text-info-200'
    ],
    message: [
      'text-info-700',
      'dark:text-info-300'
    ],
    closeButton: [
      'text-info-500',
      'hover:text-info-600',
      'hover:bg-info-100',
      'focus:ring-info-500',
      'dark:text-info-400',
      'dark:hover:text-info-300',
      'dark:hover:bg-info-900',
      'dark:hover:bg-opacity-20'
    ]
  },
  success: {
    container: {
      default: [
        'bg-success-50',
        'border',
        'border-success-200',
        'dark:bg-success-900',
        'dark:bg-opacity-20',
        'dark:border-success-800'
      ],
      filled: [
        'bg-success-600',
        'border',
        'border-success-600'
      ],
      outlined: [
        'bg-white',
        'border-2',
        'border-success-300',
        'dark:bg-secondary-800',
        'dark:border-success-700'
      ],
      minimal: [
        'bg-transparent',
        'border-l-4',
        'border-l-success-400',
        'pl-4'
      ]
    },
    icon: [
      'text-success-400',
      'h-5',
      'w-5',
      'dark:text-success-400'
    ],
    title: [
      'text-success-800',
      'dark:text-success-200'
    ],
    message: [
      'text-success-700',
      'dark:text-success-300'
    ],
    closeButton: [
      'text-success-500',
      'hover:text-success-600',
      'hover:bg-success-100',
      'focus:ring-success-500',
      'dark:text-success-400',
      'dark:hover:text-success-300',
      'dark:hover:bg-success-900',
      'dark:hover:bg-opacity-20'
    ]
  }
}

// Computed classes
const containerClasses = computed(() => [
  'rounded-lg',
  'p-4',
  'transition-all',
  'duration-200',
  'ease-smooth',
  ...typeStyles[props.type].container[props.variant]
])

const iconClasses = computed(() => [
  'flex-shrink-0',
  ...typeStyles[props.type].icon
])

const titleClasses = computed(() => [
  'text-sm',
  'font-semibold',
  'leading-5',
  ...typeStyles[props.type].title
])

const messageClasses = computed(() => [
  'text-sm',
  'leading-5',
  {
    'mt-2': props.title
  },
  ...typeStyles[props.type].message
])

const actionsClasses = [
  'mt-4',
  'flex',
  'items-center',
  'space-x-3'
]

const closeButtonClasses = computed(() => [
  'inline-flex',
  'rounded-md',
  'p-1.5',
  'transition-colors',
  'duration-200',
  'ease-smooth',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-offset-2',
  ...typeStyles[props.type].closeButton
])

// Button variant for dismiss button
const dismissButtonVariant = computed((): ButtonVariant => {
  const variantMap: Record<AlertSeverity, ButtonVariant> = {
    error: 'danger',
    warning: 'warning',
    info: 'info',
    success: 'success'
  }
  return variantMap[props.type]
})

// Event handlers
const handleDismiss = () => {
  emit('dismiss')
}
</script>
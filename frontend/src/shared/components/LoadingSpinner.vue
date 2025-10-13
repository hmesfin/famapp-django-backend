<template>
  <div :class="containerClasses">
    <!-- Spinner -->
    <div :class="spinnerWrapperClasses">
      <svg
        :class="spinnerClasses"
        fill="none"
        viewBox="0 0 24 24"
        :aria-hidden="!srOnly"
        :aria-label="ariaLabel"
        role="status"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          :stroke-width="strokeWidth"
          :class="circleClasses"
        />
        <path
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          :class="pathClasses"
        />
      </svg>
    </div>

    <!-- Message/Label -->
    <div v-if="message || label" :class="textClasses">
      <p v-if="message" :class="messageClasses">
        {{ message }}
      </p>
      <p v-if="label && !message" :class="labelClasses">
        {{ label }}
      </p>
    </div>

    <!-- Screen reader text -->
    <span v-if="srOnly" class="sr-only">{{ srText }}</span>

    <!-- Overlay backdrop -->
    <div v-if="overlay" :class="overlayClasses" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
type SpinnerVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'white' | 'current'
type SpinnerStyle = 'default' | 'dots' | 'pulse' | 'bars'

interface Props {
  // Sizing
  size?: SpinnerSize
  
  // Styling
  variant?: SpinnerVariant
  style?: SpinnerStyle
  strokeWidth?: number
  
  // Content
  message?: string
  label?: string
  
  // Layout
  center?: boolean
  inline?: boolean
  
  // Overlay
  overlay?: boolean
  overlayOpacity?: number
  
  // Accessibility
  ariaLabel?: string
  srOnly?: boolean
  srText?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'primary',
  style: 'default',
  strokeWidth: 4,
  center: false,
  inline: false,
  overlay: false,
  overlayOpacity: 75,
  srOnly: true,
  srText: 'Loading...'
})

// Size configurations
const sizeConfigs = {
  xs: {
    spinner: 'h-3 w-3',
    strokeWidth: 2,
    text: 'text-xs'
  },
  sm: {
    spinner: 'h-4 w-4',
    strokeWidth: 2,
    text: 'text-sm'
  },
  md: {
    spinner: 'h-6 w-6',
    strokeWidth: 3,
    text: 'text-sm'
  },
  lg: {
    spinner: 'h-8 w-8',
    strokeWidth: 3,
    text: 'text-base'
  },
  xl: {
    spinner: 'h-12 w-12',
    strokeWidth: 4,
    text: 'text-lg'
  },
  '2xl': {
    spinner: 'h-16 w-16',
    strokeWidth: 4,
    text: 'text-xl'
  }
}

// Color variants using semantic colors
const variantClasses = {
  primary: [
    'text-primary-600',
    'dark:text-primary-400'
  ],
  secondary: [
    'text-secondary-600',
    'dark:text-secondary-400'
  ],
  success: [
    'text-success-600',
    'dark:text-success-400'
  ],
  warning: [
    'text-warning-600',
    'dark:text-warning-400'
  ],
  danger: [
    'text-danger-600',
    'dark:text-danger-400'
  ],
  info: [
    'text-info-600',
    'dark:text-info-400'
  ],
  white: [
    'text-white'
  ],
  current: [
    'text-current'
  ]
}

// Computed stroke width
const strokeWidth = computed(() => props.strokeWidth || sizeConfigs[props.size].strokeWidth)

// Container classes
const containerClasses = computed(() => {
  const baseClasses = ['relative']
  
  if (props.overlay) {
    return [
      ...baseClasses,
      'fixed',
      'inset-0',
      'z-50',
      'flex',
      'items-center',
      'justify-center',
      'flex-col',
      'space-y-4'
    ]
  }
  
  if (props.inline) {
    return [
      ...baseClasses,
      'inline-flex',
      'items-center',
      'space-x-2'
    ]
  }
  
  const flexClasses = [
    'flex',
    'items-center'
  ]
  
  if (props.center) {
    flexClasses.push('justify-center')
  }
  
  if (props.message || props.label) {
    flexClasses.push('space-x-3')
  }
  
  if (props.center && (props.message || props.label)) {
    return [
      ...baseClasses,
      'flex',
      'flex-col',
      'items-center',
      'justify-center',
      'space-y-2'
    ]
  }
  
  return [...baseClasses, ...flexClasses]
})

// Spinner wrapper classes (for potential background)
const spinnerWrapperClasses = computed(() => [
  'flex-shrink-0'
])

// Spinner classes
const spinnerClasses = computed(() => [
  'animate-spin',
  sizeConfigs[props.size].spinner,
  ...variantClasses[props.variant]
])

// Circle classes (background circle)
const circleClasses = [
  'opacity-25'
]

// Path classes (moving part)
const pathClasses = [
  'opacity-75'
]

// Text container classes
const textClasses = computed(() => {
  if (props.center && (props.message || props.label)) {
    return ['text-center']
  }
  return []
})

// Message classes
const messageClasses = computed(() => [
  sizeConfigs[props.size].text,
  'font-medium',
  'text-secondary-900',
  'dark:text-secondary-100'
])

// Label classes (lighter than message)
const labelClasses = computed(() => [
  sizeConfigs[props.size].text,
  'font-normal',
  'text-secondary-600',
  'dark:text-secondary-400'
])

// Overlay backdrop classes
const overlayClasses = computed(() => [
  'absolute',
  'inset-0',
  '-z-10',
  'bg-white',
  `bg-opacity-${props.overlayOpacity}`,
  'backdrop-blur-sm',
  'dark:bg-secondary-900',
  `dark:bg-opacity-${props.overlayOpacity}`
])

// Computed aria label
const ariaLabel = computed(() => {
  if (props.ariaLabel) return props.ariaLabel
  if (props.message) return props.message
  if (props.label) return props.label
  return 'Loading'
})
</script>
<template>
  <component
    :is="tag"
    :class="buttonClasses"
    :disabled="disabled || loading"
    :aria-label="ariaLabel"
    :aria-describedby="ariaDescribedby"
    :type="tag === 'button' ? type : undefined"
    :href="tag === 'a' ? href : undefined"
    :to="tag === 'router-link' ? to : undefined"
    v-bind="$attrs"
    @click="handleClick"
  >
    <!-- Loading state -->
    <div v-if="loading" class="flex items-center">
      <svg
        class="animate-spin -ml-1 mr-2 h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span>{{ loadingText || 'Loading...' }}</span>
    </div>

    <!-- Normal state -->
    <div v-else class="flex items-center justify-center">
      <!-- Leading icon -->
      <component
        :is="leadingIcon"
        v-if="leadingIcon && !loading"
        :class="iconClasses"
        class="mr-2"
      />

      <!-- Button content -->
      <span v-if="$slots.default || content">
        <slot>{{ content }}</slot>
      </span>

      <!-- Trailing icon -->
      <component
        :is="trailingIcon"
        v-if="trailingIcon && !loading"
        :class="iconClasses"
        class="ml-2"
      />
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'ghost' | 'outline'
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
type ButtonTag = 'button' | 'a' | 'router-link'
type ButtonType = 'button' | 'submit' | 'reset'

interface Props {
  // Content
  content?: string
  
  // Styling
  variant?: ButtonVariant
  size?: ButtonSize
  
  // State
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  
  // Icons
  leadingIcon?: Component
  trailingIcon?: Component
  
  // HTML attributes
  tag?: ButtonTag
  type?: ButtonType
  href?: string
  to?: string | object
  
  // Accessibility
  ariaLabel?: string
  ariaDescribedby?: string
  
  // Behavior
  block?: boolean
  rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  tag: 'button',
  type: 'button',
  disabled: false,
  loading: false,
  block: false,
  rounded: false
})

const emit = defineEmits<{
  click: [event: Event]
}>()

// Base classes for all buttons
const baseClasses = [
  // Layout
  'inline-flex',
  'items-center',
  'justify-center',
  
  // Typography
  'font-medium',
  'text-center',
  
  // Interactions
  'transition-all',
  'duration-200',
  'ease-smooth',
  'cursor-pointer',
  
  // Focus states
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-offset-2',
  
  // Disabled state
  'disabled:cursor-not-allowed',
  'disabled:opacity-50',
  'disabled:pointer-events-none',
]

// Size variants
const sizeClasses = {
  xs: [
    'px-2.5',
    'py-1.5',
    'text-xs',
    'leading-4',
    'rounded',
    'min-h-[24px]'
  ],
  sm: [
    'px-3',
    'py-2',
    'text-sm',
    'leading-4',
    'rounded-md',
    'min-h-[32px]'
  ],
  md: [
    'px-4',
    'py-2.5',
    'text-sm',
    'leading-5',
    'rounded-md',
    'min-h-[40px]'
  ],
  lg: [
    'px-6',
    'py-3',
    'text-base',
    'leading-6',
    'rounded-lg',
    'min-h-[44px]'
  ],
  xl: [
    'px-8',
    'py-3.5',
    'text-base',
    'leading-6',
    'rounded-lg',
    'min-h-[48px]'
  ]
}

// Variant classes
const variantClasses = {
  primary: [
    'bg-primary-600',
    'text-white',
    'border',
    'border-primary-600',
    'shadow-button',
    'hover:bg-primary-700',
    'hover:border-primary-700',
    'hover:shadow-button-hover',
    'focus:ring-primary-500',
    'active:bg-primary-800',
    'dark:bg-primary-500',
    'dark:border-primary-500',
    'dark:hover:bg-primary-600',
    'dark:hover:border-primary-600',
    'dark:focus:ring-primary-400'
  ],
  secondary: [
    'bg-secondary-100',
    'text-secondary-900',
    'border',
    'border-secondary-200',
    'shadow-button',
    'hover:bg-secondary-200',
    'hover:border-secondary-300',
    'hover:shadow-button-hover',
    'focus:ring-secondary-500',
    'active:bg-secondary-300',
    'dark:bg-secondary-800',
    'dark:text-secondary-100',
    'dark:border-secondary-700',
    'dark:hover:bg-secondary-700',
    'dark:hover:border-secondary-600'
  ],
  success: [
    'bg-success-600',
    'text-white',
    'border',
    'border-success-600',
    'shadow-button',
    'hover:bg-success-700',
    'hover:border-success-700',
    'hover:shadow-button-hover',
    'focus:ring-success-500',
    'active:bg-success-800'
  ],
  warning: [
    'bg-warning-500',
    'text-white',
    'border',
    'border-warning-500',
    'shadow-button',
    'hover:bg-warning-600',
    'hover:border-warning-600',
    'hover:shadow-button-hover',
    'focus:ring-warning-500',
    'active:bg-warning-700'
  ],
  danger: [
    'bg-danger-600',
    'text-white',
    'border',
    'border-danger-600',
    'shadow-button',
    'hover:bg-danger-700',
    'hover:border-danger-700',
    'hover:shadow-button-hover',
    'focus:ring-danger-500',
    'active:bg-danger-800'
  ],
  info: [
    'bg-info-600',
    'text-white',
    'border',
    'border-info-600',
    'shadow-button',
    'hover:bg-info-700',
    'hover:border-info-700',
    'hover:shadow-button-hover',
    'focus:ring-info-500',
    'active:bg-info-800'
  ],
  ghost: [
    'bg-transparent',
    'text-secondary-700',
    'border',
    'border-transparent',
    'hover:bg-secondary-100',
    'hover:text-secondary-900',
    'focus:ring-secondary-500',
    'active:bg-secondary-200',
    'dark:text-secondary-300',
    'dark:hover:bg-secondary-800',
    'dark:hover:text-secondary-100'
  ],
  outline: [
    'bg-transparent',
    'text-secondary-700',
    'border',
    'border-secondary-300',
    'shadow-button',
    'hover:bg-secondary-50',
    'hover:text-secondary-900',
    'hover:shadow-button-hover',
    'focus:ring-secondary-500',
    'active:bg-secondary-100',
    'dark:text-secondary-300',
    'dark:border-secondary-600',
    'dark:hover:bg-secondary-800',
    'dark:hover:text-secondary-100'
  ]
}

// Icon size classes based on button size
const iconSizeClasses = {
  xs: 'h-3 w-3',
  sm: 'h-4 w-4',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
  xl: 'h-5 w-5'
}

const buttonClasses = computed(() => [
  ...baseClasses,
  ...sizeClasses[props.size],
  ...variantClasses[props.variant],
  {
    'w-full': props.block,
    'rounded-full': props.rounded,
  }
])

const iconClasses = computed(() => [
  iconSizeClasses[props.size],
  'flex-shrink-0'
])

const handleClick = (event: Event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
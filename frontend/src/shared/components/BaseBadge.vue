<template>
  <component
    :is="tag"
    :class="badgeClasses"
    :href="tag === 'a' ? href : undefined"
    :to="tag === 'router-link' ? to : undefined"
    v-bind="$attrs"
  >
    <!-- Leading icon -->
    <component
      :is="leadingIcon"
      v-if="leadingIcon"
      :class="iconClasses"
      class="mr-1"
    />
    
    <!-- Badge content -->
    <span v-if="$slots.default || content">
      <slot>{{ content }}</slot>
    </span>
    
    <!-- Trailing icon -->
    <component
      :is="trailingIcon"
      v-if="trailingIcon"
      :class="iconClasses"
      class="ml-1"
    />
    
    <!-- Remove button -->
    <button
      v-if="removable"
      type="button"
      :class="removeButtonClasses"
      @click="handleRemove"
      aria-label="Remove"
    >
      <XMarkIcon :class="iconClasses" />
    </button>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/20/solid'
import type { Component } from 'vue'

type BadgeVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
type BadgeSize = 'xs' | 'sm' | 'md' | 'lg'
type BadgeStyle = 'filled' | 'outlined' | 'soft' | 'minimal'
type BadgeShape = 'rounded' | 'pill' | 'square'
type BadgeTag = 'span' | 'div' | 'a' | 'router-link' | 'button'

interface Props {
  // Content
  content?: string
  
  // Styling
  variant?: BadgeVariant
  size?: BadgeSize
  style?: BadgeStyle
  shape?: BadgeShape
  
  // Icons
  leadingIcon?: Component
  trailingIcon?: Component
  
  // Behavior
  removable?: boolean
  
  // HTML attributes
  tag?: BadgeTag
  href?: string
  to?: string | object
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  style: 'filled',
  shape: 'rounded',
  tag: 'span',
  removable: false
})

const emit = defineEmits<{
  remove: []
}>()

// Size configurations
const sizeConfigs = {
  xs: {
    badge: 'px-2 py-0.5 text-xs font-medium',
    icon: 'h-3 w-3',
    removeButton: '-mr-0.5 ml-1'
  },
  sm: {
    badge: 'px-2.5 py-0.5 text-xs font-medium',
    icon: 'h-3 w-3',
    removeButton: '-mr-0.5 ml-1.5'
  },
  md: {
    badge: 'px-3 py-1 text-sm font-medium',
    icon: 'h-4 w-4',
    removeButton: '-mr-1 ml-1.5'
  },
  lg: {
    badge: 'px-4 py-1.5 text-sm font-semibold',
    icon: 'h-4 w-4',
    removeButton: '-mr-1 ml-2'
  }
}

// Shape configurations
const shapeClasses = {
  rounded: 'rounded-md',
  pill: 'rounded-full',
  square: 'rounded-none'
}

// Variant styles
const variantStyles = {
  primary: {
    filled: [
      'bg-primary-600',
      'text-white',
      'dark:bg-primary-500'
    ],
    outlined: [
      'bg-transparent',
      'text-primary-700',
      'ring-1',
      'ring-inset',
      'ring-primary-600',
      'dark:text-primary-400',
      'dark:ring-primary-400'
    ],
    soft: [
      'bg-primary-100',
      'text-primary-800',
      'dark:bg-primary-900',
      'dark:bg-opacity-30',
      'dark:text-primary-300'
    ],
    minimal: [
      'bg-transparent',
      'text-primary-700',
      'dark:text-primary-400'
    ]
  },
  secondary: {
    filled: [
      'bg-secondary-600',
      'text-white',
      'dark:bg-secondary-500'
    ],
    outlined: [
      'bg-transparent',
      'text-secondary-700',
      'ring-1',
      'ring-inset',
      'ring-secondary-600',
      'dark:text-secondary-400',
      'dark:ring-secondary-400'
    ],
    soft: [
      'bg-secondary-100',
      'text-secondary-800',
      'dark:bg-secondary-900',
      'dark:bg-opacity-30',
      'dark:text-secondary-300'
    ],
    minimal: [
      'bg-transparent',
      'text-secondary-700',
      'dark:text-secondary-400'
    ]
  },
  success: {
    filled: [
      'bg-success-600',
      'text-white',
      'dark:bg-success-500'
    ],
    outlined: [
      'bg-transparent',
      'text-success-700',
      'ring-1',
      'ring-inset',
      'ring-success-600',
      'dark:text-success-400',
      'dark:ring-success-400'
    ],
    soft: [
      'bg-success-100',
      'text-success-800',
      'dark:bg-success-900',
      'dark:bg-opacity-30',
      'dark:text-success-300'
    ],
    minimal: [
      'bg-transparent',
      'text-success-700',
      'dark:text-success-400'
    ]
  },
  warning: {
    filled: [
      'bg-warning-600',
      'text-white',
      'dark:bg-warning-500'
    ],
    outlined: [
      'bg-transparent',
      'text-warning-700',
      'ring-1',
      'ring-inset',
      'ring-warning-600',
      'dark:text-warning-400',
      'dark:ring-warning-400'
    ],
    soft: [
      'bg-warning-100',
      'text-warning-800',
      'dark:bg-warning-900',
      'dark:bg-opacity-30',
      'dark:text-warning-300'
    ],
    minimal: [
      'bg-transparent',
      'text-warning-700',
      'dark:text-warning-400'
    ]
  },
  danger: {
    filled: [
      'bg-danger-600',
      'text-white',
      'dark:bg-danger-500'
    ],
    outlined: [
      'bg-transparent',
      'text-danger-700',
      'ring-1',
      'ring-inset',
      'ring-danger-600',
      'dark:text-danger-400',
      'dark:ring-danger-400'
    ],
    soft: [
      'bg-danger-100',
      'text-danger-800',
      'dark:bg-danger-900',
      'dark:bg-opacity-30',
      'dark:text-danger-300'
    ],
    minimal: [
      'bg-transparent',
      'text-danger-700',
      'dark:text-danger-400'
    ]
  },
  info: {
    filled: [
      'bg-info-600',
      'text-white',
      'dark:bg-info-500'
    ],
    outlined: [
      'bg-transparent',
      'text-info-700',
      'ring-1',
      'ring-inset',
      'ring-info-600',
      'dark:text-info-400',
      'dark:ring-info-400'
    ],
    soft: [
      'bg-info-100',
      'text-info-800',
      'dark:bg-info-900',
      'dark:bg-opacity-30',
      'dark:text-info-300'
    ],
    minimal: [
      'bg-transparent',
      'text-info-700',
      'dark:text-info-400'
    ]
  }
}

// Base badge classes
const baseBadgeClasses = [
  'inline-flex',
  'items-center',
  'font-medium',
  'transition-all',
  'duration-200',
  'ease-smooth'
]

// Computed classes
const badgeClasses = computed(() => {
  // Ensure variant and style exist with fallbacks
  const variant = variantStyles[props.variant] || variantStyles.primary
  const styleClasses = variant[props.style] || variant.filled || []
  
  return [
    ...baseBadgeClasses,
    sizeConfigs[props.size].badge,
    shapeClasses[props.shape],
    ...styleClasses
  ]
})

const iconClasses = computed(() => [
  sizeConfigs[props.size].icon,
  'flex-shrink-0'
])

const removeButtonClasses = computed(() => [
  'inline-flex',
  'items-center',
  'justify-center',
  'flex-shrink-0',
  'rounded-full',
  'hover:bg-black',
  'hover:bg-opacity-10',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-offset-1',
  'focus:ring-current',
  'transition-colors',
  'duration-200',
  sizeConfigs[props.size].removeButton,
  {
    'h-4 w-4': props.size === 'xs' || props.size === 'sm',
    'h-5 w-5': props.size === 'md' || props.size === 'lg'
  }
])

// Event handlers
const handleRemove = (event: Event) => {
  event.stopPropagation()
  emit('remove')
}
</script>
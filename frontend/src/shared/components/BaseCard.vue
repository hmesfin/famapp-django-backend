<template>
  <component
    :is="tag"
    :class="cardClasses"
    v-bind="$attrs"
    @click="handleClick"
  >
    <!-- Card Header -->
    <div v-if="$slots.header || title || subtitle" :class="headerClasses">
      <div v-if="$slots.header">
        <slot name="header" />
      </div>
      <div v-else>
        <h3 v-if="title" :class="titleClasses">
          {{ title }}
        </h3>
        <p v-if="subtitle" :class="subtitleClasses">
          {{ subtitle }}
        </p>
      </div>
      
      <!-- Header actions -->
      <div v-if="$slots.actions" class="flex items-center space-x-2">
        <slot name="actions" />
      </div>
    </div>

    <!-- Card Body -->
    <div v-if="$slots.default" :class="bodyClasses">
      <slot />
    </div>

    <!-- Card Footer -->
    <div v-if="$slots.footer" :class="footerClasses">
      <slot name="footer" />
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" :class="loadingOverlayClasses">
      <div class="flex items-center justify-center">
        <svg
          class="animate-spin h-8 w-8 text-primary-600"
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
      </div>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type CardVariant = 'default' | 'elevated' | 'outlined' | 'ghost'
type CardSize = 'sm' | 'md' | 'lg'
type CardTag = 'div' | 'article' | 'section'

interface Props {
  // Content
  title?: string
  subtitle?: string
  
  // Styling
  variant?: CardVariant
  size?: CardSize
  
  // Behavior
  tag?: CardTag
  clickable?: boolean
  loading?: boolean
  
  // Layout
  noPadding?: boolean
  noHeaderPadding?: boolean
  noBodyPadding?: boolean
  noFooterPadding?: boolean
  
  // Accessibility
  ariaLabel?: string
  role?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  tag: 'div',
  clickable: false,
  loading: false,
  noPadding: false,
  noHeaderPadding: false,
  noBodyPadding: false,
  noFooterPadding: false
})

const emit = defineEmits<{
  click: [event: Event]
}>()

// Base card classes
const baseClasses = [
  'relative',
  'overflow-hidden',
  'transition-all',
  'duration-200',
  'ease-smooth'
]

// Variant classes
const variantClasses = {
  default: [
    'bg-white',
    'border',
    'border-secondary-200',
    'rounded-lg',
    'shadow-card',
    'dark:bg-secondary-800',
    'dark:border-secondary-700'
  ],
  elevated: [
    'bg-white',
    'rounded-lg',
    'shadow-lg',
    'hover:shadow-xl',
    'dark:bg-secondary-800'
  ],
  outlined: [
    'bg-white',
    'border',
    'border-secondary-300',
    'rounded-lg',
    'hover:border-secondary-400',
    'dark:bg-secondary-800',
    'dark:border-secondary-600',
    'dark:hover:border-secondary-500'
  ],
  ghost: [
    'bg-transparent',
    'rounded-lg',
    'hover:bg-secondary-50',
    'dark:hover:bg-secondary-800'
  ]
}

// Size-based padding classes
const paddingClasses = {
  sm: {
    header: 'p-4 pb-0',
    body: 'p-4',
    footer: 'p-4 pt-0'
  },
  md: {
    header: 'p-6 pb-0',
    body: 'p-6',
    footer: 'p-6 pt-0'
  },
  lg: {
    header: 'p-8 pb-0',
    body: 'p-8',
    footer: 'p-8 pt-0'
  }
}

// Clickable states
const clickableClasses = [
  'cursor-pointer',
  'hover:shadow-card-hover',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-primary-500',
  'focus:ring-offset-2',
  'active:scale-[0.98]'
]

const cardClasses = computed(() => [
  ...baseClasses,
  ...variantClasses[props.variant],
  {
    ...Object.fromEntries(clickableClasses.map(cls => [cls, props.clickable])),
    'opacity-75': props.loading
  }
])

const headerClasses = computed(() => [
  'flex',
  'items-start',
  'justify-between',
  {
    [paddingClasses[props.size].header]: !props.noPadding && !props.noHeaderPadding
  }
])

const titleClasses = [
  'text-lg',
  'font-semibold',
  'text-secondary-900',
  'leading-6',
  'dark:text-secondary-100'
]

const subtitleClasses = [
  'mt-1',
  'text-sm',
  'text-secondary-600',
  'dark:text-secondary-400'
]

const bodyClasses = computed(() => [
  {
    [paddingClasses[props.size].body]: !props.noPadding && !props.noBodyPadding
  }
])

const footerClasses = computed(() => [
  'border-t',
  'border-secondary-200',
  'dark:border-secondary-700',
  {
    [paddingClasses[props.size].footer]: !props.noPadding && !props.noFooterPadding
  }
])

const loadingOverlayClasses = [
  'absolute',
  'inset-0',
  'bg-white',
  'bg-opacity-75',
  'flex',
  'items-center',
  'justify-center',
  'z-10',
  'dark:bg-secondary-800',
  'dark:bg-opacity-75'
]

const handleClick = (event: Event) => {
  if (props.clickable && !props.loading) {
    emit('click', event)
  }
}
</script>
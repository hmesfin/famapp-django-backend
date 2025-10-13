<template>
  <div :class="containerClasses">
    <!-- Avatar skeleton (optional) -->
    <div v-if="showAvatar" :class="avatarClasses" />
    
    <!-- Content skeleton -->
    <div v-if="showContent" :class="contentClasses">
      <!-- Lines skeleton -->
      <div v-for="(line, index) in lines" :key="index" :class="lineClasses(line, index)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type SkeletonVariant = 'card' | 'list-item' | 'form' | 'profile' | 'comment'
type AvatarSize = 'sm' | 'md' | 'lg' | 'xl'

interface SkeletonLine {
  width?: string // e.g., 'w-1/2', 'w-3/4', 'w-full'
  height?: string // e.g., 'h-4', 'h-6', 'h-8'
  className?: string // custom classes
}

interface Props {
  variant?: SkeletonVariant
  lines?: number | SkeletonLine[]
  showAvatar?: boolean
  avatarSize?: AvatarSize
  showContent?: boolean
  animated?: boolean
  rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'card',
  lines: 3,
  showAvatar: false,
  avatarSize: 'md',
  showContent: true,
  animated: true,
  rounded: true
})

// Variant configurations
const variantConfigs = {
  card: {
    container: 'p-6 space-y-4',
    layout: 'block'
  },
  'list-item': {
    container: 'flex items-center space-x-4 p-4',
    layout: 'flex'
  },
  profile: {
    container: 'flex items-start space-x-6 p-6',
    layout: 'flex'
  },
  form: {
    container: 'space-y-6 p-6',
    layout: 'block'
  },
  comment: {
    container: 'flex space-x-3 p-4',
    layout: 'flex'
  }
}

// Avatar size configurations
const avatarSizes = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16'
}

// Generate lines configuration
const lines = computed((): SkeletonLine[] => {
  if (Array.isArray(props.lines)) {
    return props.lines
  }
  
  // Default line configurations by variant
  const defaultLines: Record<SkeletonVariant, SkeletonLine[]> = {
    card: [
      { width: 'w-3/4', height: 'h-6' }, // Title
      { width: 'w-full', height: 'h-4' }, // Content line 1
      { width: 'w-5/6', height: 'h-4' }  // Content line 2
    ],
    'list-item': [
      { width: 'w-1/3', height: 'h-5' }, // Name
      { width: 'w-1/2', height: 'h-4' }  // Subtitle
    ],
    profile: [
      { width: 'w-1/4', height: 'h-6' }, // Name
      { width: 'w-1/3', height: 'h-4' }, // Title
      { width: 'w-full', height: 'h-4' }, // Bio line 1
      { width: 'w-3/4', height: 'h-4' }  // Bio line 2
    ],
    form: [
      { width: 'w-1/4', height: 'h-4' }, // Label
      { width: 'w-full', height: 'h-10' }, // Input
      { width: 'w-1/4', height: 'h-4' }, // Label
      { width: 'w-full', height: 'h-10' }  // Input
    ],
    comment: [
      { width: 'w-1/4', height: 'h-4' }, // Author
      { width: 'w-full', height: 'h-4' }, // Comment line 1
      { width: 'w-2/3', height: 'h-4' }  // Comment line 2
    ]
  }
  
  const variantLines = defaultLines[props.variant] || defaultLines.card
  return variantLines.slice(0, props.lines)
})

// Computed classes
const containerClasses = computed(() => [
  variantConfigs[props.variant].container,
  {
    'animate-pulse': props.animated
  }
])

const avatarClasses = computed(() => [
  avatarSizes[props.avatarSize],
  'bg-secondary-200 dark:bg-secondary-700',
  'flex-shrink-0',
  {
    'rounded-full': props.rounded,
    'rounded-lg': !props.rounded
  }
])

const contentClasses = computed(() => {
  const config = variantConfigs[props.variant]
  return [
    {
      'flex-1 space-y-2': config.layout === 'flex',
      'space-y-2': config.layout === 'block'
    }
  ]
})

const lineClasses = (line: SkeletonLine, index: number) => [
  'bg-secondary-200 dark:bg-secondary-700',
  line.width || 'w-full',
  line.height || 'h-4',
  'rounded',
  line.className || '',
  {
    'mb-4': index === 0 && props.variant === 'form' && (index + 1) % 2 === 1, // Add margin after labels in form
  }
]
</script>

<style scoped>
/* Custom animation for skeleton */
@keyframes shimmer {
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
}

.animate-pulse {
  animation: shimmer 2s ease-in-out infinite;
  background: linear-gradient(
    to right,
    #f1f5f9 4%,
    #e2e8f0 25%,
    #f1f5f9 36%
  );
  background-size: 1000px 100%;
}

.dark .animate-pulse {
  background: linear-gradient(
    to right,
    #374151 4%,
    #4b5563 25%,
    #374151 36%
  );
  background-size: 1000px 100%;
}
</style>
<template>
  <div
    :class="avatarClasses"
    :title="altText"
    role="img"
    :aria-label="altText"
  >
    <!-- Avatar image -->
    <img
      v-if="avatarUrl && !imageError"
      :src="avatarUrl"
      :alt="altText"
      :class="imageClasses"
      @error="handleImageError"
      @load="handleImageLoad"
    />
    
    <!-- Fallback with initials -->
    <div
      v-else
      :class="fallbackClasses"
    >
      <span :class="textClasses">{{ initials }}</span>
    </div>
    
    <!-- Online status indicator (optional) -->
    <div
      v-if="showOnlineStatus && isOnline"
      :class="statusClasses"
      title="Online"
    />
    
    <!-- Upload overlay for editable avatars -->
    <div
      v-if="editable && !loading"
      :class="overlayClasses"
      @click="triggerFileUpload"
    >
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </div>
    
    <!-- Loading overlay -->
    <div
      v-if="loading"
      :class="loadingClasses"
    >
      <!-- Progress ring if progress available -->
      <div v-if="progress > 0" class="relative">
        <svg class="w-8 h-8 transform -rotate-90" viewBox="0 0 32 32">
          <!-- Background circle -->
          <circle
            cx="16"
            cy="16"
            r="12"
            stroke="rgba(255,255,255,0.3)"
            stroke-width="2"
            fill="none"
          />
          <!-- Progress circle -->
          <circle
            cx="16"
            cy="16"
            r="12"
            stroke="white"
            stroke-width="2"
            fill="none"
            :stroke-dasharray="progressCircumference"
            :stroke-dashoffset="progressOffset"
            stroke-linecap="round"
            class="transition-all duration-300 ease-out"
          />
        </svg>
        <span class="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
          {{ Math.round(progress) }}%
        </span>
      </div>
      
      <!-- Default spinner if no progress -->
      <svg v-else class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  </div>
  
  <!-- Hidden file input for uploads -->
  <input
    v-if="editable"
    ref="fileInput"
    type="file"
    accept="image/jpeg,image/png,image/webp"
    class="hidden"
    @change="handleFileSelect"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AvatarSize } from '../types/profile.types'

interface Props {
  // Avatar data
  avatarUrl?: string | null
  name?: string
  email?: string
  
  // Styling
  size?: AvatarSize
  
  // Behavior
  editable?: boolean
  showOnlineStatus?: boolean
  isOnline?: boolean
  loading?: boolean
  progress?: number
  
  // Customization
  fallbackBgColor?: string
  borderColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  editable: false,
  showOnlineStatus: false,
  isOnline: false,
  loading: false,
  progress: 0,
  fallbackBgColor: 'bg-primary-500',
  borderColor: 'border-secondary-200'
})

const emit = defineEmits<{
  upload: [file: File]
  click: [event: MouseEvent]
}>()

// Refs
const imageError = ref(false)
const fileInput = ref<HTMLInputElement>()

// Size classes mapping
const sizeClasses = {
  xs: {
    container: 'w-6 h-6',
    text: 'text-xs',
    status: 'w-2 h-2 -top-0.5 -right-0.5',
    overlay: 'opacity-0 group-hover:opacity-100'
  },
  sm: {
    container: 'w-8 h-8',
    text: 'text-sm',
    status: 'w-2.5 h-2.5 -top-0.5 -right-0.5',
    overlay: 'opacity-0 group-hover:opacity-100'
  },
  md: {
    container: 'w-10 h-10',
    text: 'text-sm',
    status: 'w-3 h-3 -top-1 -right-1',
    overlay: 'opacity-0 hover:opacity-100'
  },
  lg: {
    container: 'w-12 h-12',
    text: 'text-base',
    status: 'w-3.5 h-3.5 -top-1 -right-1',
    overlay: 'opacity-0 hover:opacity-100'
  },
  xl: {
    container: 'w-16 h-16',
    text: 'text-lg',
    status: 'w-4 h-4 -top-1 -right-1',
    overlay: 'opacity-0 hover:opacity-100'
  },
  '2xl': {
    container: 'w-24 h-24',
    text: 'text-xl',
    status: 'w-5 h-5 -top-1 -right-1',
    overlay: 'opacity-0 hover:opacity-100'
  }
}

// Computed properties
const altText = computed(() => {
  if (props.name) return `${props.name}'s avatar`
  if (props.email) return `${props.email}'s avatar`
  return 'User avatar'
})

const initials = computed(() => {
  if (props.name) {
    return props.name
      .split(' ')
      .slice(0, 2)
      .map(word => word.charAt(0).toUpperCase())
      .join('')
  }
  if (props.email) {
    return props.email.charAt(0).toUpperCase()
  }
  return '?'
})

const avatarClasses = computed(() => [
  // Base styles
  'relative',
  'inline-block',
  'overflow-hidden',
  'rounded-full',
  'flex-shrink-0',
  
  // Size
  sizeClasses[props.size].container,
  
  // Border
  'border-2',
  props.borderColor,
  
  // Interactive styles
  {
    'cursor-pointer group': props.editable,
    'transition-transform hover:scale-105': props.editable
  }
])

const imageClasses = computed(() => [
  'w-full',
  'h-full',
  'object-cover',
  'object-center'
])

const fallbackClasses = computed(() => [
  'w-full',
  'h-full',
  'flex',
  'items-center',
  'justify-center',
  props.fallbackBgColor,
  'text-white',
  'font-medium'
])

const textClasses = computed(() => [
  sizeClasses[props.size].text,
  'font-semibold',
  'select-none'
])

const statusClasses = computed(() => [
  'absolute',
  'rounded-full',
  'bg-success-500',
  'border-2',
  'border-white',
  'dark:border-secondary-800',
  sizeClasses[props.size].status
])

const overlayClasses = computed(() => [
  'absolute',
  'inset-0',
  'bg-black',
  'bg-opacity-50',
  'flex',
  'items-center',
  'justify-center',
  'transition-opacity',
  'duration-200',
  'cursor-pointer',
  sizeClasses[props.size].overlay
])

const loadingClasses = computed(() => [
  'absolute',
  'inset-0',
  'bg-black',
  'bg-opacity-50',
  'flex',
  'items-center',
  'justify-center'
])

// Progress circle calculations
const progressCircumference = computed(() => 2 * Math.PI * 12) // radius = 12
const progressOffset = computed(() => {
  const progress = Math.min(Math.max(props.progress, 0), 100)
  return progressCircumference.value - (progress / 100) * progressCircumference.value
})

// Methods
const handleImageError = () => {
  imageError.value = true
}

const handleImageLoad = () => {
  imageError.value = false
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    // Validate file type and size
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
    const maxSize = 5 * 1024 * 1024 // 5MB
    
    if (!allowedTypes.includes(file.type)) {
      // You might want to show a toast error here
      console.error('Please select a valid image file (JPEG, PNG, or WebP)')
      return
    }
    
    if (file.size > maxSize) {
      console.error('File size must be less than 5MB')
      return
    }
    
    emit('upload', file)
    
    // Clear the input so the same file can be selected again
    target.value = ''
  }
}

const handleClick = (event: MouseEvent) => {
  if (!props.editable) {
    emit('click', event)
  }
}
</script>
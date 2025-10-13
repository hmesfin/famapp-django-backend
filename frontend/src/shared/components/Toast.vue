<template>
  <transition
    appear
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
    enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="visible"
      class="pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5"
    >
      <div class="p-4">
        <div class="flex items-start">
          <!-- Icon -->
          <div class="flex-shrink-0">
            <!-- Success -->
            <CheckCircleIcon v-if="toast.type === 'success'" class="h-6 w-6 text-green-400" />
            
            <!-- Error -->
            <XCircleIcon v-else-if="toast.type === 'error'" class="h-6 w-6 text-red-400" />
            
            <!-- Warning -->
            <ExclamationTriangleIcon v-else-if="toast.type === 'warning'" class="h-6 w-6 text-yellow-400" />
            
            <!-- Info -->
            <InformationCircleIcon v-else class="h-6 w-6 text-blue-400" />
          </div>
          
          <!-- Content -->
          <div class="ml-3 w-0 flex-1">
            <p v-if="toast.title" class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ toast.title }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400" :class="{ 'mt-1': toast.title }">
              {{ toast.message }}
            </p>
            
            <!-- Action button -->
            <div v-if="toast.action" class="mt-3">
              <button
                @click="handleAction"
                class="text-sm font-medium"
                :class="actionButtonClass"
              >
                {{ toast.action.label }}
              </button>
            </div>
          </div>
          
          <!-- Close button -->
          <div class="ml-4 flex flex-shrink-0">
            <button
              @click="$emit('close')"
              class="inline-flex rounded-md bg-white text-gray-400 hover:text-gray-500 dark:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              <span class="sr-only">Close</span>
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
      
      <!-- Progress bar for auto-dismiss -->
      <div v-if="!toast.persistent && toast.duration" class="h-1 bg-gray-100 dark:bg-gray-800">
        <div
          class="h-full transition-all duration-100 ease-linear"
          :class="progressBarClass"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Toast } from '@/stores/toast'
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

interface Props {
  toast: Toast
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const visible = ref(true)
const progress = ref(100)
let progressInterval: ReturnType<typeof setInterval> | null = null

const actionButtonClass = computed(() => {
  const base = 'hover:underline focus:outline-none focus:ring-2 focus:ring-offset-2 rounded'
  const colors = {
    success: 'text-green-600 hover:text-green-500 focus:ring-green-500',
    error: 'text-red-600 hover:text-red-500 focus:ring-red-500',
    warning: 'text-yellow-600 hover:text-yellow-500 focus:ring-yellow-500',
    info: 'text-blue-600 hover:text-blue-500 focus:ring-blue-500'
  }
  return `${base} ${colors[props.toast.type]}`
})

const progressBarClass = computed(() => {
  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  }
  return colors[props.toast.type]
})

const handleAction = () => {
  if (props.toast.action) {
    props.toast.action.onClick()
    emit('close')
  }
}

const startProgressBar = () => {
  if (!props.toast.persistent && props.toast.duration) {
    const updateInterval = 100 // Update every 100ms
    const totalSteps = props.toast.duration / updateInterval
    const decrementAmount = 100 / totalSteps

    progressInterval = setInterval(() => {
      progress.value -= decrementAmount
      if (progress.value <= 0) {
        progress.value = 0
        if (progressInterval) {
          clearInterval(progressInterval)
        }
      }
    }, updateInterval)
  }
}

onMounted(() => {
  startProgressBar()
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})
</script>
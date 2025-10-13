<template>
  <span 
    :class="[
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
      badgeClass
    ]"
  >
    {{ displayText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: string
  type?: 'default' | 'outline' | 'solid'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default'
})

const statusConfig: Record<string, { color: string; text: string }> = {
  // Invitation statuses
  pending: { color: 'yellow', text: 'Pending' },
  accepted: { color: 'green', text: 'Accepted' },
  expired: { color: 'red', text: 'Expired' },
  cancelled: { color: 'gray', text: 'Cancelled' },
  
  // Project statuses
  planning: { color: 'blue', text: 'Planning' },
  active: { color: 'green', text: 'Active' },
  on_hold: { color: 'yellow', text: 'On Hold' },
  completed: { color: 'green', text: 'Completed' },
  archived: { color: 'gray', text: 'Archived' },
  
  // Task statuses
  todo: { color: 'gray', text: 'To Do' },
  in_progress: { color: 'blue', text: 'In Progress' },
  review: { color: 'yellow', text: 'Review' },
  done: { color: 'green', text: 'Done' },
  blocked: { color: 'red', text: 'Blocked' },
  
  // Generic statuses
  success: { color: 'green', text: 'Success' },
  warning: { color: 'yellow', text: 'Warning' },
  error: { color: 'red', text: 'Error' },
  info: { color: 'blue', text: 'Info' }
}

const config = computed(() => {
  return statusConfig[props.status.toLowerCase()] || { color: 'gray', text: props.status }
})

const displayText = computed(() => config.value.text)

const badgeClass = computed(() => {
  const color = config.value.color
  
  if (props.type === 'outline') {
    return {
      'bg-transparent border': true,
      'border-red-500 text-red-700 dark:text-red-400': color === 'red',
      'border-green-500 text-green-700 dark:text-green-400': color === 'green',
      'border-yellow-500 text-yellow-700 dark:text-yellow-400': color === 'yellow',
      'border-blue-500 text-blue-700 dark:text-blue-400': color === 'blue',
      'border-gray-500 text-gray-700 dark:text-gray-400': color === 'gray'
    }
  }
  
  if (props.type === 'solid') {
    return {
      'bg-red-500 text-white': color === 'red',
      'bg-green-500 text-white': color === 'green',
      'bg-yellow-500 text-white': color === 'yellow',
      'bg-blue-500 text-white': color === 'blue',
      'bg-gray-500 text-white': color === 'gray'
    }
  }
  
  // Default style
  return {
    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': color === 'red',
    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': color === 'green',
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': color === 'yellow',
    'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200': color === 'blue',
    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200': color === 'gray'
  }
})
</script>
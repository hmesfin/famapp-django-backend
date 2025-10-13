<template>
  <!-- Global notification live region -->
  <div
    aria-live="assertive"
    class="pointer-events-none fixed inset-0 flex items-end px-4 py-6 sm:items-start sm:p-6 z-50"
  >
    <div class="flex w-full flex-col items-center space-y-4 sm:items-end">
      <!-- Notification panel -->
      <TransitionGroup
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5"
        >
          <div class="p-4">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <component :is="getIcon(toast.type)" class="h-6 w-6" :class="getIconClass(toast.type)" />
              </div>
              <div class="ml-3 w-0 flex-1 pt-0.5">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ toast.title }}
                </p>
                <p v-if="toast.message" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {{ toast.message }}
                </p>
              </div>
              <div class="ml-4 flex flex-shrink-0">
                <button
                  @click="toastStore.removeToast(toast.id)"
                  type="button"
                  class="inline-flex rounded-md bg-white dark:bg-gray-800 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/solid'
import { useToastStore } from '../stores/toastStore'

const toastStore = useToastStore()

function getIcon(type: string) {
  switch (type) {
    case 'success':
      return CheckCircleIcon
    case 'error':
      return ExclamationCircleIcon
    case 'warning':
      return ExclamationTriangleIcon
    case 'info':
    default:
      return InformationCircleIcon
  }
}

function getIconClass(type: string) {
  switch (type) {
    case 'success':
      return 'text-green-400'
    case 'error':
      return 'text-red-400'
    case 'warning':
      return 'text-yellow-400'
    case 'info':
    default:
      return 'text-blue-400'
  }
}
</script>
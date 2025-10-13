<template>
  <nav class="flex justify-center" aria-label="Pagination">
    <div class="inline-flex items-center rounded-md shadow-sm -space-x-px">
      <!-- Previous button -->
      <BaseButton
        variant="outline"
        size="sm"
        :leading-icon="ChevronLeftIcon"
        :disabled="!hasPrevious"
        @click="$emit('prev-page')"
        class="rounded-r-none border-r-0"
        aria-label="Previous page"
      />
      
      <!-- Current page indicator -->
      <div class="relative inline-flex items-center px-4 py-2 border border-secondary-300 dark:border-secondary-600 bg-white dark:bg-secondary-800 text-sm font-medium text-secondary-700 dark:text-secondary-300">
        Page {{ currentPage }}
        <span v-if="totalPages" class="text-secondary-500 dark:text-secondary-400 ml-1">
          of {{ totalPages }}
        </span>
      </div>
      
      <!-- Next button -->
      <BaseButton
        variant="outline"
        size="sm"
        :trailing-icon="ChevronRightIcon"
        :disabled="!hasNext"
        @click="$emit('next-page')"
        class="rounded-l-none border-l-0"
        aria-label="Next page"
      />
    </div>
    
    <!-- Optional page info -->
    <div v-if="showPageInfo && (totalItems || itemsPerPage)" class="ml-4 flex items-center text-sm text-secondary-500 dark:text-secondary-400">
      <span v-if="totalItems && itemsPerPage">
        Showing {{ startItem }} to {{ endItem }} of {{ totalItems }} results
      </span>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import BaseButton from './BaseButton.vue'

interface Props {
  currentPage: number
  hasPrevious?: boolean
  hasNext?: boolean
  totalPages?: number
  totalItems?: number
  itemsPerPage?: number
  showPageInfo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  hasPrevious: false,
  hasNext: false,
  showPageInfo: false
})

const emit = defineEmits<{
  'prev-page': []
  'next-page': []
}>()

// Computed for page info
const startItem = computed(() => {
  if (!props.totalItems || !props.itemsPerPage) return 0
  return ((props.currentPage - 1) * props.itemsPerPage) + 1
})

const endItem = computed(() => {
  if (!props.totalItems || !props.itemsPerPage) return 0
  const calculated = props.currentPage * props.itemsPerPage
  return Math.min(calculated, props.totalItems)
})
</script>
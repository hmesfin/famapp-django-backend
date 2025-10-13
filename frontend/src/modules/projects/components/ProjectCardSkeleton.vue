<template>
  <BaseCard 
    variant="default" 
    size="md"
    class="animate-pulse"
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="flex-1">
          <!-- Title skeleton -->
          <div class="h-6 bg-secondary-300 dark:bg-secondary-600 rounded-md mb-2 w-3/4" />
          <!-- Owner skeleton -->
          <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-1/2" />
        </div>
        <!-- Status badge skeleton -->
        <div class="h-6 w-20 bg-secondary-200 dark:bg-secondary-700 rounded-full" />
      </div>
    </template>

    <!-- Description skeleton -->
    <div class="space-y-2 mb-4">
      <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-full" />
      <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-4/5" />
    </div>

    <!-- Stats skeleton -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <div class="text-center">
        <div class="h-8 bg-secondary-300 dark:bg-secondary-600 rounded mb-1 w-12 mx-auto" />
        <div class="h-3 bg-secondary-200 dark:bg-secondary-700 rounded w-10 mx-auto" />
      </div>
      <div class="text-center">
        <div class="h-8 bg-secondary-300 dark:bg-secondary-600 rounded mb-1 w-12 mx-auto" />
        <div class="h-3 bg-secondary-200 dark:bg-secondary-700 rounded w-12 mx-auto" />
      </div>
      <div class="text-center">
        <div class="h-8 bg-secondary-300 dark:bg-secondary-600 rounded mb-1 w-12 mx-auto" />
        <div class="h-3 bg-secondary-200 dark:bg-secondary-700 rounded w-16 mx-auto" />
      </div>
    </div>

    <!-- Progress bar skeleton -->
    <div class="mb-4">
      <div class="flex justify-between mb-1">
        <div class="h-3 bg-secondary-200 dark:bg-secondary-700 rounded w-16" />
        <div class="h-3 bg-secondary-200 dark:bg-secondary-700 rounded w-8" />
      </div>
      <div class="w-full bg-secondary-200 dark:bg-secondary-700 rounded-full h-2" />
    </div>

    <template #footer>
      <div class="flex items-center justify-between">
        <!-- Date skeleton -->
        <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-32" />
        
        <!-- Action buttons skeleton -->
        <div class="flex space-x-2">
          <div class="h-8 w-8 bg-secondary-200 dark:bg-secondary-700 rounded" />
          <div class="h-8 w-8 bg-secondary-200 dark:bg-secondary-700 rounded" />
        </div>
      </div>
    </template>
  </BaseCard>
</template>

<script setup lang="ts">
import BaseCard from '@/shared/components/BaseCard.vue'
</script>
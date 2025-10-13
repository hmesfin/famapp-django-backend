<template>
  <div class="border-b border-gray-200 dark:border-gray-700">
    <nav class="-mb-px flex space-x-8">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="$emit('update:activeTab', tab.id)"
        :class="[
          activeTab === tab.id
            ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
            : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
          'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
        ]"
      >
        <span class="flex items-center">
          <component
            :is="tab.icon"
            v-if="tab.icon"
            class="mr-2 h-5 w-5"
            :class="[
              activeTab === tab.id
                ? 'text-indigo-500'
                : 'text-gray-400 group-hover:text-gray-500'
            ]"
          />
          {{ tab.name }}
          <span
            v-if="tab.count !== undefined"
            :class="[
              activeTab === tab.id
                ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-300',
              'ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium',
            ]"
          >
            {{ tab.count }}
          </span>
        </span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

export interface Tab {
  id: string
  name: string
  icon?: Component
  count?: number
}

interface Props {
  tabs: Tab[]
  activeTab: string
}

defineProps<Props>()

defineEmits<{
  'update:activeTab': [tabId: string]
}>()
</script>
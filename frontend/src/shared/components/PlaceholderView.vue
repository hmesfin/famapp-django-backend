<template>
  <div class="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <!-- Header Section -->
      <div class="text-center mb-12">
        <div
          class="mx-auto mb-6 w-16 h-16 bg-primary-100 dark:bg-primary-900/50 rounded-full flex items-center justify-center"
        >
          <!-- Dynamic icon based on type -->
          <svg
            v-if="icon === 'construction'"
            class="h-8 w-8 text-primary-600 dark:text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
            />
          </svg>
          <svg
            v-else-if="icon === 'dashboard'"
            class="h-8 w-8 text-primary-600 dark:text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <svg
            v-else-if="icon === 'users'"
            class="h-8 w-8 text-primary-600 dark:text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
            />
          </svg>
          <svg
            v-else-if="icon === 'auth'"
            class="h-8 w-8 text-primary-600 dark:text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else-if="icon === 'settings'"
            class="h-8 w-8 text-primary-600 dark:text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          <svg
            v-else
            class="h-8 w-8 text-primary-600 dark:text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
        </div>

        <h1 class="text-3xl font-bold text-secondary-900 dark:text-secondary-100 mb-4">
          {{ title }}
        </h1>

        <p class="text-lg text-secondary-600 dark:text-secondary-400 max-w-2xl mx-auto leading-relaxed">
          {{ description }}
        </p>
      </div>

      <!-- Status Badge -->
      <div class="flex justify-center mb-8">
        <span :class="statusBadgeClasses">
          <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {{ status }}
        </span>
      </div>

      <!-- Features/Info Cards (if provided) -->
      <div
        v-if="features.length > 0"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
      >
        <div
          v-for="(feature, index) in features"
          :key="index"
          class="bg-white dark:bg-secondary-800 rounded-lg p-6 shadow-sm border border-secondary-200 dark:border-secondary-700"
        >
          <div
            class="w-10 h-10 bg-secondary-100 dark:bg-secondary-800 rounded-lg flex items-center justify-center mb-4"
          >
            <svg
              class="h-5 w-5 text-secondary-600 dark:text-secondary-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 mb-2">
            {{ feature.title }}
          </h3>
          <p class="text-secondary-600 dark:text-secondary-400 text-sm">
            {{ feature.description }}
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-center space-x-4">
        <router-link
          v-if="backLink"
          :to="backLink"
          class="inline-flex items-center px-6 py-3 border border-secondary-300 shadow-sm text-sm font-medium rounded-md text-secondary-700 dark:text-secondary-300 bg-white dark:bg-secondary-800 hover:bg-secondary-50 dark:hover:bg-secondary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
        >
          <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          {{ backText || 'Go Back' }}
        </router-link>

        <router-link
          v-if="primaryLink"
          :to="primaryLink"
          class="inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
        >
          {{ primaryText || 'Continue' }}
          <svg class="h-4 w-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </router-link>
      </div>

      <!-- Technical Info (for development) -->
      <div v-if="showTechnicalInfo" class="mt-12 p-6 bg-secondary-100 dark:bg-secondary-800 rounded-lg">
        <h3 class="text-lg font-medium text-secondary-900 dark:text-secondary-100 mb-4 flex items-center">
          <svg
            class="h-5 w-5 mr-2 text-success-600 dark:text-success-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
            />
          </svg>
          Technical Information
        </h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between text-secondary-600 dark:text-secondary-400">
            <span>Component:</span>
            <code class="text-success-600 dark:text-success-400 font-mono">{{
              componentName || 'Unknown'
            }}</code>
          </div>
          <div class="flex justify-between text-secondary-600 dark:text-secondary-400">
            <span>Route:</span>
            <code class="text-primary-600 dark:text-primary-400 font-mono">{{ $route.path }}</code>
          </div>
          <div class="flex justify-between text-secondary-600 dark:text-secondary-400">
            <span>Layout:</span>
            <code class="text-info-600 dark:text-info-400 font-mono">{{
              layoutType || 'Default'
            }}</code>
          </div>
          <div v-if="expectedProps.length > 0" class="mt-4">
            <span class="text-secondary-600 dark:text-secondary-400">Expected Props:</span>
            <ul class="mt-2 space-y-1">
              <li
                v-for="prop in expectedProps"
                :key="prop"
                class="text-secondary-500 dark:text-secondary-400 text-xs font-mono ml-4"
              >
                • {{ prop }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Feature {
  title: string
  description: string
}

interface Props {
  title: string
  description: string
  status?: 'coming-soon' | 'in-development' | 'planned' | 'placeholder'
  icon?: 'construction' | 'dashboard' | 'users' | 'auth' | 'settings' | 'default'
  features?: Feature[]
  backLink?: string
  backText?: string
  primaryLink?: string
  primaryText?: string
  componentName?: string
  layoutType?: string
  expectedProps?: string[]
  showTechnicalInfo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  status: 'placeholder',
  icon: 'default',
  features: () => [],
  expectedProps: () => [],
  showTechnicalInfo: true,
})

const statusBadgeClasses = computed(() => {
  const baseClasses = 'inline-flex items-center px-4 py-2 rounded-full text-sm font-medium'

  switch (props.status) {
    case 'coming-soon':
      return `${baseClasses} bg-success-100 dark:bg-success-900/50 text-success-800 dark:text-success-200`
    case 'in-development':
      return `${baseClasses} bg-warning-100 dark:bg-warning-900/50 text-warning-800 dark:text-warning-200`
    case 'planned':
      return `${baseClasses} bg-info-100 dark:bg-info-900/50 text-info-800 dark:text-info-200`
    default:
      return `${baseClasses} bg-secondary-100 dark:bg-secondary-800 text-secondary-800 dark:text-secondary-200`
  }
})
</script>

<template>
  <div class="min-h-screen flex bg-gray-50 dark:bg-gray-900">
    <!-- Left side - Branding/Marketing -->
    <div class="hidden lg:flex lg:w-1/2 bg-blue-600 dark:bg-blue-700 items-center justify-center">
      <div class="max-w-md text-center">
        <div class="mb-8">
          <h1 class="text-4xl font-bold text-white mb-4">
            Django Vue Starter
          </h1>
          <p class="text-blue-100 text-lg leading-relaxed">
            A modern full-stack template built with Django and Vue.js, featuring
            JWT authentication, role-based access control, and Docker orchestration.
          </p>
        </div>

        <!-- Features list -->
        <div class="space-y-4 text-left">
          <div class="flex items-center text-blue-100">
            <CheckIcon class="h-5 w-5 mr-3 text-blue-300" />
            Django REST Framework backend
          </div>
          <div class="flex items-center text-blue-100">
            <CheckIcon class="h-5 w-5 mr-3 text-blue-300" />
            Vue 3 with TypeScript
          </div>
          <div class="flex items-center text-blue-100">
            <CheckIcon class="h-5 w-5 mr-3 text-blue-300" />
            JWT Authentication
          </div>
          <div class="flex items-center text-blue-100">
            <CheckIcon class="h-5 w-5 mr-3 text-blue-300" />
            Role-Based Access Control
          </div>
          <div class="flex items-center text-blue-100">
            <CheckIcon class="h-5 w-5 mr-3 text-blue-300" />
            Docker Development Environment
          </div>
        </div>

        <!-- Decorative pattern -->
        <div class="mt-12 opacity-20">
          <div class="grid grid-cols-3 gap-4">
            <div v-for="i in 9" :key="i" class="h-2 bg-white dark:bg-gray-800 rounded"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right side - Auth Form -->
    <div class="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-800 relative">
      <!-- Theme toggle in top-right corner -->
      <div class="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      
      <div class="max-w-md w-full space-y-8">
        <!-- Logo for mobile -->
        <div class="lg:hidden text-center">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Django Vue Starter
          </h1>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            Modern full-stack development template
          </p>
        </div>

        <!-- Auth form content -->
        <div class="bg-white dark:bg-gray-800 py-8 px-6 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 lg:shadow-none lg:border-none lg:bg-transparent lg:p-0">
          <router-view />
        </div>

        <!-- Back to home link -->
        <div class="text-center">
          <router-link
            to="/"
            class="inline-flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 font-medium"
          >
            <ArrowLeftIcon class="h-4 w-4 mr-2" />
            Back to home
          </router-link>
        </div>

        <!-- Additional links -->
        <div class="text-center space-y-2">
          <div class="text-xs text-gray-500 dark:text-gray-400">
            By signing in, you agree to our
            <router-link to="/terms" class="text-blue-600 dark:text-blue-400 hover:text-blue-700">Terms of Service</router-link>
            and
            <router-link to="/privacy" class="text-blue-600 dark:text-blue-400 hover:text-blue-700">Privacy Policy</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CheckIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>
<template>
  <div>
    <!-- Hero Section -->
    <section class="bg-white dark:bg-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="text-center">
          <h1
            class="text-4xl font-bold text-gray-900 dark:text-gray-100 sm:text-5xl lg:text-6xl"
          >
            Django Vue
            <span class="text-blue-600 dark:text-blue-400">Starter</span>
          </h1>
          <p
            class="mt-6 text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto"
          >
            A modern full-stack template built with Django and Vue.js, featuring JWT authentication,
            role-based access control, and Docker orchestration for rapid development.
          </p>
          <div class="mt-10 flex justify-center space-x-4">
            <router-link
              to="/auth/register"
              class="bg-blue-600 text-white px-8 py-3 rounded-md text-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Get Started
            </router-link>
            <router-link
              to="/features"
              class="bg-gray-100 text-gray-900 dark:text-gray-100 px-8 py-3 rounded-md text-lg font-medium hover:bg-gray-200 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              Learn More
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Preview -->
    <section class="bg-gray-50 dark:bg-gray-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="text-center mb-16">
          <h2
            class="text-3xl font-bold text-gray-900 dark:text-gray-100 sm:text-4xl"
          >
            Everything you need to build fast
          </h2>
          <p
            class="mt-4 text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto"
          >
            Built on proven technologies with best practices baked in.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Backend -->
          <div
            class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          >
            <div
              class="w-12 h-12 bg-green-100 dark:bg-green-900/50 rounded-lg flex items-center justify-center mb-4"
            >
              <ArrowLeftIcon class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <h3
              class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2"
            >
              Django Backend
            </h3>
            <p class="text-gray-600 dark:text-gray-400 text-sm">
              Powered by Django REST Framework with JWT authentication, PostgreSQL, Redis, and
              Celery for background tasks.
            </p>
          </div>

          <!-- Frontend -->
          <div
            class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          >
            <div
              class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-4"
            >
              <BoltIcon class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3
              class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2"
            >
              Vue 3 Frontend
            </h3>
            <p class="text-gray-600 dark:text-gray-400 text-sm">
              Modern Vue 3 with TypeScript, Vite, Pinia state management, and Tailwind CSS for
              responsive design.
            </p>
          </div>

          <!-- DevOps -->
          <div
            class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          >
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <ArchiveBoxIcon class="w-6 h-6 text-purple-600" />
            </div>
            <h3
              class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2"
            >
              Docker Ready
            </h3>
            <p class="text-gray-600 dark:text-gray-400 text-sm">
              Complete Docker setup with cookiecutter-django foundation, Traefik proxy, and
              production-ready configuration.
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeftIcon, BoltIcon, ArchiveBoxIcon } from '@heroicons/vue/24/outline'
</script>

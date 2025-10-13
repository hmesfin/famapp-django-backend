<template>
  <div class="min-h-screen bg-white dark:bg-gray-800 px-4 py-16 sm:px-6 sm:py-24 md:grid md:place-items-center lg:px-8">
    <div class="max-w-max mx-auto">
      <main class="sm:flex">
        <p class="text-4xl font-bold text-blue-600 dark:text-blue-400 sm:text-5xl">404</p>
        <div class="sm:ml-6">
          <div class="sm:border-l sm:border-gray-200 dark:border-gray-700 sm:pl-6">
            <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 tracking-tight sm:text-5xl">
              Page not found
            </h1>
            <p class="mt-1 text-base text-gray-500 dark:text-gray-400">
              Please check the URL in the address bar and try again.
            </p>
          </div>
          <div class="mt-10 flex space-x-3 sm:border-l sm:border-transparent sm:pl-6">
            <router-link
              to="/"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go back home
            </router-link>
            <router-link
              to="/contact"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 dark:bg-blue-900/50 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Contact support
            </router-link>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404 page doesn't need any special logic
</script>
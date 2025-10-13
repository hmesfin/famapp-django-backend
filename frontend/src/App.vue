<template>
  <router-view />
  <ToastContainer />
</template>

<script setup lang="ts">
import ToastContainer from '@/shared/components/ToastContainer.vue'

// App.vue - Root application component
// The router-view will render the appropriate layout based on the current route
// ToastContainer handles all toast notifications globally
</script>

<style>
/* Global styles can go here if needed */
</style>

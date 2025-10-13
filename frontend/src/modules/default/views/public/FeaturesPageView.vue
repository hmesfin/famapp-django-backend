<template>
  <PlaceholderView
    title="Features & Capabilities"
    description="Discover everything Django Vue Starter offers for rapid full-stack development. Built with modern technologies and best practices."
    status="coming-soon"
    icon="settings"
    component-name="FeaturesPageView"
    layout-type="DefaultLayout"
    back-link="/"
    back-text="Back to Home"
    primary-link="/auth/register"
    primary-text="Get Started"
    :features="[
      {
        title: 'Django REST Framework',
        description: 'Powerful backend API with authentication, permissions, and serialization'
      },
      {
        title: 'Vue 3 + TypeScript',
        description: 'Modern reactive frontend with type safety and composition API'
      },
      {
        title: 'Docker Development',
        description: 'Complete containerized development environment with hot reloading'
      },
      {
        title: 'JWT Authentication',
        description: 'Secure token-based auth with refresh tokens and role-based access'
      },
      {
        title: 'PostgreSQL + Redis',
        description: 'Production-ready database with caching and session storage'
      },
      {
        title: 'Celery Background Jobs',
        description: 'Asynchronous task processing with monitoring and scheduling'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
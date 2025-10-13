<template>
  <PlaceholderView
    title="About Django Vue Starter"
    description="Django Vue Starter is a modern full-stack development template that combines the power of Django with the elegance of Vue.js to accelerate your development process."
    status="coming-soon"
    icon="users"
    component-name="AboutPageView"
    layout-type="DefaultLayout"
    back-link="/"
    back-text="Back to Home"
    primary-link="/features"
    primary-text="Explore Features"
    :features="[
      {
        title: 'Our Mission',
        description: 'Provide developers with production-ready templates that follow best practices'
      },
      {
        title: 'Open Source',
        description: 'Built on open source technologies with community contributions'
      },
      {
        title: 'Developer Experience',
        description: 'Focus on developer productivity and modern development workflows'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
<template>
  <PlaceholderView
    title="Contact Us"
    description="Have questions about Django Vue Starter? Need help with implementation or custom development? We're here to help!"
    status="planned"
    icon="users"
    component-name="ContactPageView"
    layout-type="DefaultLayout"
    :expected-props="['name', 'email', 'subject', 'message']"
    back-link="/"
    back-text="Back to Home"
    primary-link="/features"
    primary-text="Learn More"
    :features="[
      {
        title: 'Technical Support',
        description: 'Get help with setup, configuration, and troubleshooting'
      },
      {
        title: 'Custom Development',
        description: 'Need custom features? We offer development services'
      },
      {
        title: 'Training & Consulting',
        description: 'Learn best practices and get guidance for your team'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
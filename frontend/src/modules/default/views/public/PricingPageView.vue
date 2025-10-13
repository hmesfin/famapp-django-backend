<template>
  <PlaceholderView
    title="Pricing & Plans"
    description="Django Vue Starter offers flexible pricing options for individuals, teams, and enterprises. Choose the plan that fits your needs."
    status="planned"
    icon="dashboard"
    component-name="PricingPageView"
    layout-type="DefaultLayout"
    back-link="/"
    back-text="Back to Home"
    primary-link="/auth/register"
    primary-text="Start Free Trial"
    :features="[
      {
        title: 'Individual Plan',
        description: 'Perfect for personal projects and learning'
      },
      {
        title: 'Team Plan',
        description: 'Collaboration features for development teams'
      },
      {
        title: 'Enterprise Plan',
        description: 'Advanced features and priority support for large organizations'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
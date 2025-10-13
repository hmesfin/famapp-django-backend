<template>
  <PlaceholderView
    title="Terms of Service"
    description="Please read these terms and conditions carefully before using Django Vue Starter services and templates."
    status="planned"
    icon="settings"
    component-name="TermsPageView"
    layout-type="DefaultLayout"
    back-link="/"
    back-text="Back to Home"
    primary-link="/privacy"
    primary-text="Privacy Policy"
    :features="[
      {
        title: 'Usage Rights',
        description: 'What you can and cannot do with our templates and code'
      },
      {
        title: 'Licensing',
        description: 'Open source components and commercial usage terms'
      },
      {
        title: 'Limitations',
        description: 'Service limitations and liability disclaimers'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
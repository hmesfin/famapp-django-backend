<template>
  <PlaceholderView
    title="Privacy Policy"
    description="Your privacy is important to us. Learn how Django Vue Starter collects, uses, and protects your personal information."
    status="planned"
    icon="settings"
    component-name="PrivacyPageView"
    layout-type="DefaultLayout"
    back-link="/"
    back-text="Back to Home"
    primary-link="/terms"
    primary-text="Terms of Service"
    :features="[
      {
        title: 'Data Collection',
        description: 'What information we collect and why we collect it'
      },
      {
        title: 'Data Usage',
        description: 'How we use your information to improve our services'
      },
      {
        title: 'Data Protection',
        description: 'Security measures we take to protect your data'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
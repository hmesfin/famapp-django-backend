<template>
  <PlaceholderView
    title="Profile Settings"
    description="Manage your user profile, account preferences, and security settings. Update your information and customize your experience."
    status="in-development"
    icon="users"
    component-name="ProfileSettingsView"
    layout-type="DashboardLayout"
    :expected-props="['user', 'preferences']"
    back-link="/dashboard"
    back-text="Back to Dashboard"
    :features="[
      {
        title: 'Personal Information',
        description: 'Update your name, email, and contact details'
      },
      {
        title: 'Security Settings',
        description: 'Change password, enable 2FA, manage sessions'
      },
      {
        title: 'Preferences',
        description: 'Customize notifications, theme, and app behavior'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
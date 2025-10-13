<template>
  <PlaceholderView
    title="Dashboard Overview"
    description="Welcome to your Django Vue Starter dashboard! This is the central hub for managing your applications, monitoring performance, and accessing all features."
    status="in-development"
    icon="dashboard"
    component-name="DashboardOverviewView"
    layout-type="DashboardLayout"
    :expected-props="['stats', 'recentActivity']"
    primary-link="/dashboard/users"
    primary-text="Manage Users"
    :features="[
      {
        title: 'System Statistics',
        description: 'Monitor user activity, API usage, and system health'
      },
      {
        title: 'Recent Activity',
        description: 'Track recent user actions and system events'
      },
      {
        title: 'Quick Actions',
        description: 'Access frequently used features and management tools'
      }
    ]"
  />
</template>

<script setup lang="ts">
import { PlaceholderView } from '@/shared/components'
</script>
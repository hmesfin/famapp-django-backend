<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ welcomeMessage }}</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Here's what's happening with your Django Vue Starter application
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Users Card -->
      <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UserGroupIcon class="h-6 w-6 text-gray-400 dark:text-gray-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  Total Users
                </dt>
                <dd class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  1,234
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Sessions -->
      <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <BoltIcon class="h-6 w-6 text-gray-400 dark:text-gray-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  Active Sessions
                </dt>
                <dd class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  56
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- API Calls -->
      <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ChartBarIcon class="h-6 w-6 text-gray-400 dark:text-gray-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  API Calls Today
                </dt>
                <dd class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  12,345
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- System Status -->
      <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="h-3 w-3 bg-green-400 rounded-full"></div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  System Status
                </dt>
                <dd class="text-lg font-medium text-gray-900 dark:text-gray-100">
                  All Systems Operational
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Activity Feed -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100 mb-4">
            Recent Activity
          </h3>
          <div class="flow-root">
            <ul role="list" class="-mb-8">
              <li v-for="(activity, index) in recentActivity" :key="index">
                <div class="relative pb-8">
                  <span v-if="index !== recentActivity.length - 1" class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700" aria-hidden="true"></span>
                  <div class="relative flex space-x-3">
                    <div>
                      <span :class="[activity.iconBg, 'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white']">
                        <UserIcon class="h-4 w-4 text-white" />
                      </span>
                    </div>
                    <div class="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">
                          {{ activity.content }}
                        </p>
                      </div>
                      <div class="text-right text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
                        {{ activity.time }}
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100 mb-4">
            Quick Actions
          </h3>
          <div class="space-y-3">
            <router-link
              to="/dashboard/users"
              class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors"
            >
              <div class="flex items-center">
                <UserGroupIcon class="h-5 w-5 text-gray-400 dark:text-gray-500 mr-3" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">Users</span>
              </div>
              <ChevronRightIcon class="h-4 w-4 text-gray-400 dark:text-gray-500" />
            </router-link>

            <router-link
              to="/dashboard/invitations"
              class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors"
            >
              <div class="flex items-center">
                <EnvelopeIcon class="h-5 w-5 text-gray-400 dark:text-gray-500 mr-3" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">Invitations</span>
              </div>
              <ChevronRightIcon class="h-4 w-4 text-gray-400 dark:text-gray-500" />
            </router-link>

            <router-link
              to="/dashboard/permissions"
              class="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors"
            >
              <div class="flex items-center">
                <ShieldCheckIcon class="h-5 w-5 text-gray-400 dark:text-gray-500 mr-3" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">Permissions</span>
              </div>
              <ChevronRightIcon class="h-4 w-4 text-gray-400 dark:text-gray-500" />
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  UserGroupIcon,
  BoltIcon,
  ChartBarIcon,
  UserIcon,
  ChevronRightIcon,
  EnvelopeIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

// Personalized welcome message
const welcomeMessage = computed(() => {
  if (!authStore.user) return 'Welcome to your dashboard'
  
  const { first_name, last_name, email } = authStore.user
  const name = first_name || last_name ? `${first_name} ${last_name}`.trim() : email.split('@')[0]
  
  const hour = new Date().getHours()
  let greeting = 'Welcome back'
  if (hour < 12) greeting = 'Good morning'
  else if (hour < 17) greeting = 'Good afternoon'  
  else greeting = 'Good evening'
  
  return `${greeting}, ${name}!`
})

const recentActivity = ref([
  {
    content: 'New user registered',
    time: '2 minutes ago',
    iconBg: 'bg-green-500'
  },
  {
    content: 'User login attempt failed',
    time: '5 minutes ago',
    iconBg: 'bg-red-500'
  },
  {
    content: 'System backup completed',
    time: '1 hour ago',
    iconBg: 'bg-blue-500'
  },
  {
    content: 'New invitation sent',
    time: '2 hours ago',
    iconBg: 'bg-purple-500'
  }
])
</script>
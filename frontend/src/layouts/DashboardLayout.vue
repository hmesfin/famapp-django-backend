<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="flex h-screen">
      <!-- Sidebar -->
      <div
        :class="[
          'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        ]"
      >
        <!-- Sidebar header -->
        <div class="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
          <button
            @click="sidebarOpen = false"
            class="lg:hidden text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset p-1"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Navigation -->
        <nav class="mt-6 px-3">
          <div class="space-y-1">
            <!-- Dashboard Home -->
            <router-link
              to="/dashboard"
              class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
              :class="$route.path === '/dashboard'
                ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'"
            >
              <BriefcaseIcon
                class="mr-3 h-5 w-5 transition-colors"
                :class="$route.path === '/dashboard' ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'"
              />
              Overview
            </router-link>

            <!-- Project Management Section -->
            <div class="pt-4">
              <h3 class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Project Management
              </h3>
              <div class="mt-2 space-y-1">
                <router-link
                  to="/dashboard/projects"
                  class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/dashboard/projects')
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'"
                >
                  <FolderIcon
                    class="mr-3 h-5 w-5 transition-colors"
                    :class="$route.path.startsWith('/dashboard/projects') ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'"
                  />
                  Projects
                </router-link>
              </div>
            </div>

            <!-- User Management Section -->
            <div class="pt-4">
              <h3 class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                User Management
              </h3>
              <div class="mt-2 space-y-1">
                <router-link
                  to="/dashboard/invitations"
                  class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path.startsWith('/dashboard/invitations')
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'"
                >
                  <EnvelopeIcon
                    class="mr-3 h-5 w-5 transition-colors"
                    :class="$route.path.startsWith('/dashboard/invitations') ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'"
                  />
                  Invitations
                </router-link>
              </div>
            </div>

            <!-- Settings Section -->
            <div class="pt-4">
              <h3 class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Settings
              </h3>
              <div class="mt-2 space-y-1">
                <router-link
                  to="/dashboard/profile"
                  class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path === '/dashboard/profile' || $route.path.startsWith('/dashboard/profile/')
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'"
                >
                  <UserIcon
                    class="mr-3 h-5 w-5 transition-colors"
                    :class="$route.path === '/dashboard/profile' || $route.path.startsWith('/dashboard/profile/') ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'"
                  />
                  My Profile
                </router-link>
                
                <router-link
                  to="/dashboard/profiles"
                  class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path === '/dashboard/profiles'
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'"
                >
                  <UserGroupIcon
                    class="mr-3 h-5 w-5 transition-colors"
                    :class="$route.path === '/dashboard/profiles' ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'"
                  />
                  Browse Profiles
                </router-link>
                
                <router-link
                  to="/dashboard/settings"
                  class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="$route.path === '/dashboard/settings'
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'"
                >
                  <CogIcon
                    class="mr-3 h-5 w-5 transition-colors"
                    :class="$route.path === '/dashboard/settings' ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'"
                  />
                  Settings
                </router-link>
              </div>
            </div>
          </div>
        </nav>

        <!-- User section at bottom -->
        <div class="absolute bottom-0 w-64 p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium text-white">{{ userInitials }}</span>
              </div>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ userDisplayName }}</p>
              <button
                @click="logout"
                class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="flex-1 flex flex-col lg:pl-0">
        <!-- Top bar -->
        <div class="sticky top-0 z-40 flex h-16 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <button
            @click="sidebarOpen = true"
            class="px-4 text-gray-500 dark:text-gray-400 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 lg:hidden"
          >
            <span class="sr-only">Open sidebar</span>
            <Bars3BottomLeftIcon class="h-6 w-6" />
          </button>

          <div class="flex-1 px-4 flex justify-between items-center">
            <!-- Breadcrumbs -->
            <nav class="flex" aria-label="Breadcrumb">
              <ol class="flex items-center space-x-4">
                <li>
                  <div>
                    <router-link to="/dashboard" class="text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400">
                      <HomeIcon class="flex-shrink-0 h-5 w-5" />
                      <span class="sr-only">Home</span>
                    </router-link>
                  </div>
                </li>
                <li v-if="$route.path !== '/dashboard'">
                  <div class="flex items-center">
                    <ChevronRightIcon class="flex-shrink-0 h-5 w-5 text-gray-300 dark:text-gray-600" />
                    <span class="ml-4 text-sm font-medium text-gray-500 dark:text-gray-400 capitalize">
                      {{ $route.name?.toString().replace('dashboard-', '').replace('-', ' ') || 'Page' }}
                    </span>
                  </div>
                </li>
              </ol>
            </nav>

            <!-- Right side actions -->
            <div class="ml-4 flex items-center space-x-4">
              <!-- Theme Toggle -->
              <ThemeToggle />
              
              <!-- Notifications -->
              <button
                type="button"
                class="bg-white dark:bg-gray-800 p-1 rounded-full text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <span class="sr-only">View notifications</span>
                <BellIcon class="h-6 w-6" />
              </button>

              <!-- Quick actions -->
              <button
                type="button"
                class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Quick Action
              </button>
            </div>
          </div>
        </div>

        <!-- Page content -->
        <main class="flex-1 relative overflow-y-auto focus:outline-none">
          <div class="py-6">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <router-view />
            </div>
          </div>
        </main>
      </div>
    </div>

    <!-- Mobile sidebar overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 lg:hidden"
      @click="sidebarOpen = false"
    >
      <div class="absolute inset-0 bg-gray-600 dark:bg-gray-300 opacity-75"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/shared/composables/useConfirm'
import { useToast } from '@/shared/composables/useToast'
import ThemeToggle from '@/components/ThemeToggle.vue'
import {
  XMarkIcon,
  BriefcaseIcon,
  UserGroupIcon,
  EnvelopeIcon,
  UserIcon,
  CogIcon,
  Bars3BottomLeftIcon,
  HomeIcon,
  ChevronRightIcon,
  BellIcon,
  FolderIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const sidebarOpen = ref(false)
const { confirmLogout } = useConfirm()
const { toast } = useToast()

// User display data
const userDisplayName = computed(() => {
  if (!authStore.user) return 'Unknown User'
  
  const { first_name, last_name, email } = authStore.user
  if (first_name || last_name) {
    return `${first_name} ${last_name}`.trim()
  }
  return email
})

const userInitials = computed(() => {
  if (!authStore.user) return 'U'
  
  const { first_name, last_name, email } = authStore.user
  if (first_name && last_name) {
    return `${first_name.charAt(0).toUpperCase()}${last_name.charAt(0).toUpperCase()}`
  } else if (first_name) {
    return first_name.charAt(0).toUpperCase()
  } else if (last_name) {
    return last_name.charAt(0).toUpperCase()
  } else {
    return email.charAt(0).toUpperCase()
  }
})

const logout = async () => {
  const confirmed = await confirmLogout()
  if (confirmed) {
    await authStore.logout()
    toast.logoutSuccess()
    // Auth store handles the redirect to login
  }
}
</script>
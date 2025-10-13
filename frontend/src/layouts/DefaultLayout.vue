<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo/Brand -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">Django Vue Starter</h1>
            </router-link>
          </div>

          <!-- Navigation -->
          <nav class="hidden md:flex space-x-8">
            <router-link
              to="/"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors"
              active-class="text-blue-600 dark:text-blue-400"
            >
              Home
            </router-link>
            <router-link
              to="/features"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors"
              active-class="text-blue-600 dark:text-blue-400"
            >
              Features
            </router-link>
            <router-link
              to="/contact"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors"
              active-class="text-blue-600 dark:text-blue-400"
            >
              Contact
            </router-link>
          </nav>

          <!-- Auth Actions -->
          <div class="flex items-center space-x-4">
            <!-- Theme Toggle -->
            <ThemeToggle />
            <!-- Unauthenticated State -->
            <template v-if="!authStore.isAuthenticated">
              <router-link
                to="/auth/login"
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors"
              >
                Sign In
              </router-link>
              <router-link
                to="/auth/register"
                class="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign Up
              </router-link>
            </template>

            <!-- Authenticated State - User Dropdown -->
            <div v-else class="relative" ref="userDropdownRef">
              <button
                @click="userMenuOpen = !userMenuOpen"
                type="button"
                class="flex items-center text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                aria-expanded="false"
                aria-haspopup="true"
              >
                <span>{{ authStore.userName }}</span>
                <ChevronDownIcon
                  class="ml-2 h-4 w-4 transition-transform"
                  :class="{ 'rotate-180': userMenuOpen }"
                />
              </button>

              <!-- User Dropdown Menu -->
              <div
                v-if="userMenuOpen"
                class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-gray-800 py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                role="menu"
                aria-orientation="vertical"
              >
                <router-link
                  to="/dashboard"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  role="menuitem"
                  @click="userMenuOpen = false"
                >
                  Dashboard
                </router-link>
                <router-link
                  to="/profile"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  role="menuitem"
                  @click="userMenuOpen = false"
                >
                  Profile
                </router-link>
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:bg-gray-800 transition-colors"
                  role="menuitem"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              type="button"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset p-2"
              aria-expanded="false"
            >
              <span class="sr-only">Open main menu</span>
              <Bars3Icon v-if="!mobileMenuOpen" class="h-6 w-6" />
              <XMarkIcon v-else class="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <router-link
            to="/"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block px-3 py-2 text-base font-medium"
            @click="mobileMenuOpen = false"
          >
            Home
          </router-link>
          <router-link
            to="/features"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block px-3 py-2 text-base font-medium"
            @click="mobileMenuOpen = false"
          >
            Features
          </router-link>
          <router-link
            to="/contact"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block px-3 py-2 text-base font-medium"
            @click="mobileMenuOpen = false"
          >
            Contact
          </router-link>
          <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
            <!-- Unauthenticated State -->
            <template v-if="!authStore.isAuthenticated">
              <router-link
                to="/auth/login"
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block px-3 py-2 text-base font-medium"
                @click="mobileMenuOpen = false"
              >
                Sign In
              </router-link>
              <router-link
                to="/auth/register"
                class="bg-blue-600 text-white hover:bg-blue-700 block px-3 py-2 rounded-md text-base font-medium mt-2 mx-3"
                @click="mobileMenuOpen = false"
              >
                Sign Up
              </router-link>
            </template>

            <!-- Authenticated State -->
            <template v-else>
              <div class="px-3 py-2 text-base font-medium text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-gray-700 mb-2">
                {{ authStore.userName }}
              </div>
              <router-link
                to="/dashboard"
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block px-3 py-2 text-base font-medium"
                @click="mobileMenuOpen = false"
              >
                Dashboard
              </router-link>
              <router-link
                to="/profile"
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block px-3 py-2 text-base font-medium"
                @click="mobileMenuOpen = false"
              >
                Profile
              </router-link>
              <button
                @click="handleLogout"
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:text-blue-400 block w-full text-left px-3 py-2 text-base font-medium"
              >
                Logout
              </button>
            </template>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div class="col-span-1 md:col-span-2">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Django Vue Starter</h3>
            <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
              A modern full-stack template built with Django and Vue.js, featuring JWT authentication,
              role-based access control, and Docker orchestration.
            </p>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4">Quick Links</h4>
            <ul class="space-y-2">
              <li>
                <router-link to="/" class="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                  Home
                </router-link>
              </li>
              <li>
                <router-link to="/features" class="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                  Features
                </router-link>
              </li>
              <li>
                <router-link to="/contact" class="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                  Contact
                </router-link>
              </li>
            </ul>
          </div>
          <div>
            <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4">Legal</h4>
            <ul class="space-y-2">
              <li>
                <router-link to="/privacy" class="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                  Privacy Policy
                </router-link>
              </li>
              <li>
                <router-link to="/terms" class="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                  Terms of Service
                </router-link>
              </li>
            </ul>
          </div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <p class="text-center text-sm text-gray-500 dark:text-gray-400">
            © {{ currentYear }} Django Vue Starter. Built with cookiecutter-django and Vue.js.
          </p>
        </div>
      </div>
    </footer>

    <!-- Back to Top Button -->
    <button
      v-if="showBackToTop"
      @click="scrollToTop"
      class="fixed bottom-4 right-4 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300"
      aria-label="Back to top"
    >
      <ArrowUpIcon class="h-5 w-5" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/shared/composables/useConfirm'
import { useToast } from '@/shared/composables/useToast'
import ThemeToggle from '@/components/ThemeToggle.vue'
import {
  ChevronDownIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowUpIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const { confirmLogout } = useConfirm()
const { toast } = useToast()

const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const scrollY = ref(0)
const userDropdownRef = ref<HTMLElement>()

const currentYear = computed(() => new Date().getFullYear())
const showBackToTop = computed(() => scrollY.value > 400)

const handleScroll = () => {
  scrollY.value = window.scrollY
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const handleLogout = async () => {
  userMenuOpen.value = false
  mobileMenuOpen.value = false
  
  const confirmed = await confirmLogout()
  if (confirmed) {
    await authStore.logout()
    toast.logoutSuccess()
    // Auth store handles the redirect to login
  }
}

const handleClickOutside = (event: Event) => {
  if (userDropdownRef.value && !userDropdownRef.value.contains(event.target as Node)) {
    userMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('click', handleClickOutside)
})
</script>
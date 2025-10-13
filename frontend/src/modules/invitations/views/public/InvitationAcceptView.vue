<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo/Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome to {{ organizationName }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Complete your registration to get started
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
        <div class="flex flex-col items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Verifying invitation...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
        <div class="text-center">
          <XCircleIcon class="mx-auto h-12 w-12 text-red-500" />
          <h2 class="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
            Invalid or Expired Invitation
          </h2>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            {{ error }}
          </p>
          <router-link
            to="/"
            class="mt-6 inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Return to Home
          </router-link>
        </div>
      </div>

      <!-- Invitation Details & Form -->
      <div v-else-if="invitation" class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
        <!-- Progress Steps -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="rounded-full h-8 w-8 bg-indigo-600 text-white flex items-center justify-center text-sm font-semibold">
                1
              </div>
              <span class="ml-2 text-sm font-medium text-gray-900 dark:text-white">Verify</span>
            </div>
            <div class="flex-1 h-0.5 bg-gray-200 dark:bg-gray-700 mx-2"></div>
            <div class="flex items-center">
              <div :class="[
                'rounded-full h-8 w-8 flex items-center justify-center text-sm font-semibold',
                step >= 2 ? 'bg-indigo-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
              ]">
                2
              </div>
              <span class="ml-2 text-sm font-medium" :class="step >= 2 ? 'text-gray-900 dark:text-white' : 'text-gray-500'">
                Setup
              </span>
            </div>
            <div class="flex-1 h-0.5 bg-gray-200 dark:bg-gray-700 mx-2"></div>
            <div class="flex items-center">
              <div :class="[
                'rounded-full h-8 w-8 flex items-center justify-center text-sm font-semibold',
                step >= 3 ? 'bg-indigo-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
              ]">
                3
              </div>
              <span class="ml-2 text-sm font-medium" :class="step >= 3 ? 'text-gray-900 dark:text-white' : 'text-gray-500'">
                Accept
              </span>
            </div>
          </div>
        </div>

        <!-- Step 1: Invitation Details -->
        <div v-if="step === 1">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            You're Invited!
          </h2>
          
          <div class="space-y-4 mb-6">
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <div class="space-y-3">
                <div>
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Invited by</span>
                  <p class="text-gray-900 dark:text-white">{{ invitation.invited_by.full_name }}</p>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Your Email</span>
                  <p class="text-gray-900 dark:text-white">{{ invitation.email }}</p>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Your Name</span>
                  <p class="text-gray-900 dark:text-white">{{ invitation.full_name }}</p>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Your Role</span>
                  <p class="text-gray-900 dark:text-white capitalize">{{ invitation.role }}</p>
                </div>
                <div v-if="invitation.organization_name">
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Organization</span>
                  <p class="text-gray-900 dark:text-white">{{ invitation.organization_name }}</p>
                </div>
                <div v-if="invitation.message" class="pt-2 border-t border-gray-200 dark:border-gray-700">
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Message</span>
                  <p class="text-gray-900 dark:text-white mt-1">{{ invitation.message }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div class="flex">
                <ExclamationTriangleIcon class="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                <div class="ml-3">
                  <p class="text-sm text-yellow-800 dark:text-yellow-300">
                    This invitation expires {{ formatExpiry(invitation.expires_at) }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <button
            @click="step = 2"
            class="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Continue to Setup Account
          </button>
        </div>

        <!-- Step 2: Account Setup -->
        <div v-else-if="step === 2">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Set Up Your Account
          </h2>

          <form @submit.prevent="validatePasswordStep" class="space-y-6">
            <!-- Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Password <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="w-full px-4 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  :class="{ 'border-red-500': errors.password }"
                  placeholder="Enter a strong password"
                >
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-2 top-2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <EyeIcon v-if="!showPassword" class="h-5 w-5" />
                  <EyeSlashIcon v-else class="h-5 w-5" />
                </button>
              </div>
              <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
              
              <!-- Password Requirements -->
              <div class="mt-2 space-y-1">
                <p class="text-xs text-gray-500 dark:text-gray-400">Password must contain:</p>
                <div class="grid grid-cols-2 gap-1 text-xs">
                  <div class="flex items-center" :class="passwordChecks.minLength ? 'text-green-600' : 'text-gray-400'">
                    <CheckCircleIcon v-if="passwordChecks.minLength" class="h-3 w-3 mr-1" />
                    <XCircleIcon v-else class="h-3 w-3 mr-1" />
                    At least 8 characters
                  </div>
                  <div class="flex items-center" :class="passwordChecks.hasUppercase ? 'text-green-600' : 'text-gray-400'">
                    <CheckCircleIcon v-if="passwordChecks.hasUppercase" class="h-3 w-3 mr-1" />
                    <XCircleIcon v-else class="h-3 w-3 mr-1" />
                    One uppercase letter
                  </div>
                  <div class="flex items-center" :class="passwordChecks.hasLowercase ? 'text-green-600' : 'text-gray-400'">
                    <CheckCircleIcon v-if="passwordChecks.hasLowercase" class="h-3 w-3 mr-1" />
                    <XCircleIcon v-else class="h-3 w-3 mr-1" />
                    One lowercase letter
                  </div>
                  <div class="flex items-center" :class="passwordChecks.hasNumber ? 'text-green-600' : 'text-gray-400'">
                    <CheckCircleIcon v-if="passwordChecks.hasNumber" class="h-3 w-3 mr-1" />
                    <XCircleIcon v-else class="h-3 w-3 mr-1" />
                    One number
                  </div>
                </div>
              </div>
            </div>

            <!-- Confirm Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Confirm Password <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="form.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  required
                  class="w-full px-4 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  :class="{ 'border-red-500': errors.confirmPassword }"
                  placeholder="Confirm your password"
                >
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="absolute right-2 top-2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <EyeIcon v-if="!showConfirmPassword" class="h-5 w-5" />
                  <EyeSlashIcon v-else class="h-5 w-5" />
                </button>
              </div>
              <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ errors.confirmPassword }}</p>
            </div>

            <!-- Actions -->
            <div class="flex gap-3">
              <button
                type="button"
                @click="step = 1"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
              >
                Back
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Continue
              </button>
            </div>
          </form>
        </div>

        <!-- Step 3: Terms & Privacy -->
        <div v-else-if="step === 3">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Terms & Conditions
          </h2>

          <form @submit.prevent="handleAcceptInvitation" class="space-y-6">
            <!-- Terms Checkbox -->
            <div class="space-y-4">
              <label class="flex items-start cursor-pointer">
                <input
                  v-model="form.acceptTerms"
                  type="checkbox"
                  required
                  class="mt-1 h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                >
                <span class="ml-3 text-sm text-gray-700 dark:text-gray-300">
                  I agree to the 
                  <a href="/terms" target="_blank" class="text-indigo-600 hover:text-indigo-700 underline">
                    Terms of Service
                  </a>
                  and
                  <a href="/privacy" target="_blank" class="text-indigo-600 hover:text-indigo-700 underline">
                    Privacy Policy
                  </a>
                </span>
              </label>

              <label class="flex items-start cursor-pointer">
                <input
                  v-model="form.acceptMarketing"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                >
                <span class="ml-3 text-sm text-gray-700 dark:text-gray-300">
                  I would like to receive product updates and marketing emails (optional)
                </span>
              </label>
            </div>

            <!-- Summary -->
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Account Summary</h3>
              <div class="space-y-1 text-sm">
                <p class="text-gray-600 dark:text-gray-400">
                  <span class="font-medium">Name:</span> {{ invitation.full_name }}
                </p>
                <p class="text-gray-600 dark:text-gray-400">
                  <span class="font-medium">Email:</span> {{ invitation.email }}
                </p>
                <p class="text-gray-600 dark:text-gray-400">
                  <span class="font-medium">Role:</span> {{ invitation.role }}
                </p>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="errors.general" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p class="text-sm text-red-800 dark:text-red-300">{{ errors.general }}</p>
            </div>

            <!-- Actions -->
            <div class="flex gap-3">
              <button
                type="button"
                @click="step = 2"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
                :disabled="submitting"
              >
                Back
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="!form.acceptTerms || submitting"
              >
                <span v-if="!submitting">Create Account</span>
                <span v-else class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInvitationAcceptance } from '../../composables/useInvitationAcceptance'
import { useAuthStore } from '@/stores/auth'
import type { Invitation } from '../../types/invitation.types'
import {
  XCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { invitation, loading, error, verifyInvitationToken, acceptInvitation } = useInvitationAcceptance()

// State
const step = ref(1)
const submitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Form
const form = reactive({
  password: '',
  confirmPassword: '',
  acceptTerms: false,
  acceptMarketing: false
})

// Errors
const errors = reactive({
  password: '',
  confirmPassword: '',
  general: ''
})

// Computed
const organizationName = computed(() => {
  return invitation.value?.organization_name || 'Django Vue Starter'
})

const passwordChecks = computed(() => ({
  minLength: form.password.length >= 8,
  hasUppercase: /[A-Z]/.test(form.password),
  hasLowercase: /[a-z]/.test(form.password),
  hasNumber: /\d/.test(form.password)
}))

const isPasswordValid = computed(() => {
  return Object.values(passwordChecks.value).every(check => check)
})

// Watch password changes to clear errors
watch(() => form.password, () => {
  errors.password = ''
})

watch(() => form.confirmPassword, () => {
  errors.confirmPassword = ''
})

// Methods
const formatExpiry = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(date.getTime() - now.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return 'today'
  } else if (diffDays === 1) {
    return 'tomorrow'
  } else {
    return `in ${diffDays} days`
  }
}

const validatePasswordStep = () => {
  errors.password = ''
  errors.confirmPassword = ''
  
  if (!isPasswordValid.value) {
    errors.password = 'Password does not meet all requirements'
    return
  }
  
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    return
  }
  
  step.value = 3
}

const handleAcceptInvitation = async () => {
  if (!invitation.value || !form.acceptTerms) return
  
  submitting.value = true
  errors.general = ''
  
  try {
    const response = await acceptInvitation({
      token: route.query.token as string,
      first_name: invitation.value.first_name || '',
      last_name: invitation.value.last_name || '',
      password: form.password,
      password_confirm: form.confirmPassword
    })
    
    if (response.access && response.refresh) {
      // Success handling is done in the composable
      // Small delay to show success message
      setTimeout(() => {
        router.push('/dashboard')
      }, 1000)
    }
  } catch (err: any) {
    console.error('Failed to accept invitation:', err)
    errors.general = err.message || 'Failed to create account. Please try again.'
    submitting.value = false
  }
}

// Load invitation on mount
onMounted(async () => {
  const token = route.query.token as string
  
  if (!token) {
    error.value = 'No invitation token provided'
    loading.value = false
    return
  }
  
  try {
    const response = await verifyInvitationToken(token)
    
    if (!response) {
      error.value = 'Unable to verify invitation. Please try again.'
      loading.value = false
      return
    }
    
    if (response.is_expired) {
      error.value = 'This invitation has expired. Please request a new one.'
    } else if (response.status === 'accepted') {
      error.value = 'This invitation has already been accepted.'
    } else if (response.status === 'cancelled') {
      error.value = 'This invitation has been cancelled.'
    } else {
      invitation.value = response
    }
  } catch (err: any) {
    console.error('Failed to verify invitation:', err)
    error.value = err.response?.data?.detail || 'Invalid invitation token'
  } finally {
    loading.value = false
  }
})
</script>
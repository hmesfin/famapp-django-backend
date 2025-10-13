<template>
  <div class="w-full max-w-md mx-auto">
    <BaseCard class="shadow-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">Email Verification</h2>
        <p class="mt-2 text-sm text-secondary-600 dark:text-secondary-400">
          Verifying your email address to activate your account.
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isVerifying" class="text-center py-8">
        <div class="flex justify-center mb-4">
          <div class="w-16 h-16 bg-primary-100 dark:bg-primary-900/50 rounded-full flex items-center justify-center">
            <svg class="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
          </div>
        </div>
        <h3 class="text-lg font-medium text-secondary-900 dark:text-secondary-100 mb-2">Verifying Email</h3>
        <p class="text-secondary-600 dark:text-secondary-400">Please wait while we verify your email address...</p>
      </div>

      <!-- Success State -->
      <div v-else-if="isVerified" class="text-center py-8">
        <div class="flex justify-center mb-4">
          <div class="w-16 h-16 bg-success-100 dark:bg-success-900/50 rounded-full flex items-center justify-center">
            <CheckCircleIcon class="w-8 h-8 text-success-600 dark:text-success-400" />
          </div>
        </div>
        <h3 class="text-lg font-medium text-secondary-900 dark:text-secondary-100 mb-2">Email Verified Successfully!</h3>
        <p class="text-sm text-secondary-600 dark:text-secondary-400 mb-6">
          Your account has been activated. You can now sign in to Django Vue Starter.
        </p>
        <BaseButton
          tag="router-link"
          to="/auth/login"
          variant="success"
          size="md"
        >
          Continue to Sign In
        </BaseButton>
      </div>

      <!-- Error State -->
      <div v-else-if="errorMessage" class="text-center py-8">
        <div class="flex justify-center mb-4">
          <div class="w-16 h-16 bg-danger-100 dark:bg-danger-900/50 rounded-full flex items-center justify-center">
            <ExclamationCircleIcon class="w-8 h-8 text-danger-600 dark:text-danger-400" />
          </div>
        </div>
        <h3 class="text-lg font-medium text-secondary-900 dark:text-secondary-100 mb-4">Verification Failed</h3>
        <div class="mb-6 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-md">
          <p class="text-sm text-danger-700 dark:text-danger-300">
            {{ errorMessage }}
          </p>
        </div>
        <div class="space-y-3">
          <BaseButton
            tag="router-link"
            to="/auth/register"
            variant="secondary"
            size="md"
            block
          >
            Back to Registration
          </BaseButton>
          <BaseButton
            @click="resendVerification"
            variant="primary"
            size="md"
            :disabled="isResending"
            :loading="isResending"
            :loading-text="'Resending...'"
            block
          >
            Resend Verification Email
          </BaseButton>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BaseButton, BaseCard } from '@/shared/components'
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/vue/20/solid'

// Router and route
const route = useRoute()
const router = useRouter()

// State
const isVerifying = ref(true)
const isVerified = ref(false)
const isResending = ref(false)
const errorMessage = ref('')

// API call to verify email
const verifyEmail = async (token: string): Promise<{
  success: boolean
  message?: string
  error?: string
}> => {
  try {
    const response = await fetch(`${import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'}/auth/verify-email/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    })

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        error: data.error || data.detail || 'Email verification failed'
      }
    }

    return {
      success: true,
      message: data.message || 'Email verified successfully'
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error. Please check your connection and try again.'
    }
  }
}

// API call to resend verification email
const resendVerificationEmail = async (email?: string): Promise<{
  success: boolean
  message?: string
  error?: string
}> => {
  try {
    const response = await fetch(`${import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'}/auth/resend-verification/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    })

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        error: data.error || data.detail || 'Failed to resend verification email'
      }
    }

    return {
      success: true,
      message: data.message || 'Verification email sent successfully'
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error. Please check your connection and try again.'
    }
  }
}

// Handle email verification on mount
const handleVerification = async () => {
  const token = route.query.token as string

  if (!token) {
    errorMessage.value = 'Invalid verification link. Please check your email and try again.'
    isVerifying.value = false
    return
  }

  try {
    const result = await verifyEmail(token)

    if (result.success) {
      isVerified.value = true
    } else {
      errorMessage.value = result.error || 'Email verification failed. The link may have expired or already been used.'
    }
  } catch (error) {
    console.error('Verification error:', error)
    errorMessage.value = 'An unexpected error occurred during verification. Please try again.'
  } finally {
    isVerifying.value = false
  }
}

// Handle resend verification
const resendVerification = async () => {
  isResending.value = true
  errorMessage.value = ''

  try {
    const email = route.query.email as string || ''
    const result = await resendVerificationEmail(email)

    if (result.success) {
      // Show success message and redirect to a confirmation page
      router.push({
        path: '/auth/register',
        query: { resent: '1' }
      })
    } else {
      errorMessage.value = result.error || 'Failed to resend verification email. Please try again.'
    }
  } catch (error) {
    console.error('Resend error:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isResending.value = false
  }
}

// Start verification when component mounts
onMounted(() => {
  handleVerification()
})
</script>
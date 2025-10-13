<template>
  <div class="w-full max-w-md mx-auto">
    <BaseCard class="shadow-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">Forgot Password</h2>
        <p class="mt-2 text-sm text-secondary-600 dark:text-secondary-400">
          Enter your email address and we'll send you a link to reset your password.
        </p>
      </div>

      <!-- Success Message -->
      <div
        v-if="isSubmitted"
        class="mb-6 p-4 bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-md"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-5 w-5 text-success-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-success-700 dark:text-success-300">
              {{ successMessage }}
            </p>
            <p class="text-xs text-success-600 dark:text-success-400 mt-2">
              Check your email for the reset link. It may take a few minutes to arrive.
            </p>
            <div class="mt-3">
              <BaseButton
                tag="router-link"
                to="/auth/login"
                variant="success"
                size="sm"
              >
                Back to Sign In
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <form v-if="!isSubmitted" @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Email Field -->
        <BaseInput
          id="email"
          v-model="form.email"
          type="email"
          label="Email Address"
          placeholder="Enter your email address"
          :disabled="isLoading"
          :error="!!errors.email"
          :error-message="errors.email"
          autocomplete="email"
          help-text="We'll send a password reset link to this email address"
          required
        />

        <!-- Error Message Display -->
        <ErrorMessage
          v-if="errorMessage"
          :show="!!errorMessage"
          type="error"
          :message="errorMessage"
          dismissible
          @dismiss="clearError"
        />

        <!-- Submit Button -->
        <BaseButton
          type="submit"
          variant="primary"
          size="md"
          :disabled="isLoading || !isFormValid"
          :loading="isLoading"
          :loading-text="'Sending Link...'"
          block
          class="justify-center"
        >
          Send Reset Link
        </BaseButton>
      </form>

      <!-- Back to Login Link -->
      <div v-if="!isSubmitted" class="text-center mt-6">
        <router-link
          to="/auth/login"
          class="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-500 focus:outline-none focus:underline transition-colors duration-200"
        >
          ← Back to Sign In
        </router-link>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ErrorMessage, BaseButton, BaseInput, BaseCard } from '@/shared/components'
import { CheckCircleIcon } from '@heroicons/vue/20/solid'

// State
const form = reactive({
  email: '',
})

const isLoading = ref(false)
const isSubmitted = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Form validation errors
const errors = reactive({
  email: '',
})

// Computed properties
const isFormValid = computed(() => {
  return form.email.length > 0 && isValidEmail(form.email)
})

// Helper functions
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateForm = (): boolean => {
  errors.email = ''

  if (!form.email) {
    errors.email = 'Email address is required'
    return false
  } else if (!isValidEmail(form.email)) {
    errors.email = 'Please enter a valid email address'
    return false
  }

  return true
}

const clearError = () => {
  errorMessage.value = ''
}

const clearErrors = () => {
  errors.email = ''
  errorMessage.value = ''
}

// API call function
const sendPasswordResetEmail = async (
  email: string,
): Promise<{
  success: boolean
  message?: string
  error?: string
}> => {
  try {
    const response = await fetch(
      `${import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'}/auth/forgot-password/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      },
    )

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Failed to send password reset email',
      }
    }

    return {
      success: true,
      message: data.message,
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error. Please check your connection and try again.',
    }
  }
}

// Form submission handler
const handleSubmit = async () => {
  clearErrors()

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const result = await sendPasswordResetEmail(form.email)

    if (result.success) {
      successMessage.value = result.message || 'Password reset link sent successfully!'
      isSubmitted.value = true
    } else {
      errorMessage.value = result.error || 'Failed to send password reset email. Please try again.'
    }
  } catch (error) {
    console.error('Forgot password error:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md mx-auto">
    <BaseCard class="shadow-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">Reset Password</h2>
        <p class="mt-2 text-sm text-secondary-600 dark:text-secondary-400">
          Choose a strong new password for your account.
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
              You can now sign in with your new password.
            </p>
            <div class="mt-3">
              <BaseButton
                tag="router-link"
                to="/auth/login"
                variant="success"
                size="sm"
              >
                Go to Sign In →
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <form v-if="!isSubmitted" @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Password Field -->
        <div>
          <BaseInput
            id="password"
            v-model="form.password"
            type="password"
            label="New Password"
            placeholder="Enter your new password"
            :disabled="isLoading"
            :error="!!errors.password"
            :error-message="errors.password"
            autocomplete="new-password"
            required
          />
          
          <!-- Password Requirements -->
          <div class="mt-3 p-3 bg-secondary-50 dark:bg-secondary-800 rounded-md">
            <h4 class="text-sm font-medium text-secondary-900 dark:text-secondary-100 mb-2">
              Password Requirements:
            </h4>
            <div class="space-y-1">
              <div v-for="requirement in passwordRequirements" :key="requirement.text" class="flex items-center text-xs">
                <CheckIcon v-if="requirement.met" class="h-3 w-3 text-success-500 mr-2" />
                <XMarkIcon v-else class="h-3 w-3 text-secondary-400 mr-2" />
                <span :class="requirement.met ? 'text-success-600 dark:text-success-400' : 'text-secondary-600 dark:text-secondary-400'">
                  {{ requirement.text }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Confirm Password Field -->
        <BaseInput
          id="password-confirm"
          v-model="form.passwordConfirm"
          type="password"
          label="Confirm New Password"
          placeholder="Confirm your new password"
          :disabled="isLoading"
          :error="!!errors.passwordConfirm"
          :error-message="errors.passwordConfirm"
          autocomplete="new-password"
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
          :loading-text="'Resetting Password...'"
          block
          class="justify-center"
        >
          Reset Password
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
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ErrorMessage, BaseButton, BaseInput, BaseCard } from '@/shared/components'
import { CheckCircleIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const route = useRoute()

// State
const form = reactive({
  password: '',
  passwordConfirm: '',
})

const isLoading = ref(false)
const isSubmitted = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Form validation errors
const errors = reactive({
  password: '',
  passwordConfirm: '',
})

// Password requirements computation
const passwordRequirements = computed(() => [
  {
    text: 'At least 8 characters',
    met: form.password.length >= 8
  },
  {
    text: 'Contains uppercase letter',
    met: /[A-Z]/.test(form.password)
  },
  {
    text: 'Contains lowercase letter',
    met: /[a-z]/.test(form.password)
  },
  {
    text: 'Contains number',
    met: /\d/.test(form.password)
  },
  {
    text: 'Contains special character',
    met: /[^A-Za-z0-9]/.test(form.password)
  }
])

const passwordStrengthScore = computed(() => {
  return passwordRequirements.value.filter(req => req.met).length
})

// Computed properties
const isFormValid = computed(() => {
  return (
    form.password.length >= 8 &&
    form.passwordConfirm.length >= 8 &&
    form.password === form.passwordConfirm &&
    passwordStrengthScore.value >= 3 // Require at least 3 out of 5 requirements
  )
})

// Helper functions
const validateForm = (): boolean => {
  errors.password = ''
  errors.passwordConfirm = ''

  let isValid = true

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    isValid = false
  }

  if (!form.passwordConfirm) {
    errors.passwordConfirm = 'Password confirmation is required'
    isValid = false
  } else if (form.password !== form.passwordConfirm) {
    errors.passwordConfirm = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const clearError = () => {
  errorMessage.value = ''
}

const clearErrors = () => {
  errors.password = ''
  errors.passwordConfirm = ''
  errorMessage.value = ''
}

// API call function
const resetPassword = async (
  token: string,
  uid: string,
  password: string,
  passwordConfirm: string,
): Promise<{
  success: boolean
  message?: string
  error?: string
}> => {
  try {
    const response = await fetch(
      `${import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'}/auth/reset-password/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          uid,
          password,
          password_confirm: passwordConfirm,
        }),
      },
    )

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Failed to reset password',
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

  const token = route.query.token as string
  const uid = route.query.uid as string

  if (!token || !uid) {
    errorMessage.value = 'Invalid reset link. Please request a new password reset.'
    return
  }

  isLoading.value = true

  try {
    const result = await resetPassword(token, uid, form.password, form.passwordConfirm)

    if (result.success) {
      successMessage.value = result.message || 'Password reset successfully!'
      isSubmitted.value = true
    } else {
      errorMessage.value = result.error || 'Failed to reset password. Please try again.'
    }
  } catch (error) {
    console.error('Reset password error:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// Check for valid reset link on mount
onMounted(() => {
  const token = route.query.token as string
  const uid = route.query.uid as string

  if (!token || !uid) {
    errorMessage.value = 'Invalid reset link. Please request a new password reset.'
  }
})
</script>

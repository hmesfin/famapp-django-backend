<template>
  <div class="w-full max-w-md mx-auto">
    <BaseCard class="shadow-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">Create Account</h2>
        <p class="mt-2 text-sm text-secondary-600 dark:text-secondary-400">
          Join Django Vue Starter and start building amazing applications.
        </p>
      </div>

      <!-- Success Message -->
      <div
        v-if="isRegistered"
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
            <p class="text-xs text-success-600 dark:text-success-400 mt-1">
              Please check your email to verify your account before signing in.
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

      <form v-if="!isRegistered" @submit.prevent="handleSubmit" class="space-y-6">
        <!-- First Name Field -->
        <BaseInput
          id="firstName"
          v-model="form.firstName"
          type="text"
          label="First Name"
          placeholder="Enter your first name"
          :disabled="isLoading"
          :error="!!errors.firstName"
          :error-message="errors.firstName"
          autocomplete="given-name"
          required
        />

        <!-- Last Name Field -->
        <BaseInput
          id="lastName"
          v-model="form.lastName"
          type="text"
          label="Last Name"
          placeholder="Enter your last name"
          :disabled="isLoading"
          :error="!!errors.lastName"
          :error-message="errors.lastName"
          autocomplete="family-name"
          required
        />

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
          required
        />

        <!-- Password Field -->
        <div>
          <BaseInput
            id="password"
            v-model="form.password"
            type="password"
            label="Password"
            placeholder="Create a secure password"
            :disabled="isLoading"
            :error="!!errors.password"
            :error-message="errors.password"
            autocomplete="new-password"
            required
          />
          
          <!-- Password Strength Indicator -->
          <div v-if="form.password" class="mt-2">
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs text-secondary-600 dark:text-secondary-400">Password strength:</span>
              <span :class="passwordStrengthTextClass" class="text-xs font-medium">
                {{ passwordStrengthText }}
              </span>
            </div>
            <div class="w-full bg-secondary-200 dark:bg-secondary-700 rounded-full h-1.5">
              <div 
                :class="passwordStrengthBarClass" 
                class="h-1.5 rounded-full transition-all duration-300"
                :style="{ width: passwordStrengthPercentage + '%' }"
              ></div>
            </div>
            <div class="mt-2 space-y-1">
              <div v-for="requirement in passwordRequirements" :key="requirement.text" class="flex items-center text-xs">
                <CheckIcon v-if="requirement.met" class="h-3 w-3 text-success-500 mr-1" />
                <XMarkIcon v-else class="h-3 w-3 text-secondary-400 mr-1" />
                <span :class="requirement.met ? 'text-success-600 dark:text-success-400' : 'text-secondary-600 dark:text-secondary-400'">
                  {{ requirement.text }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Confirm Password Field -->
        <BaseInput
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          label="Confirm Password"
          placeholder="Confirm your password"
          :disabled="isLoading"
          :error="!!errors.confirmPassword"
          :error-message="errors.confirmPassword"
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
          :loading-text="'Creating Account...'"
          block
          class="justify-center"
        >
          Create Account
        </BaseButton>
      </form>

      <!-- Sign In Link -->
      <div v-if="!isRegistered" class="text-center mt-6">
        <p class="text-sm text-secondary-600 dark:text-secondary-400">
          Already have an account?
          <router-link
            to="/auth/login"
            class="font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 focus:outline-none focus:underline transition-colors duration-200"
          >
            Sign In
          </router-link>
        </p>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ErrorMessage, BaseButton, BaseInput, BaseCard } from '@/shared/components'
import { CheckCircleIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'

// State
const form = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const isLoading = ref(false)
const isRegistered = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Form validation errors
const errors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
})

// Password strength computation
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

const passwordStrengthPercentage = computed(() => {
  return (passwordStrengthScore.value / passwordRequirements.value.length) * 100
})

const passwordStrengthText = computed(() => {
  const score = passwordStrengthScore.value
  if (score <= 1) return 'Very Weak'
  if (score === 2) return 'Weak'
  if (score === 3) return 'Fair'
  if (score === 4) return 'Good'
  return 'Strong'
})

const passwordStrengthTextClass = computed(() => {
  const score = passwordStrengthScore.value
  if (score <= 1) return 'text-danger-600 dark:text-danger-400'
  if (score === 2) return 'text-warning-600 dark:text-warning-400'
  if (score === 3) return 'text-info-600 dark:text-info-400'
  if (score === 4) return 'text-primary-600 dark:text-primary-400'
  return 'text-success-600 dark:text-success-400'
})

const passwordStrengthBarClass = computed(() => {
  const score = passwordStrengthScore.value
  if (score <= 1) return 'bg-danger-500'
  if (score === 2) return 'bg-warning-500'
  if (score === 3) return 'bg-info-500'
  if (score === 4) return 'bg-primary-500'
  return 'bg-success-500'
})

// Computed properties
const isFormValid = computed(() => {
  return (
    form.firstName.length > 0 &&
    form.lastName.length > 0 &&
    form.email.length > 0 &&
    form.password.length >= 8 &&
    form.confirmPassword.length >= 8 &&
    form.password === form.confirmPassword &&
    isValidEmail(form.email) &&
    passwordStrengthScore.value >= 3 // Require at least 'Fair' password strength
  )
})

// Helper functions
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateForm = (): boolean => {
  // Clear previous errors
  errors.firstName = ''
  errors.lastName = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  let isValid = true

  if (!form.firstName.trim()) {
    errors.firstName = 'First name is required'
    isValid = false
  }

  if (!form.lastName.trim()) {
    errors.lastName = 'Last name is required'
    isValid = false
  }

  if (!form.email) {
    errors.email = 'Email address is required'
    isValid = false
  } else if (!isValidEmail(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    isValid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Password confirmation is required'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const clearError = () => {
  errorMessage.value = ''
}

const clearErrors = () => {
  errors.firstName = ''
  errors.lastName = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''
  errorMessage.value = ''
}

// API call function
const registerUser = async (userData: {
  first_name: string
  last_name: string
  email: string
  password: string
  password_confirm: string
}): Promise<{
  success: boolean
  message?: string
  error?: string
  user?: any
}> => {
  try {
    const response = await fetch(
      `${import.meta.env.VITE_APP_API_URL || 'http://localhost:8000/api'}/auth/register/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      },
    )

    const data = await response.json()

    if (!response.ok) {
      return {
        success: false,
        error: data.error || data.detail || 'Registration failed',
      }
    }

    return {
      success: true,
      message: data.message,
      user: data.user,
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
    const result = await registerUser({
      first_name: form.firstName,
      last_name: form.lastName,
      email: form.email,
      password: form.password,
      password_confirm: form.confirmPassword,
    })

    if (result.success) {
      successMessage.value =
        result.message || 'Registration successful! Please check your email to verify your account.'
      isRegistered.value = true
    } else {
      errorMessage.value = result.error || 'Registration failed. Please try again.'
    }
  } catch (error) {
    console.error('Registration error:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md mx-auto">
    <BaseCard class="shadow-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">Sign In</h2>
        <p class="mt-2 text-sm text-secondary-600 dark:text-secondary-400">
          Welcome back! Please sign in to your account.
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Email Field -->
      <BaseInput
        id="email"
        v-model="form.email"
        type="email"
        label="Email Address"
        placeholder="Enter your email address"
        :disabled="authStore.isLoading"
        :error="!!errors.email"
        :error-message="errors.email"
        autocomplete="email"
        required
      />

      <!-- Password Field -->
      <BaseInput
        id="password"
        v-model="form.password"
        type="password"
        label="Password"
        placeholder="Enter your password"
        :disabled="authStore.isLoading"
        :error="!!errors.password"
        :error-message="errors.password"
        autocomplete="current-password"
        required
      />

      <!-- Remember Me Checkbox -->
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
            :disabled="authStore.isLoading"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 dark:border-secondary-600 rounded"
          />
          <label for="remember" class="ml-2 block text-sm text-secondary-700 dark:text-secondary-300">
            Remember me
          </label>
        </div>

        <div class="text-sm">
          <router-link
            to="/auth/forgot-password"
            class="font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 focus:outline-none focus:underline transition-colors duration-200"
          >
            Forgot your password?
          </router-link>
        </div>
      </div>

      <!-- Error Message Display -->
      <ErrorMessage
        v-if="authStore.error"
        :show="!!authStore.error"
        type="error"
        :message="authStore.error"
        dismissible
        @dismiss="clearError"
      />

      <!-- Submit Button -->
      <BaseButton
        type="submit"
        variant="primary"
        size="md"
        :disabled="authStore.isLoading || !isFormValid"
        :loading="authStore.isLoading"
        :loading-text="'Signing In...'"
        block
        class="justify-center"
      >
        Sign In
      </BaseButton>

      <!-- Sign Up Link -->
      <div class="text-center">
        <p class="text-sm text-secondary-600 dark:text-secondary-400">
          Don't have an account?
          <router-link
            to="/auth/register"
            class="font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 focus:outline-none focus:underline transition-colors duration-200"
          >
            Sign up here
          </router-link>
        </p>
      </div>
    </form>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ErrorMessage, BaseButton, BaseInput, BaseCard } from '@/shared/components'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/shared/composables/useToast'

// Store and router setup
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { toast } = useToast()

// Form data
const form = reactive({
  email: '',
  password: '',
  remember: false,
})


// Form validation errors
const errors = reactive({
  email: '',
  password: '',
})

// Computed properties
const isFormValid = computed(() => {
  return form.email.length > 0 && form.password.length > 0 && isValidEmail(form.email)
})

// Helper functions
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateForm = (): boolean => {
  // Clear previous errors
  errors.email = ''
  errors.password = ''

  let isValid = true

  // Email validation
  if (!form.email) {
    errors.email = 'Email address is required'
    isValid = false
  } else if (!isValidEmail(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  // Password validation
  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters'
    isValid = false
  }

  return isValid
}

const clearError = () => {
  authStore.clearError()
}

const clearErrors = () => {
  errors.email = ''
  errors.password = ''
  authStore.clearError()
}

// Form submission handler
const handleSubmit = async () => {
  clearErrors()

  if (!validateForm()) {
    return
  }

  const result = await authStore.login({
    email: form.email,
    password: form.password,
    remember: form.remember,
  })

  if (result.success) {
    // Show success toast
    toast.loginSuccess(authStore.user?.first_name || authStore.user?.email)

    // Redirect to intended page or dashboard
    const redirectTo = (route.query.redirect as string) || '/dashboard'
    await router.push(redirectTo)
  } else if ((result as any).requires_email_verification) {
    // Show email verification toast with resend option
    const emailResult = result as any

    if (emailResult.email_sent) {
      toast.emailSent(emailResult.email || form.email)
    }

    toast.emailVerificationRequired(emailResult.email || form.email, async () => {
      // Resend verification email
      try {
        const response = await fetch('/api/auth/resend-verification/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: form.email }),
        })

        if (response.ok) {
          toast.success('Verification email sent! Check your inbox.')
        } else {
          toast.error('Failed to send verification email. Please try again.')
        }
      } catch (error) {
        toast.error('Network error. Please check your connection.')
      }
    })
  } else {
    // Show general error toast
    toast.error(result.error || 'Login failed. Please try again.')
  }
}

// Auto-fill remembered email on component mount
const checkRememberedUser = () => {
  const rememberedEmail = localStorage.getItem('rememberedEmail')
  const rememberMe = localStorage.getItem('rememberMe')

  if (rememberMe === 'true' && rememberedEmail) {
    form.email = rememberedEmail
    form.remember = true
  }
}

// Redirect authenticated users away from login page
const redirectIfAuthenticated = () => {
  if (authStore.isAuthenticated) {
    console.log('User already authenticated, redirecting to dashboard')
    const redirectTo = (route.query.redirect as string) || '/dashboard'
    router.replace(redirectTo)
  }
}

// Initialize component
onMounted(() => {
  checkRememberedUser()
  redirectIfAuthenticated()
})

// Also check when auth state changes
authStore.$subscribe((mutation, state) => {
  redirectIfAuthenticated()
})
</script>

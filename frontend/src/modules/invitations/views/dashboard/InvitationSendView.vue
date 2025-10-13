<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Header -->
    <div class="mb-8">
      <button
        @click="router.push({ name: 'invitations' })"
        class="mb-4 text-secondary-600 dark:text-secondary-400 hover:text-secondary-900 dark:hover:text-secondary-100 flex items-center gap-2"
      >
        <ArrowLeftIcon class="h-5 w-5" />
        Back to Invitations
      </button>
      
      <h1 class="text-3xl font-bold text-secondary-900 dark:text-secondary-100">
        Send Invitation
      </h1>
      <p class="text-secondary-600 dark:text-secondary-400 mt-2">
        Invite new team members to join your organization
      </p>
    </div>

    <!-- Form Card -->
    <BaseCard variant="elevated" size="lg">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Single or Bulk Toggle -->
        <div class="flex gap-4 mb-6">
          <BaseButton
            :variant="!isBulkMode ? 'primary' : 'secondary'"
            size="md"
            block
            :leading-icon="EnvelopeIcon"
            @click="toggleMode('single')"
          >
            Single Invitation
          </BaseButton>
          <BaseButton
            :variant="isBulkMode ? 'primary' : 'secondary'"
            size="md"
            block
            :leading-icon="EnvelopeOpenIcon"
            @click="toggleMode('bulk')"
          >
            Bulk Invitations
          </BaseButton>
        </div>

        <!-- Single Mode -->
        <div v-if="!isBulkMode" class="space-y-6">
          <!-- Name Fields -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BaseInput
              v-model="form.first_name"
              label="First Name"
              type="text"
              placeholder="John"
              required
              :error="!!errors.first_name"
              :error-message="errors.first_name"
            />
            
            <BaseInput
              v-model="form.last_name"
              label="Last Name"
              type="text"
              placeholder="Doe"
              required
              :error="!!errors.last_name"
              :error-message="errors.last_name"
            />
          </div>

          <!-- Email -->
          <BaseInput
            v-model="form.email"
            label="Email Address"
            type="email"
            placeholder="john.doe@example.com"
            required
            :error="!!errors.email"
            :error-message="errors.email"
          />
        </div>

        <!-- Bulk Mode - CSV Upload Placeholder -->
        <div v-else class="space-y-6">
          <div class="bg-secondary-50 dark:bg-secondary-900 border-2 border-dashed border-secondary-300 dark:border-secondary-600 rounded-lg p-8 text-center">
            <DocumentArrowUpIcon class="mx-auto h-12 w-12 text-secondary-400" />
            <h3 class="mt-4 text-lg font-medium text-secondary-900 dark:text-secondary-100">
              CSV Upload Coming Soon
            </h3>
            <p class="mt-2 text-sm text-secondary-600 dark:text-secondary-400">
              Upload a CSV file with multiple invitations including names, emails, and roles.
            </p>
            <p class="mt-4 text-xs text-secondary-500 dark:text-secondary-400">
              Expected format: First Name, Last Name, Email, Role, Organization (optional)
            </p>
            <BaseButton
              disabled
              variant="ghost"
              size="md"
              :leading-icon="DocumentArrowUpIcon"
              class="mt-6"
            >
              Select CSV File (Coming Soon)
            </BaseButton>
          </div>
        </div>

        <!-- Common Fields - Only show in single mode -->
        <!-- Role Selection -->
        <div v-if="!isBulkMode">
          <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
            Role <span class="text-danger-500">*</span>
          </label>
          <select
            v-model="form.role"
            required
            class="form-select w-full px-4 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-700 text-secondary-900 dark:text-secondary-100 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option v-for="role in availableRoles" :key="role" :value="role">
              {{ getRoleDisplayName(role) }}
            </option>
          </select>
          <p class="mt-1 text-sm text-secondary-600 dark:text-secondary-400">
            {{ getRoleDescription(form.role) }}
          </p>
        </div>

        <!-- Organization Name - Only in single mode -->
        <BaseInput
          v-if="!isBulkMode"
          v-model="form.organization_name"
          label="Organization Name (Optional)"
          type="text"
          placeholder="Your Organization"
        />

        <!-- Personal Message - Only in single mode -->
        <BaseInput
          v-if="!isBulkMode"
          v-model="form.message"
          label="Personal Message (Optional)"
          type="textarea"
          :rows="4"
          placeholder="Add a personal message to your invitation..."
        />

        <!-- Preview Section - Only in single mode -->
        <div v-if="!isBulkMode" class="bg-secondary-50 dark:bg-secondary-900 rounded-lg p-4">
          <h3 class="text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-3">
            Preview
          </h3>
          <div class="text-sm text-secondary-600 dark:text-secondary-400 space-y-1">
            <p>
              <span class="font-medium">Recipient:</span> 
              {{ form.first_name && form.last_name ? `${form.first_name} ${form.last_name}` : 'John Doe' }}
            </p>
            <p>
              <span class="font-medium">Email:</span> 
              {{ form.email || 'email@example.com' }}
            </p>
            <p>
              <span class="font-medium">Role:</span> 
              {{ getRoleDisplayName(form.role) }}
            </p>
            <p v-if="form.organization_name">
              <span class="font-medium">Organization:</span> 
              {{ form.organization_name }}
            </p>
            <p>
              <span class="font-medium">Expires:</span> 
              In 7 days
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-4">
          <BaseButton
            type="submit"
            variant="primary"
            size="lg"
            block
            :disabled="submitting || !isFormValid"
            :loading="submitting"
            :loading-text="'Sending...'"
            :leading-icon="submitting ? undefined : PaperAirplaneIcon"
          >
            {{ submitting ? 'Sending...' : (isBulkMode ? 'Send Invitations' : 'Send Invitation') }}
          </BaseButton>
          
          <BaseButton
            variant="secondary"
            size="lg"
            @click="router.push({ name: 'invitations' })"
          >
            Cancel
          </BaseButton>
        </div>
      </form>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useInvitationFormStore } from '../../stores/invitationFormStore'
import { useInvitationListStore } from '../../stores/invitationListStore'
import { useAuthStore } from '@/stores/auth'
import {
  ArrowLeftIcon,
  EnvelopeIcon,
  EnvelopeOpenIcon,
  PaperAirplaneIcon,
  DocumentArrowUpIcon
} from '@heroicons/vue/24/outline'
import { BaseCard, BaseInput, BaseButton } from '@/shared/components'
import { ROLE_DISPLAY_NAMES, ROLE_DESCRIPTIONS } from '../../types/invitation.types'

const router = useRouter()
const invitationFormStore = useInvitationFormStore()
const invitationListStore = useInvitationListStore()
const authStore = useAuthStore()

// Use form store state
const {
  singleForm: form,
  errors,
  loading,
  submitting,
  isBulkMode,
  isFormValid,
  hasErrors,
  availableRoles,
  canSendInvitations
} = invitationFormStore

// Methods
const getRoleDisplayName = (role: string) => {
  return ROLE_DISPLAY_NAMES[role as keyof typeof ROLE_DISPLAY_NAMES] || role
}

const getRoleDescription = (role: string) => {
  return ROLE_DESCRIPTIONS[role as keyof typeof ROLE_DESCRIPTIONS] || ''
}

// Use form store validation
const { validateEmail, toggleMode, submitSingleInvitation } = invitationFormStore

const handleSubmit = async () => {
  try {
    if (!isBulkMode) {
      // Send single invitation using form store
      await submitSingleInvitation()
      
      // Refresh the invitation list
      await invitationListStore.refreshInvitations()
      
      // Navigate back to list
      router.push({ name: 'invitations' })
    } else {
      // Bulk mode - not implemented yet
      // This would use invitationFormStore.submitBulkInvitations()
      console.info('Bulk invitation feature coming soon!')
    }
  } catch (error: any) {
    console.error('Failed to send invitation(s):', error)
    // Error handling is done in the form store
  }
}

// Spinner component (simple inline component)
const SpinnerIcon = {
  template: `
    <svg class="animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  `
}
</script>
<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">
        Settings
      </h1>
      <p class="text-secondary-600 dark:text-secondary-400 mt-1">
        Manage your account settings and preferences
      </p>
    </div>

    <!-- Loading state -->
    <div v-if="loading && !settings" class="space-y-6">
      <BaseCard class="p-6">
        <div class="animate-pulse space-y-4">
          <div class="h-6 bg-secondary-200 dark:bg-secondary-700 rounded w-1/4"></div>
          <div class="space-y-3">
            <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded"></div>
            <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-3/4"></div>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Settings sections -->
    <div v-else class="space-y-6">
      <!-- Notifications -->
      <BaseCard class="p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100">
              Notifications
            </h2>
            <p class="text-sm text-secondary-600 dark:text-secondary-400 mt-1">
              Choose what notifications you want to receive
            </p>
          </div>
          <BellIcon class="w-6 h-6 text-secondary-400" />
        </div>

        <div class="space-y-4">
          <!-- Email notifications -->
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Email Notifications
              </h3>
              <p class="text-sm text-secondary-600 dark:text-secondary-400">
                Receive notifications via email for important updates
              </p>
            </div>
            <BaseCheckbox
              v-model="settingsForm.formData.email_notifications"
              @update:modelValue="handleNotificationChange"
              :disabled="settingsForm.saving.value"
            />
          </div>

          <!-- Push notifications -->
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Push Notifications
              </h3>
              <p class="text-sm text-secondary-600 dark:text-secondary-400">
                Receive push notifications in your browser
              </p>
            </div>
            <BaseCheckbox
              v-model="settingsForm.formData.push_notifications"
              @update:modelValue="handleNotificationChange"
              :disabled="settingsForm.saving.value"
            />
          </div>
        </div>
      </BaseCard>

      <!-- Privacy -->
      <BaseCard class="p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100">
              Privacy
            </h2>
            <p class="text-sm text-secondary-600 dark:text-secondary-400 mt-1">
              Control who can see your information and activity
            </p>
          </div>
          <ShieldCheckIcon class="w-6 h-6 text-secondary-400" />
        </div>

        <div class="space-y-6">
          <!-- Profile visibility -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-3">
              Profile Visibility
            </label>
            <div class="space-y-3">
              <div
                v-for="visibility in visibilityOptions"
                :key="visibility.value"
                :class="visibilityOptionClasses(visibility.value)"
                @click="updateProfileVisibility(visibility.value)"
              >
                <div class="flex items-start">
                  <input
                    type="radio"
                    :value="visibility.value"
                    v-model="settingsForm.formData.profile_visibility"
                    :disabled="settingsForm.saving.value"
                    class="mt-1 w-4 h-4 text-primary-600 border-secondary-300 focus:ring-primary-500"
                  />
                  <div class="ml-3">
                    <h4 class="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                      {{ visibility.label }}
                    </h4>
                    <p class="text-sm text-secondary-600 dark:text-secondary-400">
                      {{ visibility.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Show email -->
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Show Email Address
              </h3>
              <p class="text-sm text-secondary-600 dark:text-secondary-400">
                Allow others to see your email address on your profile
              </p>
            </div>
            <BaseCheckbox
              v-model="settingsForm.formData.show_email"
              @update:modelValue="handlePrivacyChange"
              :disabled="settingsForm.saving.value"
            />
          </div>

          <!-- Show activity -->
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Show Activity
              </h3>
              <p class="text-sm text-secondary-600 dark:text-secondary-400">
                Allow others to see your recent activity and contributions
              </p>
            </div>
            <BaseCheckbox
              v-model="settingsForm.formData.show_activity"
              @update:modelValue="handlePrivacyChange"
              :disabled="settingsForm.saving.value"
            />
          </div>
        </div>
      </BaseCard>

      <!-- Account Actions -->
      <BaseCard class="p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100">
              Account
            </h2>
            <p class="text-sm text-secondary-600 dark:text-secondary-400 mt-1">
              Manage your account and data
            </p>
          </div>
          <UserIcon class="w-6 h-6 text-secondary-400" />
        </div>

        <div class="space-y-4">
          <!-- Export data -->
          <div class="flex items-center justify-between p-4 border border-secondary-200 dark:border-secondary-700 rounded-lg">
            <div>
              <h3 class="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Export Your Data
              </h3>
              <p class="text-sm text-secondary-600 dark:text-secondary-400">
                Download a copy of all your data
              </p>
            </div>
            <BaseButton
              variant="outline"
              size="sm"
              @click="exportData"
              :leading-icon="ArrowDownTrayIcon"
            >
              Export
            </BaseButton>
          </div>

          <!-- Delete account -->
          <div class="flex items-center justify-between p-4 border border-danger-200 dark:border-danger-800 rounded-lg bg-danger-50 dark:bg-danger-900/20">
            <div>
              <h3 class="text-sm font-medium text-danger-900 dark:text-danger-100">
                Delete Account
              </h3>
              <p class="text-sm text-danger-600 dark:text-danger-400">
                Permanently delete your account and all associated data
              </p>
            </div>
            <BaseButton
              variant="danger"
              size="sm"
              @click="confirmDeleteAccount"
              :leading-icon="TrashIcon"
            >
              Delete
            </BaseButton>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Error message -->
    <ErrorMessage
      v-if="error && !loading"
      :message="error"
      @retry="loadSettings"
    />

    <!-- Delete confirmation dialog -->
    <ConfirmDialog
      v-if="showDeleteConfirm"
      title="Delete Account"
      message="Are you sure you want to delete your account? This action cannot be undone and will permanently remove all your data."
      confirm-text="Delete Account"
      confirm-variant="danger"
      @confirm="deleteAccount"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import {
  BellIcon,
  ShieldCheckIcon,
  UserIcon,
  ArrowDownTrayIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import BaseCheckbox from '@/shared/components/BaseCheckbox.vue'
import LoadingSpinner from '@/shared/components/LoadingSpinner.vue'
import ErrorMessage from '@/shared/components/ErrorMessage.vue'
import ConfirmDialog from '@/shared/components/ConfirmDialog.vue'
import { useDebouncedApiCall, DEBOUNCE_DELAYS } from '@/composables/useDebounce'
import { useSettingsStore } from '../stores/settingsStore'
import { useSettingsForm } from '../composables/useProfileForm'
import type { SettingsForm, ProfileVisibility } from '../types/profile.types'

const settingsStore = useSettingsStore()

// Enhanced form composable
const settingsForm = useSettingsForm()

// Debounced API calls for settings updates
const debouncedNotificationUpdate = useDebouncedApiCall(
  (data: { email: boolean; push: boolean }) => settingsStore.updateNotificationSettings(data),
  DEBOUNCE_DELAYS.SETTINGS
)

const debouncedPrivacyUpdate = useDebouncedApiCall(
  (data: { profileVisibility: ProfileVisibility }) => settingsStore.updatePrivacySettings(data),
  DEBOUNCE_DELAYS.SETTINGS
)

// Refs
const showDeleteConfirm = ref(false)

// Computed
const loading = computed(() => settingsStore.loading)
const error = computed(() => settingsStore.error)
const settings = computed(() => settingsStore.userSettings)

// Visibility options
const visibilityOptions = [
  {
    value: 'public',
    label: 'Public',
    description: 'Anyone can see your profile'
  },
  {
    value: 'private', 
    label: 'Private',
    description: 'Only you can see your profile'
  },
  {
    value: 'friends',
    label: 'Friends Only', 
    description: 'Only your connections can see your profile'
  }
]

const selectClasses = computed(() => [
  'block w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600',
  'rounded-md shadow-sm bg-white dark:bg-secondary-800',
  'text-secondary-900 dark:text-secondary-100',
  'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
  'disabled:opacity-50 disabled:cursor-not-allowed'
])

// Methods
const loadSettings = async () => {
  await settingsStore.fetchUserSettings()
  initializeForm()
}

const initializeForm = () => {
  if (settings.value) {
    settingsForm.initializeForm(settings.value)
  }
}

const visibilityOptionClasses = (visibility: ProfileVisibility) => [
  'flex items-start p-4 rounded-lg border cursor-pointer transition-all',
  'hover:bg-secondary-50 dark:hover:bg-secondary-800',
  {
    'border-primary-500 bg-primary-50 dark:bg-primary-900/20': settingsForm.formData.profile_visibility === visibility,
    'border-secondary-200 dark:border-secondary-700': settingsForm.formData.profile_visibility !== visibility
  }
]

const handleNotificationChange = async () => {
  await settingsForm.handleBatchUpdate(
    {
      email_notifications: settingsForm.formData.email_notifications,
      push_notifications: settingsForm.formData.push_notifications
    },
    (data) => settingsStore.updateNotificationSettings({
      email: data.email_notifications!,
      push: data.push_notifications!
    }),
    { successMessage: 'Notification settings updated successfully!' }
  )
}

const updateProfileVisibility = async (visibility: ProfileVisibility) => {
  await settingsForm.handleFieldUpdate(
    'profile_visibility',
    visibility,
    (data) => settingsStore.updatePrivacySettings({ profileVisibility: data.profile_visibility! }),
    { successMessage: 'Privacy settings updated successfully!' }
  )
}

const handlePrivacyChange = async () => {
  await settingsForm.handleBatchUpdate(
    {
      show_email: settingsForm.formData.show_email,
      show_activity: settingsForm.formData.show_activity
    },
    (data) => settingsStore.updatePrivacySettings({
      showEmail: data.show_email!,
      showActivity: data.show_activity!
    }),
    { successMessage: 'Privacy settings updated successfully!' }
  )
}

const exportData = () => {
  console.log('Data export feature coming soon')
}

const confirmDeleteAccount = () => {
  showDeleteConfirm.value = true
}

const deleteAccount = () => {
  showDeleteConfirm.value = false
  console.log('Account deletion feature coming soon')
}

// Lifecycle
onMounted(() => {
  loadSettings()
})

// Watch settings changes to update form
watch(
  settings,
  (newSettings) => {
    if (newSettings) {
      initializeForm()
    }
  },
  { immediate: true }
)
</script>
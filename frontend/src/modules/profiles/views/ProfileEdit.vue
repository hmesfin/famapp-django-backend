<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">
          Edit Profile
        </h1>
        <p class="text-secondary-600 dark:text-secondary-400 mt-1">
          Update your profile information and settings
        </p>
      </div>
      
      <BaseButton
        variant="ghost"
        :to="{ name: 'profile-view', params: { id: 'me' } }"
        tag="router-link"
        :leading-icon="ArrowLeftIcon"
      >
        Back to Profile
      </BaseButton>
    </div>

    <!-- Loading state -->
    <BaseCard v-if="loading && !profileForm.initialized.value" class="p-6">
      <div class="animate-pulse space-y-6">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 bg-secondary-200 dark:bg-secondary-700 rounded-full"></div>
          <div class="flex-1">
            <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-1/4"></div>
          </div>
        </div>
        <div class="space-y-4">
          <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded"></div>
          <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-3/4"></div>
        </div>
      </div>
    </BaseCard>

    <!-- Profile form -->
    <form v-else @submit.prevent="handleSubmit">
      <!-- Avatar section -->
      <BaseCard class="p-6 mb-6">
        <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 mb-4">
          Profile Picture
        </h2>
        
        <div class="flex items-start space-x-6">
          <ProfileAvatar
            :avatar-url="profileForm.formData.avatar_url"
            :name="currentProfile?.user_full_name"
            :email="currentProfile?.user_email"
            size="xl"
            :editable="true"
            :loading="avatarForm.uploading.value"
            :progress="avatarForm.uploadProgress.value"
            @upload="handleAvatarUpload"
          />
          
          <div class="flex-1">
            <h3 class="text-sm font-medium text-secondary-900 dark:text-secondary-100 mb-2">
              Update your profile picture
            </h3>
            <p class="text-sm text-secondary-600 dark:text-secondary-400 mb-4">
              Click on your avatar to upload a new profile picture. Recommended size is 400x400px.
            </p>
            
            <div class="flex items-center space-x-3">
              <BaseButton
                variant="outline"
                size="sm"
                @click="triggerFileUpload"
                :leading-icon="PhotoIcon"
                :disabled="avatarForm.uploading.value"
              >
                Upload New
              </BaseButton>
              
              <BaseButton
                v-if="profileForm.formData.avatar_url"
                variant="ghost"
                size="sm"
                @click="removeAvatar"
                :leading-icon="TrashIcon"
                :disabled="avatarForm.uploading.value"
              >
                Remove
              </BaseButton>
            </div>
          </div>
        </div>
        
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          class="hidden"
          @change="handleFileSelect"
        />
      </BaseCard>

      <!-- Basic information -->
      <BaseCard class="p-6 mb-6">
        <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 mb-6">
          Basic Information
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Name (read-only) -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Full Name
            </label>
            <BaseInput
              :model-value="currentProfile?.user_full_name"
              disabled
              placeholder="Your full name"
            />
            <p class="mt-1 text-xs text-secondary-500 dark:text-secondary-400">
              Contact support to change your name
            </p>
          </div>

          <!-- Email (read-only) -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Email Address
            </label>
            <BaseInput
              :model-value="currentProfile?.user_email"
              disabled
              placeholder="Your email address"
            />
            <p class="mt-1 text-xs text-secondary-500 dark:text-secondary-400">
              Contact support to change your email
            </p>
          </div>
        </div>

        <div class="mt-6">
          <!-- Bio -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Bio
            </label>
            <textarea
              v-model="profileForm.formData.bio"
              rows="4"
              class="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-md shadow-sm placeholder-secondary-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-secondary-800 text-secondary-900 dark:text-secondary-100"
              placeholder="Tell us about yourself..."
              :class="{ 'border-danger-500 focus:ring-danger-500 focus:border-danger-500': profileForm.errors.bio }"
            />
            <div class="flex justify-between items-center mt-1">
              <p v-if="profileForm.errors.bio" class="text-sm text-danger-600 dark:text-danger-400">
                {{ profileForm.errors.bio }}
              </p>
              <p class="text-xs text-secondary-500 dark:text-secondary-400 ml-auto">
                {{ (profileForm.formData.bio || '').length }}/500 characters
              </p>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Location & Work -->
      <BaseCard class="p-6 mb-6">
        <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 mb-6">
          Location & Work
        </h2>
        
        <div class="space-y-6">
          <!-- Location -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              <MapPinIcon class="inline w-4 h-4 mr-1" />
              Location
            </label>
            <BaseInput
              v-model="profileForm.formData.location"
              placeholder="e.g., San Francisco, CA"
              :error="!!profileForm.errors.location"
              :error-message="profileForm.errors.location"
            />
          </div>

          <!-- Company -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              <BuildingOfficeIcon class="inline w-4 h-4 mr-1" />
              Company
            </label>
            <BaseInput
              v-model="profileForm.formData.company"
              placeholder="e.g., Acme Inc"
              :error="!!profileForm.errors.company"
              :error-message="profileForm.errors.company"
            />
          </div>

          <!-- Website -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              <GlobeAltIcon class="inline w-4 h-4 mr-1" />
              Website
            </label>
            <BaseInput
              v-model="profileForm.formData.website"
              type="url"
              placeholder="e.g., https://example.com"
              :error="!!profileForm.errors.website"
              :error-message="profileForm.errors.website"
            />
            <p class="mt-1 text-xs text-secondary-500 dark:text-secondary-400">
              Include https:// or http://
            </p>
          </div>
        </div>
      </BaseCard>

      <!-- Form actions -->
      <div class="flex items-center justify-between">
        <BaseButton
          variant="ghost"
          :to="{ name: 'profile-view', params: { id: 'me' } }"
          tag="router-link"
          :disabled="profileForm.saving.value"
        >
          Cancel
        </BaseButton>
        
        <div class="flex items-center space-x-3">
          <BaseButton
            variant="outline"
            type="button"
            @click="resetForm"
            :disabled="profileForm.saving.value || !profileForm.hasChanges.value"
          >
            Reset
          </BaseButton>
          
          <BaseButton
            variant="primary"
            type="submit"
            :loading="profileForm.saving.value"
            :disabled="!profileForm.hasChanges.value"
          >
            Save Changes
          </BaseButton>
        </div>
      </div>
    </form>

    <!-- Error display -->
    <ErrorMessage
      v-if="error"
      :message="error"
      @retry="loadProfile"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeftIcon,
  PhotoIcon,
  TrashIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  GlobeAltIcon
} from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import BaseInput from '@/shared/components/BaseInput.vue'
import ErrorMessage from '@/shared/components/ErrorMessage.vue'
import ProfileAvatar from '../components/ProfileAvatar.vue'
import { useProfileStore } from '../stores/profileStore'
import { useProfileForm, useAvatarForm } from '../composables/useProfileForm'

const router = useRouter()
const profileStore = useProfileStore()

// Enhanced form composables
const profileForm = useProfileForm()
const avatarForm = useAvatarForm()

// Refs
const fileInput = ref<HTMLInputElement>()

// Computed
const loading = computed(() => profileStore.loading)
const error = computed(() => profileStore.error)
const currentProfile = computed(() => profileStore.currentUserProfile)

// Methods
const loadProfile = async () => {
  await profileStore.fetchCurrentUserProfile()
  initializeForm()
}

const initializeForm = () => {
  if (currentProfile.value) {
    const profileData = {
      bio: currentProfile.value.bio || '',
      location: currentProfile.value.location || '',
      company: currentProfile.value.company || '',
      website: currentProfile.value.website || '',
      avatar_url: currentProfile.value.avatar_url || ''
    }
    
    profileForm.initializeForm(profileData)
  }
}

const resetForm = () => {
  profileForm.resetForm()
}

const handleSubmit = async () => {
  await profileForm.handleSubmit(profileStore.updateCurrentUserProfile, {
    successMessage: 'Profile updated successfully!',
    onSuccess: () => {
      router.push({ name: 'profile-view', params: { id: 'me' } })
    }
  })
}

const triggerFileUpload = () => {
  avatarForm.triggerFileUpload(fileInput.value!)
}

const handleFileSelect = async (event: Event) => {
  const result = await avatarForm.handleFileInputChange(event, profileStore.uploadAvatar)
  if (result) {
    profileForm.formData.avatar_url = result.avatar_url
  }
}

const handleAvatarUpload = async (file: File) => {
  const result = await avatarForm.handleAvatarUpload(file, profileStore.uploadAvatar)
  if (result) {
    profileForm.formData.avatar_url = result.avatar_url
  }
}

const removeAvatar = () => {
  profileForm.formData.avatar_url = ''
}

// Lifecycle
onMounted(() => {
  loadProfile()
})

// Watch for profile changes to reinitialize form
watch(
  currentProfile,
  (newProfile) => {
    if (newProfile && !profileForm.initialized.value) {
      initializeForm()
    }
  },
  { immediate: true }
)
</script>
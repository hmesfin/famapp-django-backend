<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Loading state -->
    <div v-if="loading && !profile" class="animate-pulse space-y-6">
      <div class="bg-white dark:bg-secondary-800 rounded-lg shadow p-6">
        <div class="flex items-start space-x-6">
          <div class="w-24 h-24 bg-secondary-200 dark:bg-secondary-700 rounded-full"></div>
          <div class="flex-1 space-y-4">
            <div class="h-8 bg-secondary-200 dark:bg-secondary-700 rounded w-1/3"></div>
            <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-1/2"></div>
            <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile header -->
    <BaseCard v-else-if="profile" class="relative">
      <!-- Background pattern (optional) -->
      <div class="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 rounded-lg"></div>
      
      <div class="relative p-6">
        <div class="flex flex-col lg:flex-row lg:items-start lg:space-x-6 space-y-4 lg:space-y-0">
          <!-- Avatar -->
          <div class="flex-shrink-0 self-center lg:self-start">
            <ProfileAvatar
              :avatar-url="profile.avatar_url"
              :name="profile.user_full_name"
              :email="profile.user_email"
              size="2xl"
              :border-color="isCurrentUser ? 'border-primary-300 dark:border-primary-600' : 'border-secondary-200 dark:border-secondary-700'"
            />
          </div>
          
          <!-- Profile info -->
          <div class="flex-1 text-center lg:text-left">
            <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h1 class="text-3xl font-bold text-secondary-900 dark:text-secondary-100">
                  {{ profile.user_full_name || 'Unnamed User' }}
                </h1>
                <p class="text-lg text-secondary-600 dark:text-secondary-400 mt-1">
                  {{ profile.user_email }}
                </p>
                
                <!-- Location and company -->
                <div class="mt-3 space-y-2">
                  <div 
                    v-if="profile.location" 
                    class="flex items-center justify-center lg:justify-start text-secondary-600 dark:text-secondary-400"
                  >
                    <MapPinIcon class="w-5 h-5 mr-2" />
                    <span>{{ profile.location }}</span>
                  </div>
                  <div 
                    v-if="profile.company" 
                    class="flex items-center justify-center lg:justify-start text-secondary-600 dark:text-secondary-400"
                  >
                    <BuildingOfficeIcon class="w-5 h-5 mr-2" />
                    <span>{{ profile.company }}</span>
                  </div>
                  <div 
                    v-if="profile.website" 
                    class="flex items-center justify-center lg:justify-start"
                  >
                    <a
                      :href="formattedWebsite"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="flex items-center text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                    >
                      <GlobeAltIcon class="w-5 h-5 mr-2" />
                      <span>{{ displayWebsite }}</span>
                      <ArrowTopRightOnSquareIcon class="w-4 h-4 ml-1" />
                    </a>
                  </div>
                </div>
              </div>
              
              <!-- Action buttons -->
              <div class="flex items-center space-x-3 mt-4 lg:mt-0 justify-center lg:justify-end">
                <BaseButton
                  v-if="isCurrentUser"
                  variant="primary"
                  :to="{ name: 'profile-edit' }"
                  tag="router-link"
                  :leading-icon="PencilIcon"
                >
                  Edit Profile
                </BaseButton>
                
                <BaseButton
                  v-if="!isCurrentUser"
                  variant="outline"
                  @click="sendMessage"
                  :leading-icon="EnvelopeIcon"
                >
                  Message
                </BaseButton>
                
                <BaseButton
                  v-if="!isCurrentUser"
                  variant="secondary"
                  @click="addFriend"
                  :leading-icon="UserPlusIcon"
                >
                  Add Friend
                </BaseButton>
              </div>
            </div>
            
            <!-- Join date -->
            <div class="mt-4 text-sm text-secondary-500 dark:text-secondary-400">
              <CalendarIcon class="inline w-4 h-4 mr-1" />
              Joined {{ formatDate(profile.created_at) }}
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Bio section -->
    <BaseCard v-if="profile?.bio" class="p-6">
      <h2 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 mb-4">
        About
      </h2>
      <div class="prose prose-secondary dark:prose-invert max-w-none">
        <p class="text-secondary-700 dark:text-secondary-300 leading-relaxed whitespace-pre-wrap">
          {{ profile.bio }}
        </p>
      </div>
    </BaseCard>

    <!-- Activity/Stats section (placeholder for future features) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <BaseCard class="p-6">
        <div class="flex items-center">
          <div class="p-3 bg-primary-100 dark:bg-primary-900 rounded-lg">
            <FolderIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div class="ml-4">
            <p class="text-2xl font-semibold text-secondary-900 dark:text-secondary-100">12</p>
            <p class="text-sm text-secondary-600 dark:text-secondary-400">Projects</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard class="p-6">
        <div class="flex items-center">
          <div class="p-3 bg-success-100 dark:bg-success-900 rounded-lg">
            <CheckCircleIcon class="w-6 h-6 text-success-600 dark:text-success-400" />
          </div>
          <div class="ml-4">
            <p class="text-2xl font-semibold text-secondary-900 dark:text-secondary-100">47</p>
            <p class="text-sm text-secondary-600 dark:text-secondary-400">Tasks Completed</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard class="p-6">
        <div class="flex items-center">
          <div class="p-3 bg-info-100 dark:bg-info-900 rounded-lg">
            <ClockIcon class="w-6 h-6 text-info-600 dark:text-info-400" />
          </div>
          <div class="ml-4">
            <p class="text-2xl font-semibold text-secondary-900 dark:text-secondary-100">156h</p>
            <p class="text-sm text-secondary-600 dark:text-secondary-400">Hours Logged</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Error state -->
    <ErrorMessage
      v-if="error && !loading"
      :message="error"
      @retry="loadProfile"
    />
    
    <!-- 404 state for profile not found -->
    <BaseCard v-if="!loading && !profile && !error" class="p-12 text-center">
      <UserIcon class="mx-auto w-16 h-16 text-secondary-400 dark:text-secondary-600 mb-4" />
      <h2 class="text-xl font-semibold text-secondary-900 dark:text-secondary-100 mb-2">
        Profile Not Found
      </h2>
      <p class="text-secondary-600 dark:text-secondary-400 mb-6">
        The profile you're looking for doesn't exist or has been made private.
      </p>
      <BaseButton
        variant="primary"
        :to="{ name: 'dashboard' }"
        tag="router-link"
      >
        Back to Dashboard
      </BaseButton>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  MapPinIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  ArrowTopRightOnSquareIcon,
  PencilIcon,
  EnvelopeIcon,
  UserPlusIcon,
  CalendarIcon,
  FolderIcon,
  CheckCircleIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import ErrorMessage from '@/shared/components/ErrorMessage.vue'
import ProfileAvatar from '../components/ProfileAvatar.vue'
import { useProfileStore } from '../stores/profileStore'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const profileStore = useProfileStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

// Computed
const loading = computed(() => profileStore.loading)
const error = computed(() => profileStore.error)
const profile = computed(() => {
  // If looking at 'me', show current user profile
  if (route.params.id === 'me') {
    return profileStore.currentUserProfile
  }
  return profileStore.currentProfile
})

const isCurrentUser = computed(() => {
  if (!profile.value || !authStore.user) return false
  if (route.params.id === 'me') return true
  return profile.value.user_email === authStore.user.email
})

const formattedWebsite = computed(() => {
  if (!profile.value?.website) return ''
  if (profile.value.website.startsWith('http://') || profile.value.website.startsWith('https://')) {
    return profile.value.website
  }
  return `https://${profile.value.website}`
})

const displayWebsite = computed(() => {
  if (!profile.value?.website) return ''
  return profile.value.website.replace(/^https?:\/\//, '')
})

// Methods
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadProfile = async () => {
  const profileId = route.params.id as string
  
  if (profileId === 'me') {
    // Load current user profile
    await profileStore.fetchCurrentUserProfile()
  } else {
    // Load specific user profile
    await profileStore.fetchProfile(profileId)
  }
}

const sendMessage = () => {
  toastStore.info('Messaging feature coming soon!')
}

const addFriend = () => {
  toastStore.info('Friend requests coming soon!')
}

// Lifecycle
onMounted(() => {
  loadProfile()
})

// Watch route changes to load different profiles
watch(
  () => route.params.id,
  () => {
    profileStore.clearCurrentProfile()
    loadProfile()
  }
)
</script>
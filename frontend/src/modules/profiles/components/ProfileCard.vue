<template>
  <BaseCard
    :class="cardClasses"
    @click="handleCardClick"
  >
    <!-- Header with avatar and basic info -->
    <div class="flex items-start space-x-4">
      <!-- Avatar -->
      <ProfileAvatar
        :avatar-url="profile.avatar_url"
        :name="profile.user_full_name"
        :email="profile.user_email"
        :size="avatarSize"
        :show-online-status="showOnlineStatus"
        :is-online="isOnline"
        @click.stop="$emit('avatar-click', profile)"
      />
      
      <!-- Profile info -->
      <div class="flex-1 min-w-0">
        <!-- Name and email -->
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <h3 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 truncate">
              {{ profile.user_full_name || 'Unnamed User' }}
            </h3>
            <p 
              v-if="showEmail" 
              class="text-sm text-secondary-600 dark:text-secondary-400 truncate"
            >
              {{ profile.user_email }}
            </p>
          </div>
          
          <!-- Actions dropdown -->
          <div v-if="showActions" class="flex-shrink-0 ml-2">
            <BaseButton
              variant="ghost"
              size="sm"
              :leading-icon="EllipsisVerticalIcon"
              @click.stop="toggleActionsMenu"
              aria-label="Profile actions"
            />
            
            <!-- Actions menu -->
            <div
              v-if="showActionsMenu"
              class="absolute right-0 mt-2 w-48 bg-white dark:bg-secondary-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10"
            >
              <div class="py-1">
                <button
                  v-for="action in actions"
                  :key="action.key"
                  :class="actionItemClasses(action)"
                  @click.stop="handleActionClick(action)"
                >
                  <component
                    :is="action.icon"
                    v-if="action.icon"
                    class="w-4 h-4 mr-3"
                  />
                  {{ action.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Location and company -->
        <div v-if="profile.location || profile.company" class="mt-1 space-y-1">
          <div 
            v-if="profile.location" 
            class="flex items-center text-sm text-secondary-600 dark:text-secondary-400"
          >
            <MapPinIcon class="w-4 h-4 mr-1.5 flex-shrink-0" />
            <span class="truncate">{{ profile.location }}</span>
          </div>
          <div 
            v-if="profile.company" 
            class="flex items-center text-sm text-secondary-600 dark:text-secondary-400"
          >
            <BuildingOfficeIcon class="w-4 h-4 mr-1.5 flex-shrink-0" />
            <span class="truncate">{{ profile.company }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bio -->
    <div v-if="profile.bio && showBio" class="mt-4">
      <p class="text-sm text-secondary-700 dark:text-secondary-300">
        {{ truncatedBio }}
      </p>
      <button
        v-if="profile.bio.length > bioCharacterLimit && !expanded"
        class="mt-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
        @click.stop="expanded = true"
      >
        Read more
      </button>
    </div>
    
    <!-- Website link -->
    <div v-if="profile.website && showWebsite" class="mt-3">
      <a
        :href="formattedWebsite"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
        @click.stop
      >
        <GlobeAltIcon class="w-4 h-4 mr-1.5" />
        <span class="truncate">{{ displayWebsite }}</span>
        <ArrowTopRightOnSquareIcon class="w-3 h-3 ml-1 flex-shrink-0" />
      </a>
    </div>
    
    <!-- Footer with join date and stats -->
    <div v-if="showFooter" class="mt-4 pt-4 border-t border-secondary-200 dark:border-secondary-700">
      <div class="flex items-center justify-between text-xs text-secondary-500 dark:text-secondary-400">
        <span>Joined {{ formatDate(profile.created_at) }}</span>
        <div v-if="stats" class="flex items-center space-x-4">
          <span v-if="stats.projects">{{ stats.projects }} projects</span>
          <span v-if="stats.tasks">{{ stats.tasks }} tasks</span>
        </div>
      </div>
    </div>
    
    <!-- Skeleton loading state -->
    <template v-if="loading">
      <div class="animate-pulse">
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 bg-secondary-200 dark:bg-secondary-700 rounded-full"></div>
          <div class="flex-1">
            <div class="h-4 bg-secondary-200 dark:bg-secondary-700 rounded mb-2"></div>
            <div class="h-3 bg-secondary-200 dark:bg-secondary-700 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    </template>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  EllipsisVerticalIcon, 
  MapPinIcon, 
  BuildingOfficeIcon,
  GlobeAltIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import ProfileAvatar from './ProfileAvatar.vue'
import type { Profile, AvatarSize } from '../types/profile.types'
import type { Component } from 'vue'

interface ProfileStats {
  projects?: number
  tasks?: number
  [key: string]: any
}

interface ProfileAction {
  key: string
  label: string
  icon?: Component
  variant?: 'default' | 'danger'
  onClick: (profile: Profile) => void
}

interface Props {
  profile: Profile
  
  // Display options
  showEmail?: boolean
  showBio?: boolean
  showWebsite?: boolean
  showFooter?: boolean
  showActions?: boolean
  showOnlineStatus?: boolean
  
  // Styling
  avatarSize?: AvatarSize
  clickable?: boolean
  
  // Behavior
  bioCharacterLimit?: number
  isOnline?: boolean
  loading?: boolean
  
  // Data
  stats?: ProfileStats
  actions?: ProfileAction[]
}

const props = withDefaults(defineProps<Props>(), {
  showEmail: true,
  showBio: true,
  showWebsite: true,
  showFooter: true,
  showActions: false,
  showOnlineStatus: false,
  avatarSize: 'lg',
  clickable: false,
  bioCharacterLimit: 150,
  isOnline: false,
  loading: false
})

const emit = defineEmits<{
  click: [profile: Profile]
  'avatar-click': [profile: Profile]
  'action-click': [action: ProfileAction, profile: Profile]
}>()

// Refs
const expanded = ref(false)
const showActionsMenu = ref(false)

// Computed
const cardClasses = computed(() => [
  'relative',
  {
    'cursor-pointer hover:shadow-lg transition-shadow duration-200': props.clickable,
    'opacity-50': props.loading
  }
])

const truncatedBio = computed(() => {
  if (!props.profile.bio) return ''
  if (expanded.value || props.profile.bio.length <= props.bioCharacterLimit) {
    return props.profile.bio
  }
  return props.profile.bio.substring(0, props.bioCharacterLimit) + '...'
})

const formattedWebsite = computed(() => {
  if (!props.profile.website) return ''
  if (props.profile.website.startsWith('http://') || props.profile.website.startsWith('https://')) {
    return props.profile.website
  }
  return `https://${props.profile.website}`
})

const displayWebsite = computed(() => {
  if (!props.profile.website) return ''
  return props.profile.website.replace(/^https?:\/\//, '')
})

const actionItemClasses = (action: ProfileAction) => [
  'flex items-center w-full px-4 py-2 text-sm text-left',
  'hover:bg-secondary-50 dark:hover:bg-secondary-700',
  'focus:outline-none focus:bg-secondary-50 dark:focus:bg-secondary-700',
  {
    'text-secondary-700 dark:text-secondary-300': action.variant !== 'danger',
    'text-danger-600 dark:text-danger-400': action.variant === 'danger'
  }
]

// Methods
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long'
  })
}

const handleCardClick = () => {
  if (props.clickable && !props.loading) {
    emit('click', props.profile)
  }
}

const toggleActionsMenu = () => {
  showActionsMenu.value = !showActionsMenu.value
}

const handleActionClick = (action: ProfileAction) => {
  showActionsMenu.value = false
  emit('action-click', action, props.profile)
  action.onClick(props.profile)
}

// Close actions menu when clicking outside
const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.relative')) {
    showActionsMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
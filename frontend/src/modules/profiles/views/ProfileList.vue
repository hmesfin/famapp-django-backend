<template>
  <div class="profile-list-container">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl font-bold text-secondary-900 dark:text-secondary-100">
          Browse Profiles
        </h1>
        <p class="mt-2 text-secondary-600 dark:text-secondary-400">
          Discover and connect with team members
        </p>
      </div>
      
      <!-- Stats -->
      <div class="flex items-center space-x-6 text-sm">
        <div class="text-center">
          <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {{ profileCount }}
          </div>
          <div class="text-secondary-600 dark:text-secondary-400">
            {{ profileCount === 1 ? 'Profile' : 'Profiles' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <BaseCard class="mb-8">
      <div class="space-y-6">
        <!-- Search Bar -->
        <div class="relative">
          <BaseInput
            v-model="searchQuery"
            placeholder="Search profiles by name or email..."
            leading-icon="MagnifyingGlassIcon"
            clearable
            size="lg"
            @clear="onClearSearch"
          />
        </div>

        <!-- Filter Row -->
        <div class="flex flex-col sm:flex-row gap-4">
          <!-- Location Filter -->
          <div class="flex-1">
            <BaseInput
              v-model="locationFilter"
              placeholder="Filter by location"
              leading-icon="MapPinIcon"
              clearable
              label="Location"
            />
          </div>

          <!-- Company Filter -->
          <div class="flex-1">
            <BaseInput
              v-model="companyFilter"
              placeholder="Filter by company"
              leading-icon="BuildingOfficeIcon"
              clearable
              label="Company"
            />
          </div>

          <!-- Clear Filters Button -->
          <div class="flex-shrink-0 flex items-end">
            <BaseButton
              v-if="hasFilters"
              variant="outline"
              size="md"
              leading-icon="XMarkIcon"
              @click="clearAllFilters"
            >
              Clear Filters
            </BaseButton>
          </div>
        </div>

        <!-- Active Filters Tags -->
        <div v-if="hasFilters" class="flex flex-wrap gap-2">
          <BaseBadge
            v-if="searchQuery"
            variant="primary"
            class="flex items-center gap-1"
          >
            <MagnifyingGlassIcon class="w-3 h-3" />
            Search: "{{ searchQuery }}"
            <button @click="searchQuery = ''" class="ml-1">
              <XMarkIcon class="w-3 h-3 hover:text-primary-300" />
            </button>
          </BaseBadge>
          
          <BaseBadge
            v-if="locationFilter"
            variant="secondary"
            class="flex items-center gap-1"
          >
            <MapPinIcon class="w-3 h-3" />
            {{ locationFilter }}
            <button @click="locationFilter = ''" class="ml-1">
              <XMarkIcon class="w-3 h-3 hover:text-secondary-300" />
            </button>
          </BaseBadge>
          
          <BaseBadge
            v-if="companyFilter"
            variant="secondary"
            class="flex items-center gap-1"
          >
            <BuildingOfficeIcon class="w-3 h-3" />
            {{ companyFilter }}
            <button @click="companyFilter = ''" class="ml-1">
              <XMarkIcon class="w-3 h-3 hover:text-secondary-300" />
            </button>
          </BaseBadge>
        </div>
      </div>
    </BaseCard>

    <!-- Loading State -->
    <div v-if="loading && profiles.length === 0" class="space-y-6">
      <BaseCard v-for="n in 6" :key="n">
        <SkeletonLoader 
          variant="profile"
          :show-avatar="true"
          avatar-size="xl"
          :lines="3"
        />
      </BaseCard>
    </div>

    <!-- Empty State -->
    <div 
      v-else-if="!loading && profiles.length === 0" 
      class="text-center py-16"
    >
      <UserGroupIcon class="mx-auto h-16 w-16 text-secondary-400 dark:text-secondary-600 mb-4" />
      <h3 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 mb-2">
        {{ hasFilters ? 'No profiles found' : 'No profiles yet' }}
      </h3>
      <p class="text-secondary-600 dark:text-secondary-400 mb-6">
        {{ hasFilters 
          ? 'Try adjusting your search criteria or clearing filters' 
          : 'Profiles will appear here as team members join'
        }}
      </p>
      <BaseButton
        v-if="hasFilters"
        variant="outline"
        @click="clearAllFilters"
      >
        Clear All Filters
      </BaseButton>
    </div>

    <!-- Profiles Grid -->
    <div 
      v-else
      class="grid grid-cols-1 lg:grid-cols-2 gap-6"
    >
      <ProfileCard
        v-for="profile in profiles"
        :key="profile.public_id"
        :profile="profile"
        :clickable="true"
        :show-actions="false"
        :show-footer="true"
        @click="onProfileClick"
      />
    </div>

    <!-- Load More / Pagination (if needed) -->
    <div 
      v-if="profiles.length > 0 && !loading" 
      class="mt-12 text-center"
    >
      <p class="text-sm text-secondary-600 dark:text-secondary-400">
        Showing {{ profiles.length }} of {{ profileCount }} profiles
      </p>
      
      <!-- Add pagination component here if backend supports it -->
      <!-- <Pagination 
        :current-page="currentPage"
        :total-pages="totalPages"
        @page-change="onPageChange"
      /> -->
    </div>

    <!-- Error State -->
    <ErrorMessage 
      v-if="error" 
      :message="error"
      :show-retry="true"
      @retry="retryFetch"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  XMarkIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseInput from '@/shared/components/BaseInput.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import BaseBadge from '@/shared/components/BaseBadge.vue'
import SkeletonLoader from '@/shared/components/SkeletonLoader.vue'
import ErrorMessage from '@/shared/components/ErrorMessage.vue'
import ProfileCard from '../components/ProfileCard.vue'
import { useProfile } from '../composables/useProfile'
import type { Profile } from '../types/profile.types'

const router = useRouter()

// Use the profile composable for all data management
const {
  profiles,
  loading,
  error,
  profileCount,
  searchQuery,
  locationFilter,
  companyFilter,
  hasFilters,
  fetchProfiles,
  clearFilters
} = useProfile()

// Methods
const onProfileClick = (profile: Profile) => {
  router.push(`/profiles/${profile.public_id}`)
}

const onClearSearch = () => {
  searchQuery.value = ''
}

const clearAllFilters = () => {
  clearFilters()
}

const retryFetch = async () => {
  await fetchProfiles()
}

// Load profiles on mount
onMounted(async () => {
  await fetchProfiles()
})

// Watch for filter changes is handled in the composable
// The composable automatically fetches when filters change
</script>

<style scoped>
.profile-list-container {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8;
}
</style>
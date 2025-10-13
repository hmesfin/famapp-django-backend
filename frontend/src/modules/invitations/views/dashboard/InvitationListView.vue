<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Invitations
          </h1>
          <p class="text-gray-600 dark:text-gray-400 mt-2">
            Manage system invitations and user onboarding
          </p>
        </div>
        
        <button
          @click="router.push({ name: 'invitation-send' })"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 shadow-sm"
        >
          <PlusIcon class="h-5 w-5" />
          Send Invitation
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="invitationStatsStore.stats" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Total</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ invitationStatsStore.totalInvitations }}
            </p>
          </div>
          <EnvelopeIcon class="h-8 w-8 text-gray-400" />
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Pending</p>
            <p class="text-2xl font-bold text-yellow-600">
              {{ invitationStatsStore.pendingInvitations }}
            </p>
          </div>
          <ClockIcon class="h-8 w-8 text-yellow-400" />
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Accepted</p>
            <p class="text-2xl font-bold text-green-600">
              {{ invitationStatsStore.acceptedInvitations }}
            </p>
          </div>
          <CheckCircleIcon class="h-8 w-8 text-green-400" />
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Acceptance Rate</p>
            <p class="text-2xl font-bold text-blue-600">
              {{ invitationStatsStore.acceptanceRate }}%
            </p>
          </div>
          <ChartBarIcon class="h-8 w-8 text-blue-400" />
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <select
          v-model="filters.status"
          @change="applyFilters"
          class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="expired">Expired</option>
          <option value="cancelled">Cancelled</option>
        </select>

        <select
          v-model="filters.role"
          @change="applyFilters"
          class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        >
          <option value="">All Roles</option>
          <option value="admin">Administrator</option>
          <option value="manager">Manager</option>
          <option value="member">Member</option>
          <option value="viewer">Viewer</option>
          <option value="guest">Guest</option>
        </select>

        <input
          v-model="filters.search"
          @input="debounceSearch"
          type="text"
          placeholder="Search by email..."
          class="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500"
        >

        <button
          @click="resetFilters"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
        >
          <XMarkIcon v-if="hasActiveFilters" class="h-4 w-4" />
          Clear Filters
          <span v-if="hasActiveFilters" class="ml-1 px-2 py-0.5 bg-indigo-600 text-white text-xs rounded-full">
            {{ activeFilterCount }}
          </span>
        </button>
      </div>
    </div>

    <!-- Invitations List -->
    <div v-if="invitationListStore.loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 4" :key="i" class="animate-pulse">
        <div class="bg-gray-200 dark:bg-gray-700 rounded-lg h-48"></div>
      </div>
    </div>

    <div v-else-if="invitationListStore.invitations.length === 0" class="text-center py-12">
      <EnvelopeIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No invitations</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ hasActiveFilters ? 'No invitations match your filters.' : 'Get started by sending your first invitation.' }}
      </p>
      <div class="mt-6">
        <button
          @click="router.push({ name: 'invitation-send' })"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
          Send Invitation
        </button>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <InvitationCard
        v-for="invitation in invitationListStore.invitations"
        :key="invitation.public_id"
        :invitation="invitation"
        :can-resend="invitationListStore.canPerformAction(invitation, 'resend')"
        :can-extend="invitationListStore.canPerformAction(invitation, 'extend')"
        :can-cancel="invitationListStore.canPerformAction(invitation, 'cancel')"
        :can-delete="invitationListStore.canPerformAction(invitation, 'delete')"
        :loading="invitationListStore.actionLoading"
        @resend="handleResend"
        @extend="handleExtend"
        @cancel="handleCancel"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useInvitationListStore } from '../../stores/invitationListStore'
import { useInvitationStatsStore } from '../../stores/invitationStatsStore'
import InvitationCard from '../../components/InvitationCard.vue'
import {
  PlusIcon,
  EnvelopeIcon,
  ClockIcon,
  CheckCircleIcon,
  ChartBarIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import type { Invitation, InvitationFilters } from '../../types/invitation.types'

const router = useRouter()
const invitationListStore = useInvitationListStore()
const invitationStatsStore = useInvitationStatsStore()

// Local filter state (synchronized with store)
const filters = ref<InvitationFilters>({
  status: undefined,
  role: undefined,
  search: ''
})
let searchTimeout: ReturnType<typeof setTimeout>

// Computed properties for filter state
const hasActiveFilters = computed(() => {
  return invitationListStore.hasActiveFilters()
})

const activeFilterCount = computed(() => {
  return invitationListStore.getActiveFilterCount()
})

// Filter actions
const applyFilters = () => {
  invitationListStore.applyFilters(filters.value)
}

const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300)
}

const resetFilters = () => {
  filters.value = {
    status: undefined,
    role: undefined,
    search: ''
  }
  invitationListStore.resetFilters()
}

// Actions
const handleResend = async (id: string) => {
  try {
    await invitationListStore.resendInvitation(id)
  } catch (error) {
    console.error('Failed to resend invitation:', error)
  }
}

const handleExtend = async (id: string) => {
  try {
    await invitationListStore.extendInvitationExpiry(id)
  } catch (error) {
    console.error('Failed to extend invitation:', error)
  }
}

const handleCancel = async (id: string) => {
  if (confirm('Are you sure you want to cancel this invitation?')) {
    try {
      await invitationListStore.cancelInvitation(id)
    } catch (error) {
      console.error('Failed to cancel invitation:', error)
    }
  }
}

const handleDelete = async (id: string) => {
  if (confirm('Are you sure you want to permanently delete this invitation? This action cannot be undone.')) {
    try {
      await invitationListStore.deleteInvitation(id)
    } catch (error) {
      console.error('Failed to delete invitation:', error)
    }
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    invitationListStore.fetchInvitations(),
    invitationStatsStore.fetchStats()
  ])
})
</script>

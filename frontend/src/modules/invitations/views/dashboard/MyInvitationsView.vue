<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">My Invitations</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">
        View and manage invitations you've sent
      </p>
    </div>

    <!-- Stats Summary -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Sent</div>
        <div class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {{ stats.total }}
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">Pending</div>
        <div class="mt-2 text-3xl font-bold text-yellow-600 dark:text-yellow-400">
          {{ stats.pending }}
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">Accepted</div>
        <div class="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
          {{ stats.accepted }}
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">Expired</div>
        <div class="mt-2 text-3xl font-bold text-gray-500 dark:text-gray-400">
          {{ stats.expired }}
        </div>
      </div>
    </div>

    <!-- Invitations List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-medium text-gray-900 dark:text-white">Sent Invitations</h2>
      </div>
      
      <div v-if="loading" class="p-8 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="ml-2 text-gray-600 dark:text-gray-400">Loading invitations...</span>
        </div>
      </div>

      <div v-else-if="invitations.length === 0" class="p-8 text-center">
        <p class="text-gray-500 dark:text-gray-400">You haven't sent any invitations yet.</p>
        <router-link
          to="/invitations/send"
          class="mt-4 inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Send Your First Invitation
        </router-link>
      </div>

      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div v-for="invitation in invitations" :key="invitation.public_id" class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ invitation.get_full_name || invitation.email }}
                </h3>
                <StatusBadge :status="invitation.status" />
              </div>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ invitation.email }} " {{ invitation.role_display }}
              </p>
              <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
                Sent {{ formatDate(invitation.created_at) }}
                <span v-if="invitation.expires_at" class="ml-2">
                  " Expires {{ formatDate(invitation.expires_at) }}
                </span>
              </p>
            </div>
            
            <div class="ml-4 flex items-center space-x-2">
              <button
                v-if="invitation.status === 'pending'"
                @click="resendInvitation(invitation.public_id)"
                class="px-3 py-1 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              >
                Resend
              </button>
              <button
                v-if="invitation.status === 'pending'"
                @click="cancelInvitation(invitation.public_id)"
                class="px-3 py-1 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useInvitationListStore } from '../../stores/invitationListStore'
import { useInvitationStatsStore } from '../../stores/invitationStatsStore'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { formatDistanceToNow } from 'date-fns'

const listStore = useInvitationListStore()
const statsStore = useInvitationStatsStore()

const loading = ref(true)

const invitations = computed(() => listStore.invitations)
const stats = computed(() => ({
  total: invitations.value.length,
  pending: invitations.value.filter(i => i.status === 'pending').length,
  accepted: invitations.value.filter(i => i.status === 'accepted').length,
  expired: invitations.value.filter(i => i.status === 'expired').length
}))

const formatDate = (date: string) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

const resendInvitation = async (publicId: string) => {
  await listStore.resendInvitation(publicId)
}

const cancelInvitation = async (publicId: string) => {
  if (confirm('Are you sure you want to cancel this invitation?')) {
    await listStore.cancelInvitation(publicId)
  }
}

onMounted(async () => {
  try {
    await listStore.fetchMyInvitations()
  } finally {
    loading.value = false
  }
})
</script>
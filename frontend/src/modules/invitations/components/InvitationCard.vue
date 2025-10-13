<template>
  <BaseCard 
    :class="borderClasses"
    variant="elevated"
    size="md"
  >
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <div>
        <h3 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100">
          {{ invitation.full_name || invitation.email }}
        </h3>
        <p class="text-sm text-secondary-600 dark:text-secondary-400">
          {{ invitation.full_name ? invitation.email : `Role: ${getRoleDisplayName(invitation.role)}` }}
        </p>
        <p v-if="invitation.full_name" class="text-sm text-secondary-600 dark:text-secondary-400">
          Role: {{ getRoleDisplayName(invitation.role) }}
        </p>
      </div>
      <StatusBadge :status="getEffectiveStatus(invitation)" />
    </div>

    <!-- Details -->
    <div class="space-y-2 mb-4">
      <div class="flex items-center text-sm text-secondary-600 dark:text-secondary-300">
        <UserIcon class="h-4 w-4 mr-2" />
        <span>Invited by {{ invitation.invited_by.full_name || invitation.invited_by.email }}</span>
      </div>
      
      <div class="flex items-center text-sm text-secondary-600 dark:text-secondary-300">
        <CalendarIcon class="h-4 w-4 mr-2" />
        <span>{{ formatDate(invitation.created_at) }}</span>
      </div>

      <div v-if="invitation.status === 'pending' && !invitation.is_expired" class="flex items-center text-sm">
        <ClockIcon class="h-4 w-4 mr-2" :class="expiryColorClass" />
        <span :class="expiryColorClass">
          Expires in {{ getTimeUntilExpiry() }}
        </span>
      </div>

      <div v-if="invitation.status === 'accepted'" class="flex items-center text-sm text-success-600 dark:text-success-400">
        <CheckCircleIcon class="h-4 w-4 mr-2" />
        <span>Accepted by {{ invitation.accepted_by?.full_name || invitation.accepted_by?.email }}</span>
      </div>

      <div v-if="invitation.organization_name" class="flex items-center text-sm text-secondary-600 dark:text-secondary-300">
        <BuildingOfficeIcon class="h-4 w-4 mr-2" />
        <span>{{ invitation.organization_name }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div v-if="showActions" class="flex justify-end">
      <div class="relative" ref="dropdownRef">
        <button
          @click="toggleDropdown"
          class="p-2 text-secondary-500 hover:text-secondary-700 dark:text-secondary-400 dark:hover:text-secondary-200 rounded-lg hover:bg-secondary-100 dark:hover:bg-secondary-700 transition-colors"
          :disabled="loading"
        >
          <EllipsisVerticalIcon class="h-5 w-5" />
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="isDropdownOpen"
          class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-secondary-800 ring-1 ring-black ring-opacity-5 z-dropdown"
        >
          <div class="py-1">
            <button
              v-if="canResend"
              @click="handleAction('resend')"
              class="flex items-center w-full px-4 py-2 text-sm text-secondary-700 dark:text-secondary-200 hover:bg-secondary-100 dark:hover:bg-secondary-700"
            >
              <ArrowPathIcon class="h-4 w-4 mr-3" />
              Resend Invitation
            </button>

            <button
              v-if="canExtend"
              @click="handleAction('extend')"
              class="flex items-center w-full px-4 py-2 text-sm text-secondary-700 dark:text-secondary-200 hover:bg-secondary-100 dark:hover:bg-secondary-700"
            >
              <CalendarDaysIcon class="h-4 w-4 mr-3" />
              Extend Expiry
            </button>

            <button
              v-if="canCopyLink && invitation.status === 'pending'"
              @click="handleCopyLink"
              class="flex items-center w-full px-4 py-2 text-sm text-secondary-700 dark:text-secondary-200 hover:bg-secondary-100 dark:hover:bg-secondary-700"
            >
              <ClipboardDocumentIcon class="h-4 w-4 mr-3" />
              Copy Link
            </button>


            <div v-if="canCancel || canDelete" class="border-t border-secondary-200 dark:border-secondary-700 my-1"></div>
            
            <button
              v-if="canCancel"
              @click="handleAction('cancel')"
              class="flex items-center w-full px-4 py-2 text-sm text-warning-600 dark:text-warning-400 hover:bg-warning-50 dark:hover:bg-warning-900/20"
            >
              <XCircleIcon class="h-4 w-4 mr-3" />
              Cancel Invitation
            </button>

            <button
              v-if="canDelete"
              @click="handleAction('delete')"
              class="flex items-center w-full px-4 py-2 text-sm text-danger-600 dark:text-danger-400 hover:bg-danger-50 dark:hover:bg-danger-900/20"
            >
              <TrashIcon class="h-4 w-4 mr-3" />
              Delete Invitation
            </button>
          </div>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  UserIcon,
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  BuildingOfficeIcon,
  ArrowPathIcon,
  CalendarDaysIcon,
  XCircleIcon,
  ClipboardDocumentIcon,
  EllipsisVerticalIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import { BaseCard } from '@/shared/components'
import type { Invitation, InvitationStatus } from '../types/invitation.types'
import { ROLE_DISPLAY_NAMES } from '../types/invitation.types'
import invitationService from '../services/invitationService'
import { useToastStore } from '@/stores/toast'
import StatusBadge from '@/components/common/StatusBadge.vue'

interface Props {
  invitation: Invitation
  showActions?: boolean
  canResend?: boolean
  canExtend?: boolean
  canCancel?: boolean
  canDelete?: boolean
  canCopyLink?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
  canResend: false,
  canExtend: false,
  canCancel: false,
  canDelete: false,
  canCopyLink: true,
  loading: false
})

const emit = defineEmits<{
  resend: [id: string]
  extend: [id: string]
  cancel: [id: string]
  delete: [id: string]
}>()

const toastStore = useToastStore()

// Status-based border styling
const borderClasses = computed(() => ({
  'border-l-4': true,
  'border-warning-500': props.invitation.status === 'pending',
  'border-success-500': props.invitation.status === 'accepted',
  'border-danger-500': props.invitation.status === 'expired' || props.invitation.is_expired,
  'border-secondary-500': props.invitation.status === 'cancelled'
}))

// Dropdown state
const isDropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement>()

// Toggle dropdown
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isDropdownOpen.value = false
  }
}

// Handle action from dropdown
const handleAction = (action: 'resend' | 'extend' | 'cancel' | 'delete') => {
  isDropdownOpen.value = false
  const id = props.invitation.public_id
  
  switch (action) {
    case 'resend':
      emit('resend', id)
      break
    case 'extend':
      emit('extend', id)
      break
    case 'cancel':
      emit('cancel', id)
      break
    case 'delete':
      emit('delete', id)
      break
  }
}

// Handle copy link with dropdown close
const handleCopyLink = () => {
  isDropdownOpen.value = false
  copyInvitationLink()
}

// Setup click outside listener
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Get effective status (considering is_expired flag)
const getEffectiveStatus = (invitation: Invitation): InvitationStatus => {
  if (invitation.is_expired && invitation.status === 'pending') {
    return 'expired'
  }
  return invitation.status
}

// Get role display name
const getRoleDisplayName = (role: string) => {
  return ROLE_DISPLAY_NAMES[role as keyof typeof ROLE_DISPLAY_NAMES] || role
}

// Format date
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Get time until expiry
const getTimeUntilExpiry = () => {
  return invitationService.getTimeUntilExpiry(props.invitation)
}

// Expiry color class
const expiryColorClass = computed(() => {
  const timeStr = getTimeUntilExpiry()
  if (timeStr === 'Expired') return 'text-danger-600 dark:text-danger-400'
  
  const days = parseInt(timeStr.split(' ')[0])
  if (days <= 1) return 'text-danger-600 dark:text-danger-400'
  if (days <= 3) return 'text-warning-600 dark:text-warning-400'
  return 'text-secondary-600 dark:text-secondary-300'
})

// Copy invitation link
const copyInvitationLink = async () => {
  try {
    // Generate the invitation URL using the public_id
    // The backend should handle token validation via the public_id
    const url = `${window.location.origin}/invitations/accept/${props.invitation.public_id}`
    await navigator.clipboard.writeText(url)
    toastStore.success('Invitation link copied to clipboard!')
  } catch (error) {
    toastStore.error('Failed to copy link')
  }
}
</script>

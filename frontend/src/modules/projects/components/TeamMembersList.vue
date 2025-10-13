<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Team Members</h3>

      <div v-if="!members.length" class="text-center py-8 text-gray-500 dark:text-gray-400">
        No team members yet
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="member in members"
          :key="member.public_id"
          class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div class="flex items-center">
            <div class="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center">
              <span class="text-white font-medium">
                {{ getUserInitials(member.user) }}
              </span>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ getUserDisplayName(member.user) }}
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ member.role }}</p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <span class="text-xs text-gray-500 dark:text-gray-400">
              Joined {{ formatDate(member.joined_at) }}
            </span>
            <button
              v-if="canManage && member.role !== 'owner'"
              @click="$emit('remove', member.public_id)"
              class="text-red-600 dark:text-red-400 hover:text-red-800"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'
import type { ProjectMembership } from '../types/project.types'
import { getUserDisplayName, getUserInitials } from '@/utils/userHelpers'
import { formatDate } from '@/utils/dateHelpers'

interface Props {
  members: ProjectMembership[]
  canManage?: boolean
}

defineProps<Props>()
defineEmits<{
  remove: [memberId: string]
}>()

</script>

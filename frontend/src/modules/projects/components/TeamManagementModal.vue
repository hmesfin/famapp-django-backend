<template>
  <TransitionRoot as="template" :show="show">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 dark:bg-gray-900 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl">
              <div class="bg-white dark:bg-gray-800 px-6 pt-6 pb-4">
                <div class="flex items-center justify-between mb-4">
                  <DialogTitle as="h3" class="text-xl font-semibold leading-6 text-gray-900 dark:text-gray-100">
                    Manage Team Members
                  </DialogTitle>
                  <button
                    @click="$emit('close')"
                    class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                  >
                    <XMarkIcon class="h-6 w-6" />
                  </button>
                </div>

                <!-- Add Member Section -->
                <div class="mb-6">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Add Team Member</h4>
                  <div class="flex gap-3">
                    <div class="flex-1 relative">
                      <input
                        v-model="searchQuery"
                        type="text"
                        placeholder="Search by email or name..."
                        class="block w-full rounded-lg border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-base px-4 py-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                        @input="handleSearch"
                      />
                      
                      <!-- Search Results Dropdown -->
                      <div v-if="showSearchResults && searchResults.length > 0" class="absolute z-10 mt-1 w-full bg-white dark:bg-gray-700 shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                        <div
                          v-for="user in searchResults"
                          :key="user.public_id"
                          @click="selectUser(user)"
                          class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-100 dark:hover:bg-gray-600"
                        >
                          <div class="flex items-center">
                            <span class="font-normal block truncate text-gray-900 dark:text-gray-100">
                              {{ getUserDisplayName(user) }}
                            </span>
                            <span class="text-gray-500 dark:text-gray-400 ml-2 truncate">
                              {{ user.email }}
                            </span>
                          </div>
                        </div>
                      </div>

                      <!-- Selected User Display -->
                      <div v-if="selectedUser" class="mt-2 p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-md flex items-center justify-between">
                        <span class="text-sm text-indigo-700 dark:text-indigo-300">
                          {{ getUserDisplayName(selectedUser) }} ({{ selectedUser.email }})
                        </span>
                        <button
                          @click="selectedUser = null"
                          class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200"
                        >
                          <XMarkIcon class="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    
                    <select
                      v-model="selectedRole"
                      class="rounded-lg border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-base px-4 py-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="developer">Developer</option>
                      <option value="manager">Manager</option>
                    </select>
                    
                    <button
                      @click="addMember"
                      :disabled="!selectedUser || addingMember"
                      class="inline-flex items-center px-5 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <PlusIcon class="-ml-1 mr-2 h-4 w-4" />
                      Add
                    </button>
                  </div>
                </div>

                <!-- Current Members List -->
                <div>
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Current Team Members</h4>
                  <div class="space-y-2 max-h-96 overflow-y-auto">
                    <div
                      v-for="member in members"
                      :key="member.public_id"
                      class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
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
                          <p class="text-xs text-gray-500 dark:text-gray-400">
                            {{ member.user?.email || 'No email' }} · {{ capitalizeRole(member.role) }}
                          </p>
                        </div>
                      </div>
                      
                      <div class="flex items-center space-x-3">
                        <span class="text-xs text-gray-500 dark:text-gray-400">
                          Joined {{ formatDate(member.joined_at) }}
                        </span>
                        
                        <!-- Role selector for non-owners -->
                        <select
                          v-if="member.role !== 'owner'"
                          :value="member.role"
                          @change="updateMemberRole(member, $event)"
                          class="text-sm rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                        >
                          <option value="viewer">Viewer</option>
                          <option value="developer">Developer</option>
                          <option value="manager">Manager</option>
                        </select>
                        
                        <!-- Owner badge -->
                        <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
                          Owner
                        </span>
                        
                        <!-- Remove button for non-owners -->
                        <button
                          v-if="member.role !== 'owner'"
                          @click="removeMember(member)"
                          :disabled="removingMemberId === member.public_id"
                          class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 disabled:opacity-50"
                        >
                          <TrashIcon class="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-gray-50 dark:bg-gray-900 px-6 py-3 flex justify-end">
                <button
                  @click="$emit('close')"
                  class="inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Close
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'
import type { ProjectMembership, UserSummary } from '../types/project.types'
import { getUserDisplayName, getUserInitials } from '@/utils/userHelpers'
import { useToastStore } from '@/stores/toast'
import projectService from '../services/projectService'
import userService from '@/services/userService'
import { formatDate } from '@/utils/dateHelpers'

interface Props {
  show: boolean
  projectId: string
  members: ProjectMembership[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  memberAdded: [member: ProjectMembership]
  memberRemoved: [memberId: string]
  memberUpdated: [member: ProjectMembership]
}>()

const toastStore = useToastStore()

// State
const searchQuery = ref('')
const searchResults = ref<UserSummary[]>([])
const showSearchResults = ref(false)
const selectedUser = ref<UserSummary | null>(null)
const selectedRole = ref('developer')
const addingMember = ref(false)
const removingMemberId = ref<string | null>(null)
const searchTimeout = ref<NodeJS.Timeout | null>(null)

// Reset search when modal closes
watch(() => props.show, (isOpen) => {
  if (!isOpen) {
    searchQuery.value = ''
    searchResults.value = []
    selectedUser.value = null
    selectedRole.value = 'developer'
    showSearchResults.value = false
  }
})

// Search for users
async function handleSearch() {
  // Clear previous timeout
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }

  // Debounce search
  searchTimeout.value = setTimeout(async () => {
    if (searchQuery.value.length < 2) {
      searchResults.value = []
      showSearchResults.value = false
      return
    }

    try {
      // Search for users via API
      const users = await userService.searchUsers(searchQuery.value)

      // Filter out existing members
      const existingMemberIds = props.members.map(m => m.user?.public_id).filter(Boolean)
      searchResults.value = users.filter(user => !existingMemberIds.includes(user.public_id))
      showSearchResults.value = searchResults.value.length > 0
    } catch (error) {
      console.error('Failed to search users:', error)
      toastStore.error('Failed to search users')
    }
  }, 300)
}

function selectUser(user: UserSummary) {
  selectedUser.value = user
  showSearchResults.value = false
  searchQuery.value = getUserDisplayName(user)
}

async function addMember() {
  if (!selectedUser.value) return

  addingMember.value = true
  try {
    const newMember = await projectService.addProjectMember(
      props.projectId,
      selectedUser.value.public_id,
      selectedRole.value
    )
    
    emit('memberAdded', newMember)
    toastStore.success(`${getUserDisplayName(selectedUser.value)} added to the team!`)
    
    // Reset form
    selectedUser.value = null
    searchQuery.value = ''
    selectedRole.value = 'developer'
  } catch (error: any) {
    console.error('Failed to add member:', error)
    toastStore.error(error.message || 'Failed to add team member')
  } finally {
    addingMember.value = false
  }
}

async function removeMember(member: ProjectMembership) {
  if (!confirm(`Are you sure you want to remove ${getUserDisplayName(member.user)} from the team?`)) {
    return
  }

  removingMemberId.value = member.public_id
  try {
    await projectService.removeProjectMember(props.projectId, member.user?.public_id || '')
    emit('memberRemoved', member.public_id)
    toastStore.success(`${getUserDisplayName(member.user)} removed from the team`)
  } catch (error: any) {
    console.error('Failed to remove member:', error)
    toastStore.error(error.message || 'Failed to remove team member')
  } finally {
    removingMemberId.value = null
  }
}

async function updateMemberRole(member: ProjectMembership, event: Event) {
  const newRole = (event.target as HTMLSelectElement).value
  
  try {
    // For now, we'll update locally and emit the change
    // In production, this would call an API to update the role
    const updatedMember = { ...member, role: newRole }
    emit('memberUpdated', updatedMember)
    toastStore.success(`${getUserDisplayName(member.user)}'s role updated to ${capitalizeRole(newRole)}`)
  } catch (error: any) {
    console.error('Failed to update member role:', error)
    toastStore.error(error.message || 'Failed to update member role')
    // Reset the select to the original value
    ;(event.target as HTMLSelectElement).value = member.role
  }
}

function capitalizeRole(role: string): string {
  return role.charAt(0).toUpperCase() + role.slice(1)
}

</script>
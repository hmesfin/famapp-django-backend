<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">Sprints</h3>
        <button
          v-if="canManage"
          @click="$emit('create')"
          class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon class="-ml-1 mr-2 h-4 w-4" />
          New Sprint
        </button>
      </div>
      
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
      </div>
      
      <div v-else-if="!sprints.length" class="text-center py-8 text-gray-500 dark:text-gray-400">
        No sprints created yet
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="sprint in sprints"
          :key="sprint.public_id"
          class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
          :class="{ 'ring-2 ring-indigo-500 bg-indigo-50 dark:bg-indigo-900/20': sprint.is_active }"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center">
                <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ sprint.name }}</h4>
                <span
                  v-if="sprint.is_active"
                  class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200"
                >
                  Active
                </span>
              </div>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ sprint.goal }}</p>
              <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(sprint.start_date) }} - {{ formatDate(sprint.end_date) }}
                <span class="ml-2">• {{ sprint.task_count || 0 }} tasks</span>
              </div>
              
              <!-- Sprint Stats -->
              <div v-if="sprint.stats" class="mt-3">
                <div class="flex items-center text-xs text-gray-600 dark:text-gray-400">
                  <span>Progress: {{ sprint.stats.completed_tasks }} / {{ sprint.stats.total_tasks }} tasks</span>
                  <span class="ml-3">
                    ({{ Math.round(sprint.stats.completion_percentage || 0) }}%)
                  </span>
                </div>
                <div class="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div
                    class="bg-green-600 h-1.5 rounded-full transition-all duration-300"
                    :style="{ width: `${sprint.stats.completion_percentage || 0}%` }"
                  />
                </div>
              </div>
            </div>
            
            <!-- Sprint Actions -->
            <div v-if="canManage" class="flex items-center space-x-2 ml-4">
              <Menu as="div" class="relative inline-block text-left">
                <MenuButton class="inline-flex items-center p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <EllipsisVerticalIcon class="h-5 w-5" />
                </MenuButton>
                
                <transition
                  enter-active-class="transition duration-100 ease-out"
                  enter-from-class="transform scale-95 opacity-0"
                  enter-to-class="transform scale-100 opacity-100"
                  leave-active-class="transition duration-75 ease-in"
                  leave-from-class="transform scale-100 opacity-100"
                  leave-to-class="transform scale-95 opacity-0"
                >
                  <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-gray-700 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div class="py-1">
                      <MenuItem v-if="!sprint.is_active" v-slot="{ active }">
                        <button
                          @click="$emit('activate', sprint.public_id)"
                          :class="[
                            active ? 'bg-gray-100 dark:bg-gray-600 text-gray-900 dark:text-gray-100' : 'text-gray-700 dark:text-gray-300',
                            'block w-full text-left px-4 py-2 text-sm'
                          ]"
                        >
                          <PlayIcon class="inline-block h-4 w-4 mr-2" />
                          Activate Sprint
                        </button>
                      </MenuItem>
                      
                      <MenuItem v-else v-slot="{ active }">
                        <button
                          @click="$emit('deactivate', sprint.public_id)"
                          :class="[
                            active ? 'bg-gray-100 dark:bg-gray-600 text-gray-900 dark:text-gray-100' : 'text-gray-700 dark:text-gray-300',
                            'block w-full text-left px-4 py-2 text-sm'
                          ]"
                        >
                          <PauseIcon class="inline-block h-4 w-4 mr-2" />
                          Deactivate Sprint
                        </button>
                      </MenuItem>
                      
                      <MenuItem v-slot="{ active }">
                        <button
                          @click="$emit('edit', sprint)"
                          :class="[
                            active ? 'bg-gray-100 dark:bg-gray-600 text-gray-900 dark:text-gray-100' : 'text-gray-700 dark:text-gray-300',
                            'block w-full text-left px-4 py-2 text-sm'
                          ]"
                        >
                          <PencilIcon class="inline-block h-4 w-4 mr-2" />
                          Edit Sprint
                        </button>
                      </MenuItem>
                      
                      <MenuItem v-slot="{ active }">
                        <button
                          @click="$emit('delete', sprint)"
                          :class="[
                            active ? 'bg-gray-100 dark:bg-gray-600 text-gray-900 dark:text-gray-100' : 'text-gray-700 dark:text-gray-300',
                            'block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400'
                          ]"
                          :disabled="sprint.task_count > 0"
                        >
                          <TrashIcon class="inline-block h-4 w-4 mr-2" />
                          {{ sprint.task_count > 0 ? 'Has tasks (cannot delete)' : 'Delete Sprint' }}
                        </button>
                      </MenuItem>
                    </div>
                  </MenuItems>
                </transition>
              </Menu>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { 
  PlusIcon, 
  EllipsisVerticalIcon,
  PlayIcon,
  PauseIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { Sprint } from '../types/project.types'
import { formatDate } from '@/utils/dateHelpers'

interface Props {
  sprints: Sprint[]
  canManage?: boolean
  loading?: boolean
}

defineProps<Props>()

defineEmits<{
  create: []
  edit: [sprint: Sprint]
  delete: [sprint: Sprint]
  activate: [sprintId: string]
  deactivate: [sprintId: string]
}>()

</script>
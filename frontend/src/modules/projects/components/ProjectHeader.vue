<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <div class="flex items-center">
            <button
              @click="$router.back()"
              class="mr-4 text-gray-400 hover:text-gray-600 dark:text-gray-400"
            >
              <ArrowLeftIcon class="h-6 w-6" />
            </button>
            <div>
              <h2
                class="text-2xl font-bold leading-7 text-gray-900 dark:text-gray-100 sm:text-3xl sm:truncate"
              >
                {{ project.name }}
              </h2>
              <div class="mt-1 flex items-center space-x-3">
                <ProjectStatusBadge :status="project.status" />
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  Created by {{ getUserDisplayName(project.owner) }}
                </span>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ project.created_at ? formatDate(project.created_at) : 'Unknown' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 flex md:mt-0 md:ml-4 space-x-3">
          <button
            v-if="canManageTeam"
            @click="$emit('manageTeam')"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <UserGroupIcon class="-ml-1 mr-2 h-5 w-5" />
            Manage Team
          </button>
          <button
            v-if="canEdit"
            @click="$emit('editProject')"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <PencilIcon class="-ml-1 mr-2 h-5 w-5" />
            Edit
          </button>
          <button
            @click="$emit('addTask')"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Add Task
          </button>
        </div>
      </div>

      <!-- Description -->
      <div v-if="project.description" class="mt-4">
        <p class="text-gray-600 dark:text-gray-300">{{ project.description }}</p>
      </div>

      <!-- Metadata Grid -->
      <div class="mt-6 grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-3">
        <div class="sm:col-span-1">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Start Date</dt>
          <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">
            {{ project.start_date ? formatDate(project.start_date) : 'Not set' }}
          </dd>
        </div>
        <div class="sm:col-span-1">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">End Date</dt>
          <dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">
            {{ project.end_date ? formatDate(project.end_date) : 'Ongoing' }}
          </dd>
        </div>
        <div class="sm:col-span-1">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Progress</dt>
          <dd class="mt-1">
            <div class="flex items-center">
              <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="bg-indigo-600 h-2 rounded-full"
                  :style="{ width: `${projectProgress}%` }"
                ></div>
              </div>
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                {{ projectProgress }}%
              </span>
            </div>
          </dd>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="projectStats" class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div
          v-for="stat in projectStatsArray"
          :key="stat.name"
          class="bg-gray-50 dark:bg-gray-900 overflow-hidden rounded-lg px-4 py-3"
        >
          <dt class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            {{ stat.name }}
          </dt>
          <dd class="mt-1 text-2xl font-semibold text-gray-900 dark:text-gray-100">
            {{ stat.value }}
          </dd>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeftIcon, UserGroupIcon, PencilIcon, PlusIcon } from '@heroicons/vue/24/outline'
import ProjectStatusBadge from './ProjectStatusBadge.vue'
import type { Project } from '../types/project.types'
import { getUserDisplayName } from '@/utils/userHelpers'
import { formatDate } from '@/utils/dateHelpers'

interface Props {
  project: Project
  canEdit: boolean
  canManageTeam: boolean
}

const props = defineProps<Props>()

defineEmits<{
  manageTeam: []
  editProject: []
  addTask: []
}>()

const projectProgress = computed(() => {
  if (!props.project.stats) return 0
  const total = props.project.stats.total_tasks
  const completed = props.project.stats.completed_tasks
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
})

const projectStats = computed(() => props.project.stats)

const projectStatsArray = computed(() => {
  if (!projectStats.value) return []
  return [
    { name: 'Total Tasks', value: projectStats.value.total_tasks },
    { name: 'Completed', value: projectStats.value.completed_tasks },
    { name: 'In Progress', value: projectStats.value.in_progress_tasks },
    { name: 'Team Members', value: projectStats.value.team_members }
  ]
})
</script>
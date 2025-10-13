<template>
  <BaseCard
    :clickable="true"
    variant="default"
    size="md"
    @click="$emit('click', project)"
  >
    <template #header>
      <div class="flex items-start justify-between w-full">
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-secondary-900 dark:text-secondary-100 hover:text-primary-600 transition-colors">
            {{ project.name }}
          </h3>
          <p class="text-sm text-secondary-500 dark:text-secondary-400 mt-1">
            <span class="font-medium">Owner:</span> {{ getUserDisplayName(project.owner) }}
          </p>
        </div>
        
        <ProjectStatusBadge :status="project.status" />
      </div>
    </template>

    <!-- Description -->
    <p class="text-secondary-600 dark:text-secondary-400 text-sm mb-4 line-clamp-2">
      {{ project.description }}
    </p>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <div class="text-center">
        <p class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">
          {{ project.task_count || 0 }}
        </p>
        <p class="text-xs text-secondary-500 dark:text-secondary-400">Tasks</p>
      </div>
      <div class="text-center">
        <p class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">
          {{ project.member_count || 0 }}
        </p>
        <p class="text-xs text-secondary-500 dark:text-secondary-400">Members</p>
      </div>
      <div class="text-center">
        <p class="text-2xl font-bold text-secondary-900 dark:text-secondary-100">{{ daysLeft }}</p>
        <p class="text-xs text-secondary-500 dark:text-secondary-400">Days Left</p>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="project.stats" class="mb-4">
      <div class="flex justify-between text-sm text-secondary-600 dark:text-secondary-400 mb-1">
        <span>Progress</span>
        <span>{{ progressPercentage }}%</span>
      </div>
      <div class="w-full bg-secondary-200 dark:bg-secondary-700 rounded-full h-2">
        <div
          class="h-2 rounded-full transition-all duration-300"
          :class="progressColor"
          :style="{ width: `${progressPercentage}%` }"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between">
        <div class="flex items-center text-sm text-secondary-500 dark:text-secondary-400">
          <CalendarIcon class="h-4 w-4 mr-1" />
          <span>{{ formatDate(project.start_date) }}</span>
          <span class="mx-1">→</span>
          <span>{{ project.end_date ? formatDate(project.end_date) : 'Ongoing' }}</span>
        </div>

        <!-- Action buttons -->
        <div class="flex space-x-2" @click.stop>
          <BaseButton
            v-if="canEdit"
            variant="ghost"
            size="sm"
            :leading-icon="PencilIcon"
            aria-label="Edit project"
            @click="$emit('edit', project)"
          />
          <BaseButton
            v-if="canDelete"
            variant="ghost"
            size="sm"
            :leading-icon="TrashIcon"
            aria-label="Delete project"
            class="text-danger-600 hover:text-danger-700 hover:bg-danger-50 dark:text-danger-400 dark:hover:text-danger-300 dark:hover:bg-danger-900/20"
            @click="$emit('delete', project)"
          />
        </div>
      </div>
    </template>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CalendarIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import ProjectStatusBadge from './ProjectStatusBadge.vue'
import type { Project } from '../types/project.types'
import { useAuthStore } from '@/stores/auth'
import { getUserDisplayName } from '@/utils/userHelpers'
import { formatDate } from '@/utils/dateHelpers'

interface Props {
  project: Project
  canEdit?: boolean
  canDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canEdit: false,
  canDelete: false,
})

defineEmits<{
  click: [project: Project]
  edit: [project: Project]
  delete: [project: Project]
}>()

const authStore = useAuthStore()

// Computed
const daysLeft = computed(() => {
  if (!props.project.end_date) return '∞'

  const end = new Date(props.project.end_date)
  const today = new Date()
  const diff = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

  return diff > 0 ? diff : 0
})

const progressPercentage = computed(() => {
  if (!props.project.stats) return 0
  const { total_tasks, completed_tasks } = props.project.stats
  if (total_tasks === 0) return 0
  return Math.round((completed_tasks / total_tasks) * 100)
})

const progressColor = computed(() => {
  const percentage = progressPercentage.value
  if (percentage < 25) return 'bg-danger-500'
  if (percentage < 50) return 'bg-warning-500'
  if (percentage < 75) return 'bg-info-500'
  return 'bg-success-500'
})

</script>

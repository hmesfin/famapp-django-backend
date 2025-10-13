<template>
  <BaseCard
    :clickable="true"
    variant="default"
    size="sm"
    @click="$emit('click', task)"
    :class="{
      'ring-2 ring-primary-500 dark:ring-primary-400': selected,
      'group': true
    }"
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="flex-1">
          <h4 class="text-sm font-medium text-secondary-900 dark:text-secondary-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
            {{ task.title }}
          </h4>
          <div class="flex items-center mt-1 space-x-2">
            <TaskPriorityBadge :priority="task.priority" size="sm" />
            <BaseBadge
              v-if="task.story_points > 0"
              :content="`${task.story_points} pts`"
              variant="secondary"
              size="xs"
              :style="'soft'"
            />
          </div>
        </div>
        
        <!-- Actions Menu -->
        <div class="opacity-0 group-hover:opacity-100 transition-opacity">
          <Menu as="div" class="relative">
            <MenuButton
              class="flex items-center text-secondary-400 hover:text-secondary-600 dark:hover:text-secondary-300 focus:outline-none focus:text-secondary-600"
              @click.stop
            >
              <EllipsisVerticalIcon class="h-5 w-5" />
            </MenuButton>
            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-secondary-800 py-1 shadow-lg ring-1 ring-black dark:ring-secondary-700 ring-opacity-5 focus:outline-none">
                <MenuItem v-slot="{ active }">
                  <button
                    @click.stop="$emit('edit', task)"
                    :class="[
                      active ? 'bg-secondary-100 dark:bg-secondary-700' : '',
                      'flex w-full items-center px-4 py-2 text-sm text-secondary-700 dark:text-secondary-300'
                    ]"
                  >
                    <PencilIcon class="mr-3 h-4 w-4" />
                    Edit Task
                  </button>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <button
                    @click.stop="$emit('duplicate', task)"
                    :class="[
                      active ? 'bg-secondary-100 dark:bg-secondary-700' : '',
                      'flex w-full items-center px-4 py-2 text-sm text-secondary-700 dark:text-secondary-300'
                    ]"
                  >
                    <DocumentDuplicateIcon class="mr-3 h-4 w-4" />
                    Duplicate
                  </button>
                </MenuItem>
                <div class="border-t border-secondary-100 dark:border-secondary-700"></div>
                <MenuItem v-slot="{ active }">
                  <button
                    @click.stop="$emit('delete', task)"
                    :class="[
                      active ? 'bg-danger-50 dark:bg-danger-900/20' : '',
                      'flex w-full items-center px-4 py-2 text-sm text-danger-700 dark:text-danger-400'
                    ]"
                  >
                    <TrashIcon class="mr-3 h-4 w-4" />
                    Delete
                  </button>
                </MenuItem>
              </MenuItems>
            </transition>
          </Menu>
        </div>
      </div>
    </template>

    <!-- Description -->
    <p v-if="task.description" class="text-xs text-secondary-600 dark:text-secondary-400 mb-3 line-clamp-2">
      {{ task.description }}
    </p>

    <!-- Assignee -->
    <div v-if="task.assignee" class="flex items-center mb-3">
      <div class="flex items-center text-xs text-secondary-500 dark:text-secondary-400">
        <UserIcon class="h-3 w-3 mr-1" />
        <span>{{ getUserDisplayName(task.assignee) }}</span>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between">
        <!-- Due Date -->
        <div v-if="task.due_date" class="flex items-center text-xs">
          <CalendarDaysIcon class="h-3 w-3 mr-1" />
          <span 
            :class="{
              'text-danger-600 dark:text-danger-400': isOverdue,
              'text-warning-600 dark:text-warning-400': isDueSoon,
              'text-secondary-500 dark:text-secondary-400': !isOverdue && !isDueSoon
            }"
          >
            {{ formatDueDate(task.due_date) }}
          </span>
        </div>
        <div v-else class="text-xs text-secondary-400 dark:text-secondary-500">
          No due date
        </div>

        <!-- Comments Count -->
        <div v-if="task.comments && task.comments.length > 0" class="flex items-center text-xs text-secondary-500 dark:text-secondary-400">
          <ChatBubbleLeftIcon class="h-3 w-3 mr-1" />
          <span>{{ task.comments.length }}</span>
        </div>
      </div>
    </template>

    <!-- Status Indicator (for drag preview) -->
    <div 
      v-if="showStatusIndicator"
      class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b"
      :class="statusIndicatorColor"
    />
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import {
  EllipsisVerticalIcon,
  PencilIcon,
  TrashIcon,
  DocumentDuplicateIcon,
  UserIcon,
  CalendarDaysIcon,
  ChatBubbleLeftIcon
} from '@heroicons/vue/24/outline'
import BaseCard from '@/shared/components/BaseCard.vue'
import BaseBadge from '@/shared/components/BaseBadge.vue'
import TaskPriorityBadge from './TaskPriorityBadge.vue'
import type { Task } from '../types/project.types'
import { getUserDisplayName } from '@/utils/userHelpers'
import { formatDueDate } from '@/utils/dateHelpers'

interface Props {
  task: Task
  selected?: boolean
  showStatusIndicator?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  showStatusIndicator: false
})

const emit = defineEmits<{
  click: [task: Task]
  edit: [task: Task]
  duplicate: [task: Task]
  delete: [task: Task]
}>()

// Computed properties for due date handling
const isOverdue = computed(() => {
  if (!props.task.due_date) return false
  return new Date(props.task.due_date) < new Date()
})

const isDueSoon = computed(() => {
  if (!props.task.due_date || isOverdue.value) return false
  const dueDate = new Date(props.task.due_date)
  const threeDaysFromNow = new Date()
  threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3)
  return dueDate <= threeDaysFromNow
})

const statusIndicatorColor = computed(() => {
  switch (props.task.status) {
    case 'todo':
      return 'from-secondary-400 to-secondary-600'
    case 'in_progress':
      return 'from-info-400 to-info-600'
    case 'review':
      return 'from-warning-400 to-warning-600'
    case 'done':
      return 'from-success-400 to-success-600'
    case 'blocked':
      return 'from-danger-400 to-danger-600'
    default:
      return 'from-secondary-400 to-secondary-600'
  }
})

// Utility functions
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <!-- Board Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Task Board</h2>
      <div class="flex items-center space-x-3">
        <!-- Add Task Button -->
        <button
          @click="$emit('create-task')"
          class="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <PlusIcon class="-ml-1 mr-2 h-4 w-4" />
          Add Task
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!tasks || !tasks.length" class="text-center py-12">
      <ClipboardDocumentListIcon class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No tasks yet</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by creating a new task.</p>
      <div class="mt-6">
        <button
          @click="$emit('create-task')"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
          Create Task
        </button>
      </div>
    </div>

    <!-- Kanban Board -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <!-- Columns -->
      <div
        v-for="column in columns"
        :key="column.status"
        class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 min-h-96"
        :class="`column-${column.status}`"
        @drop="handleDrop($event, column.status)"
        @dragover.prevent
        @dragenter.prevent
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <div 
              class="w-3 h-3 rounded-full mr-2"
              :class="column.color"
            ></div>
            <h3 class="font-semibold text-gray-700 dark:text-gray-300">{{ column.title }}</h3>
          </div>
          <span class="text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-full">
            {{ getTasksByStatus(column.status).length }}
          </span>
        </div>

        <!-- Drop Zone -->
        <div 
          class="space-y-3 min-h-64"
          :class="{
            'border-2 border-dashed border-indigo-300 dark:border-indigo-600 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg': isDragOver && draggedOverColumn === column.status
          }"
          @dragover.prevent="handleDragOver(column.status)"
          @dragleave="handleDragLeave"
        >
          <!-- Tasks -->
          <TaskCard
            v-for="task in getTasksByStatus(column.status)"
            :key="task.public_id"
            :task="task"
            :show-status-indicator="true"
            :selected="selectedTaskId === task.public_id"
            :draggable="true"
            @click="handleTaskClick(task)"
            @edit="$emit('edit-task', task)"
            @duplicate="$emit('duplicate-task', task)"
            @delete="$emit('delete-task', task)"
            @dragstart="handleDragStart($event, task)"
            @dragend="handleDragEnd"
            :class="{
              'opacity-50': draggedTask && draggedTask.public_id === task.public_id,
              'cursor-grab': !draggedTask || draggedTask.public_id !== task.public_id,
              'cursor-grabbing': draggedTask && draggedTask.public_id === task.public_id
            }"
          />

          <!-- Empty Column Message -->
          <div 
            v-if="getTasksByStatus(column.status).length === 0"
            class="flex items-center justify-center h-32 text-sm text-gray-400 dark:text-gray-500 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg"
          >
            Drop tasks here or
            <button 
              @click="$emit('create-task', column.status)"
              class="ml-1 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 underline"
            >
              create new
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <TaskDetailModal
      v-if="selectedTask"
      :show="showTaskDetail"
      :task="selectedTask"
      @close="closeTaskDetail"
      @edit="handleEditFromDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ClipboardDocumentListIcon, PlusIcon } from '@heroicons/vue/24/outline'
import TaskCard from './TaskCard.vue'
import TaskDetailModal from './TaskDetailModal.vue'
import type { Task, TaskStatus } from '../types/project.types'
import { useTaskStore } from '../stores/taskStore'

interface Props {
  tasks?: Task[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  'update-status': [taskId: string, status: TaskStatus]
  'create-task': [initialStatus?: TaskStatus]
  'edit-task': [task: Task]
  'duplicate-task': [task: Task] 
  'delete-task': [task: Task]
  'task-click': [task: Task]
}>()

// State for drag and drop
const isDragOver = ref(false)
const draggedTask = ref<Task | null>(null)
const draggedOverColumn = ref<TaskStatus | null>(null)

// State for task selection and detail view
const selectedTaskId = ref<string | null>(null)
const showTaskDetail = ref(false)
const fullTaskDetails = ref<Task | null>(null)
const loadingTaskDetails = ref(false)

const taskStore = useTaskStore()

const selectedTask = computed(() => {
  // Use full task details if available, otherwise fall back to list data
  return fullTaskDetails.value || (selectedTaskId.value && props.tasks ? 
    props.tasks.find(task => task.public_id === selectedTaskId.value) : null)
})

const columns = [
  { 
    status: 'todo' as TaskStatus, 
    title: 'To Do', 
    color: 'bg-gray-400',
    nextStatus: 'in_progress' as TaskStatus 
  },
  { 
    status: 'in_progress' as TaskStatus, 
    title: 'In Progress', 
    color: 'bg-blue-500',
    nextStatus: 'review' as TaskStatus 
  },
  { 
    status: 'review' as TaskStatus, 
    title: 'In Review', 
    color: 'bg-yellow-500',
    nextStatus: 'done' as TaskStatus 
  },
  { 
    status: 'done' as TaskStatus, 
    title: 'Done', 
    color: 'bg-green-500',
    nextStatus: null 
  },
  { 
    status: 'blocked' as TaskStatus, 
    title: 'Blocked', 
    color: 'bg-red-500',
    nextStatus: null 
  }
]

function getTasksByStatus(status: TaskStatus) {
  return (props.tasks || []).filter(task => task.status === status)
}

async function handleTaskClick(task: Task) {
  selectedTaskId.value = task.public_id
  showTaskDetail.value = true
  loadingTaskDetails.value = true
  
  // Fetch full task details including project object
  try {
    const taskDetails = await taskStore.fetchTask(task.public_id)
    fullTaskDetails.value = taskDetails
  } catch (error) {
    console.error('Failed to fetch task details:', error)
    // Fall back to using the list data
    fullTaskDetails.value = null
  } finally {
    loadingTaskDetails.value = false
  }
  
  emit('task-click', task)
}

function closeTaskDetail() {
  showTaskDetail.value = false
  selectedTaskId.value = null
  fullTaskDetails.value = null
}

function handleEditFromDetail(task: Task) {
  closeTaskDetail()
  emit('edit-task', task)
}

// Drag and drop handlers
function handleDragStart(event: DragEvent, task: Task) {
  draggedTask.value = task
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', task.public_id)
  }
}

function handleDragEnd() {
  draggedTask.value = null
  isDragOver.value = false
  draggedOverColumn.value = null
}

function handleDragOver(columnStatus: TaskStatus) {
  if (!draggedTask.value) return
  
  isDragOver.value = true
  draggedOverColumn.value = columnStatus
}

function handleDragLeave() {
  // Small delay to prevent flickering when moving between child elements
  setTimeout(() => {
    isDragOver.value = false
    draggedOverColumn.value = null
  }, 100)
}

function handleDrop(event: DragEvent, newStatus: TaskStatus) {
  event.preventDefault()
  
  if (!draggedTask.value) return
  
  const taskId = event.dataTransfer?.getData('text/plain')
  
  if (taskId && draggedTask.value.public_id === taskId) {
    // Only emit if status actually changed
    if (draggedTask.value.status !== newStatus) {
      emit('update-status', draggedTask.value.public_id, newStatus)
    }
  }
  
  handleDragEnd()
}
</script>

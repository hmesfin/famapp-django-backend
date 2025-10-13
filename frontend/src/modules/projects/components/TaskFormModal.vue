<template>
  <BaseModal
    :show="show"
    :title="task ? 'Edit Task' : 'New Task'"
    size="xl"
    @close="$emit('close')"
  >
    <form @submit.prevent="onSubmit">
      <!-- Header icon and description -->
      <div class="sm:flex sm:items-start mb-6">
        <div class="mx-auto flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-info-100 dark:bg-info-900/50 sm:mx-0 sm:h-12 sm:w-12">
          <ClipboardDocumentListIcon class="h-7 w-7 text-info-600 dark:text-info-400" />
        </div>
        <div class="mt-4 text-center sm:ml-5 sm:mt-0 sm:text-left w-full">
          <p class="text-sm text-secondary-500 dark:text-secondary-400">
            {{ task ? 'Update task details below' : 'Create a new task for your project' }}
          </p>
        </div>
      </div>
                      
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <!-- Title -->
        <div class="sm:col-span-2">
          <BaseInput
            v-model="title"
            label="Task Title"
            placeholder="Enter task title..."
            :error="titleError"
            :disabled="loading"
            required
          />
        </div>

        <!-- Description -->
        <div class="sm:col-span-2">
          <BaseInput
            v-model="description"
            label="Description"
            type="textarea"
            rows="5"
            placeholder="Describe the task in detail..."
            :error="descriptionError"
            :disabled="loading"
          />
        </div>

        <!-- Status -->
        <div>
          <BaseSelect
            v-model="status"
            label="Status"
            :options="statusOptions"
            :error="statusError"
            :disabled="loading"
            required
          />
        </div>

        <!-- Priority -->
        <div>
          <BaseSelect
            v-model="priority"
            label="Priority"
            :options="priorityOptions"
            :error="priorityError"
            :disabled="loading"
            required
          />
        </div>

        <!-- Story Points -->
        <div>
          <BaseSelect
            v-model="storyPoints"
            label="Story Points"
            :options="storyPointOptions"
            :error="storyPointsError"
            :disabled="loading"
          />
        </div>

        <!-- Due Date -->
        <div>
          <BaseInput
            v-model="dueDate"
            label="Due Date"
            type="date"
            :error="dueDateError"
            :disabled="loading"
          />
        </div>

        <!-- Assignee (if available) -->
        <div v-if="availableAssignees.length" class="sm:col-span-2">
          <BaseSelect
            v-model="assigneeId"
            label="Assignee"
            :options="assigneeOptions"
            :error="assigneeIdError"
            :disabled="loading"
            placeholder="Select assignee"
          />
        </div>
      </div>
    </form>
    
    <template #footer>
      <BaseButton
        variant="secondary"
        :disabled="loading"
        @click="$emit('close')"
      >
        Cancel
      </BaseButton>
      <BaseButton
        type="submit"
        variant="primary"
        :loading="loading"
        :disabled="Object.keys(errors).length > 0"
        @click="onSubmit"
      >
        {{ task ? 'Update Task' : 'Create Task' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useField, useForm } from 'vee-validate'
import { ClipboardDocumentListIcon } from '@heroicons/vue/24/outline'
import BaseModal from '@/shared/components/BaseModal.vue'
import BaseInput from '@/shared/components/BaseInput.vue'
import BaseSelect from '@/shared/components/BaseSelect.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import type { Task, TaskForm, UserSummary } from '../types/project.types'
import { taskValidationSchema } from '@/utils/veeValidate'
import { getUserDisplayName } from '@/utils/userHelpers'

interface Props {
  show: boolean
  task?: Task | null
  projectId: string
  availableAssignees?: UserSummary[]
}

const props = withDefaults(defineProps<Props>(), {
  task: null,
  availableAssignees: () => []
})

const emit = defineEmits<{
  close: []
  save: [data: TaskForm]
}>()

const loading = ref(false)

// Select options
const statusOptions = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'review', label: 'In Review' },
  { value: 'done', label: 'Done' },
  { value: 'blocked', label: 'Blocked' }
]

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' }
]

const storyPointOptions = [
  { value: 0, label: '0' },
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 5, label: '5' },
  { value: 8, label: '8' },
  { value: 13, label: '13' },
  { value: 21, label: '21' }
]

// Computed assignee options
const assigneeOptions = computed(() => [
  { value: '', label: 'Unassigned' },
  ...props.availableAssignees.map(user => ({
    value: user.public_id,
    label: `${getUserDisplayName(user)} (${user?.email || 'No email'})`
  }))
])

// VeeValidate form setup
const { handleSubmit, errors, setFieldValue, setErrors, resetForm } = useForm({
  validationSchema: taskValidationSchema,
  initialValues: {
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    story_points: 0,
    assignee_id: '',
    due_date: '',
    sprint_id: '',
    project_id: props.projectId
  } as TaskForm
})

// Individual field composables
const { value: title, errorMessage: titleError } = useField<string>('title')
const { value: description, errorMessage: descriptionError } = useField<string>('description')
const { value: status, errorMessage: statusError } = useField<string>('status')
const { value: priority, errorMessage: priorityError } = useField<string>('priority')
const { value: storyPoints, errorMessage: storyPointsError } = useField<number>('story_points')
const { value: assigneeId, errorMessage: assigneeIdError } = useField<string>('assignee_id')
const { value: dueDate, errorMessage: dueDateError } = useField<string>('due_date')
const { value: sprintId, errorMessage: sprintIdError } = useField<string>('sprint_id')

// Reset form when modal opens/closes or task changes
watch([() => props.show, () => props.task], () => {
  if (props.show) {
    resetFormData()
  }
})

function resetFormData() {
  if (props.task) {
    // Edit mode - populate form with task data
    const assigneeId = props.task.assignee?.public_id || ''
    
    // Handle project_id safely - it could be a string or an object
    let projectId = props.projectId // Default to the prop
    if (props.task.project) {
      projectId = typeof props.task.project === 'string' 
        ? props.task.project 
        : props.task.project.public_id
    }
    
    // Handle sprint_id safely - it could be a string or an object
    let sprintId = ''
    if (props.task.sprint) {
      sprintId = typeof props.task.sprint === 'string'
        ? props.task.sprint
        : props.task.sprint.public_id
    }
    
    // Format due_date for input field (YYYY-MM-DD format)
    let formattedDueDate = ''
    if (props.task.due_date) {
      const date = new Date(props.task.due_date)
      if (!isNaN(date.getTime())) {
        formattedDueDate = date.toISOString().split('T')[0]
      }
    }
    
    // Reset form with all values at once, including description
    resetForm({
      values: {
        title: props.task.title || '',
        description: props.task.description || '',
        status: props.task.status || 'todo',
        priority: props.task.priority || 'medium',
        story_points: props.task.story_points || 0,
        assignee_id: assigneeId,
        due_date: formattedDueDate,
        sprint_id: sprintId,
        project_id: projectId
      }
    })
  } else {
    // Create mode - reset to defaults
    resetForm({
      values: {
        title: '',
        description: '',
        status: 'todo',
        priority: 'medium',
        story_points: 0,
        assignee_id: '',
        due_date: '',
        sprint_id: '',
        project_id: props.projectId
      }
    })
  }
}

const onSubmit = handleSubmit((formValues) => {
  const formData = { ...formValues }
  
  // Clean up empty string values that should be null or undefined
  if (formData.assignee_id === '') {
    delete formData.assignee_id
  }
  if (formData.due_date === '') {
    delete formData.due_date
  }
  if (formData.sprint_id === '') {
    delete formData.sprint_id
  }
  
  emit('save', formData as TaskForm)
})

// Expose loading state and error handling for parent component
function handleServerError(serverErrors: Record<string, string[]>) {
  const formattedErrors: Record<string, string> = {}
  Object.entries(serverErrors).forEach(([field, messages]) => {
    if (messages && messages.length > 0) {
      formattedErrors[field] = messages[0]
    }
  })
  setErrors(formattedErrors)
  loading.value = false
}

defineExpose({
  loading,
  handleServerError
})
</script>
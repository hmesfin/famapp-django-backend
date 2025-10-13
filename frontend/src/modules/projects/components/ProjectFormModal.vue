<template>
  <BaseModal
    :show="show"
    :title="project ? 'Edit Project' : 'New Project'"
    size="lg"
    @close="$emit('close')"
  >
    <form @submit.prevent="onSubmit">
      <!-- Header icon and description -->
      <div class="sm:flex sm:items-start mb-6">
        <div class="mx-auto flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 sm:mx-0 sm:h-12 sm:w-12">
          <FolderIcon class="h-7 w-7 text-primary-600" />
        </div>
        <div class="mt-4 text-center sm:ml-5 sm:mt-0 sm:text-left w-full">
          <p class="text-sm text-secondary-500 dark:text-secondary-400">
            {{
              project
                ? 'Update your project details below'
                : 'Fill in the details to create a new project'
            }}
          </p>
        </div>
      </div>

      <div class="space-y-5">
        <!-- Name -->
        <BaseInput
          v-model="name"
          label="Project Name"
          placeholder="My Awesome Project"
          :error="nameError"
          required
        />

        <!-- Description -->
        <BaseInput
          v-model="description"
          label="Description"
          type="textarea"
          rows="4"
          placeholder="What's this project about?"
          :error="descriptionError"
          required
        />

        <!-- Status -->
        <BaseSelect
          v-model="status"
          label="Status"
          :options="statusOptions"
          :error="statusError"
        />

        <!-- Dates -->
        <div class="grid grid-cols-2 gap-4">
          <BaseInput
            v-model="startDate"
            label="Start Date"
            type="date"
            :error="startDateError"
            required
          />
          <BaseInput
            v-model="endDate"
            label="End Date"
            type="date"
            :error="endDateError"
          />
        </div>
      </div>

    </form>
    
    <template #footer>
      <BaseButton
        variant="secondary"
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
        Save Project
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useField, useForm } from 'vee-validate'
import { FolderIcon } from '@heroicons/vue/24/outline'
import BaseModal from '@/shared/components/BaseModal.vue'
import BaseInput from '@/shared/components/BaseInput.vue'
import BaseSelect from '@/shared/components/BaseSelect.vue'
import BaseButton from '@/shared/components/BaseButton.vue'
import type { Project, ProjectForm } from '../types/project.types'
import { projectValidationSchema } from '@/utils/veeValidate'

interface Props {
  show: boolean
  project?: Project
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  save: [data: ProjectForm]
}>()

const loading = ref(false)

// Status options for select component
const statusOptions = [
  { value: 'planning', label: 'Planning' },
  { value: 'active', label: 'Active' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' }
]

// VeeValidate form setup
const { handleSubmit, errors, setFieldValue, setErrors, resetForm } = useForm({
  validationSchema: projectValidationSchema,
  initialValues: {
    name: '',
    description: '',
    status: 'planning',
    start_date: new Date().toISOString().split('T')[0],
    end_date: undefined,
  } as ProjectForm,
})

// Individual field composables for better UX
const { value: name, errorMessage: nameError } = useField<string>('name')
const { value: description, errorMessage: descriptionError } = useField<string>('description')
const { value: status, errorMessage: statusError } = useField<string>('status')
const { value: startDate, errorMessage: startDateError } = useField<string>('start_date')
const { value: endDate, errorMessage: endDateError } = useField<string>('end_date')

// Watch for project prop changes to populate form
watch(
  () => props.project,
  (project) => {
    if (project) {
      setFieldValue('name', project.name)
      setFieldValue('description', project.description)
      setFieldValue('status', project.status)
      setFieldValue('start_date', project.start_date)
      setFieldValue('end_date', project.end_date)
    }
  },
  { immediate: true },
)

// Reset form when modal closes/opens
watch(
  () => props.show,
  (isShowing) => {
    if (!isShowing && !props.project) {
      // Reset form for new projects
      resetForm({
        values: {
          name: '',
          description: '',
          status: 'planning',
          start_date: new Date().toISOString().split('T')[0],
          end_date: undefined,
        },
      })
      loading.value = false
    }
  },
)

const onSubmit = handleSubmit((formValues) => {
  loading.value = true
  emit('save', formValues as ProjectForm)
  // Note: Parent component handles success/error and controls loading state
})

// Method to handle server errors (called by parent)
function handleServerError(serverErrors: Record<string, string | string[]>) {
  loading.value = false

  const formattedErrors: Record<string, string> = {}

  Object.entries(serverErrors).forEach(([field, message]) => {
    if (Array.isArray(message)) {
      formattedErrors[field] = message[0]
    } else {
      formattedErrors[field] = message
    }
  })

  // Handle Django's non_field_errors as name errors (usually unique constraint)
  if (
    formattedErrors.non_field_errors &&
    formattedErrors.non_field_errors.toLowerCase().includes('project')
  ) {
    formattedErrors.name = formattedErrors.non_field_errors
    delete formattedErrors.non_field_errors
  }

  setErrors(formattedErrors)
}

// Expose method to parent
defineExpose({
  handleServerError,
})
</script>

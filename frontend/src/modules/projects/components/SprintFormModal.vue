<template>
  <TransitionRoot as="template" :show="show">
    <Dialog as="div" class="relative z-50" @close="handleClose">
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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
              <Form @submit="onSubmit" :validation-schema="validationSchema">
                <div class="bg-white dark:bg-gray-800 px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                  <div class="sm:flex sm:items-start">
                    <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/50 sm:mx-0 sm:h-10 sm:w-10">
                      <CalendarDaysIcon class="h-6 w-6 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
                    </div>
                    <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                      <DialogTitle as="h3" class="text-lg font-semibold leading-6 text-gray-900 dark:text-gray-100">
                        {{ isEditMode ? 'Edit Sprint' : 'Create New Sprint' }}
                      </DialogTitle>
                      
                      <div class="mt-4 space-y-4">
                        <!-- Sprint Name -->
                        <Field name="name" v-model="formData.name" v-slot="{ field, errors, value }">
                          <div>
                            <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                              Sprint Name <span class="text-red-500">*</span>
                            </label>
                            <input
                              v-bind="field"
                              :value="value"
                              type="text"
                              id="name"
                              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-gray-100 px-3 py-2"
                              :class="{ 'border-red-500': errors.length }"
                              placeholder="Sprint 1"
                            />
                            <ErrorMessage name="name" class="mt-1 text-sm text-red-600 dark:text-red-400" />
                          </div>
                        </Field>

                        <!-- Sprint Goal -->
                        <Field name="goal" v-model="formData.goal" v-slot="{ field, errors, value }">
                          <div>
                            <label for="goal" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                              Sprint Goal <span class="text-red-500">*</span>
                            </label>
                            <textarea
                              v-bind="field"
                              :value="value"
                              id="goal"
                              rows="3"
                              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-gray-100 px-3 py-2"
                              :class="{ 'border-red-500': errors.length }"
                              placeholder="Complete user authentication and profile features"
                            />
                            <ErrorMessage name="goal" class="mt-1 text-sm text-red-600 dark:text-red-400" />
                          </div>
                        </Field>

                        <!-- Date Range -->
                        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                          <!-- Start Date -->
                          <Field name="start_date" v-model="formData.start_date" v-slot="{ field, errors, value }">
                            <div>
                              <label for="start_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Start Date <span class="text-red-500">*</span>
                              </label>
                              <input
                                v-bind="field"
                                :value="value"
                                type="date"
                                id="start_date"
                                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-gray-100 px-3 py-2"
                                :class="{ 'border-red-500': errors.length }"
                              />
                              <ErrorMessage name="start_date" class="mt-1 text-sm text-red-600 dark:text-red-400" />
                            </div>
                          </Field>

                          <!-- End Date -->
                          <Field name="end_date" v-model="formData.end_date" v-slot="{ field, errors, value }">
                            <div>
                              <label for="end_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                End Date <span class="text-red-500">*</span>
                              </label>
                              <input
                                v-bind="field"
                                :value="value"
                                type="date"
                                id="end_date"
                                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-gray-100 px-3 py-2"
                                :class="{ 'border-red-500': errors.length }"
                              />
                              <ErrorMessage name="end_date" class="mt-1 text-sm text-red-600 dark:text-red-400" />
                            </div>
                          </Field>
                        </div>

                        <!-- Active Sprint Toggle -->
                        <Field name="is_active" v-model="formData.is_active" type="checkbox" v-slot="{ field, value }">
                          <div class="flex items-center">
                            <input
                              v-bind="field"
                              :checked="value"
                              type="checkbox"
                              id="is_active"
                              class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700"
                            />
                            <label for="is_active" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                              Set as active sprint
                              <span class="block text-xs text-gray-500 dark:text-gray-400">
                                Only one sprint can be active at a time
                              </span>
                            </label>
                          </div>
                        </Field>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                  <button
                    type="submit"
                    :disabled="isSubmitting"
                    class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span v-if="isSubmitting" class="flex items-center">
                      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    </span>
                    <span v-else>{{ isEditMode ? 'Update Sprint' : 'Create Sprint' }}</span>
                  </button>
                  <button
                    type="button"
                    @click.prevent="handleClose"
                    :disabled="isSubmitting"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white dark:bg-gray-600 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-500 hover:bg-gray-50 dark:hover:bg-gray-500 sm:mt-0 sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              </Form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, watch, ref, nextTick } from 'vue'
import { Form, Field, ErrorMessage, useForm } from 'vee-validate'
import * as yup from 'yup'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { CalendarDaysIcon } from '@heroicons/vue/24/outline'
import type { Sprint, SprintForm } from '../types/project.types'

interface Props {
  show: boolean
  sprint?: Sprint | null
  projectId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  save: [data: SprintForm]
}>()

const isEditMode = computed(() => !!props.sprint)
const isSubmitting = ref(false)

// Form data reactive ref
const formData = ref({
  name: '',
  goal: '',
  start_date: '',
  end_date: '',
  is_active: false
})

// Form validation schema
const validationSchema = yup.object({
  name: yup.string()
    .required('Sprint name is required')
    .min(3, 'Sprint name must be at least 3 characters')
    .max(100, 'Sprint name must be less than 100 characters'),
  goal: yup.string()
    .required('Sprint goal is required')
    .min(10, 'Sprint goal must be at least 10 characters')
    .max(500, 'Sprint goal must be less than 500 characters'),
  start_date: yup.date()
    .required('Start date is required')
    .typeError('Invalid date format'),
  end_date: yup.date()
    .required('End date is required')
    .min(yup.ref('start_date'), 'End date must be after start date')
    .typeError('Invalid date format'),
  is_active: yup.boolean()
})

// Initialize form with default values
const getInitialValues = () => {
  if (props.sprint) {
    // Edit mode - use sprint data
    const startDate = props.sprint.start_date ? 
      new Date(props.sprint.start_date).toISOString().split('T')[0] : ''
    const endDate = props.sprint.end_date ? 
      new Date(props.sprint.end_date).toISOString().split('T')[0] : ''
    
    return {
      name: props.sprint.name || '',
      goal: props.sprint.goal || '',
      start_date: startDate,
      end_date: endDate,
      is_active: props.sprint.is_active || false
    }
  } else {
    // New sprint - default values
    const today = new Date()
    const twoWeeksLater = new Date()
    twoWeeksLater.setDate(today.getDate() + 14)
    
    return {
      name: '',
      goal: '',
      start_date: today.toISOString().split('T')[0],
      end_date: twoWeeksLater.toISOString().split('T')[0],
      is_active: false
    }
  }
}

const { resetForm, handleSubmit, setValues } = useForm({
  validationSchema,
  initialValues: getInitialValues()
})

// Reset form when modal opens
watch(
  () => props.show,
  async (newValue, oldValue) => {
    // Only set values when opening the modal, not when closing
    if (newValue && !oldValue) {
      await nextTick()
      
      if (props.sprint) {
        // Edit mode - populate with existing sprint data
        const startDate = props.sprint.start_date ? 
          new Date(props.sprint.start_date).toISOString().split('T')[0] : ''
        const endDate = props.sprint.end_date ? 
          new Date(props.sprint.end_date).toISOString().split('T')[0] : ''
        
        // Set both formData and form values
        formData.value = {
          name: props.sprint.name || '',
          goal: props.sprint.goal || '',
          start_date: startDate,
          end_date: endDate,
          is_active: props.sprint.is_active || false
        }
        
        // Also set VeeValidate values
        setValues(formData.value)
      } else {
        // New sprint - set default dates
        const today = new Date()
        const twoWeeksLater = new Date()
        twoWeeksLater.setDate(today.getDate() + 14)
        
        formData.value = {
          name: '',
          goal: '',
          start_date: today.toISOString().split('T')[0],
          end_date: twoWeeksLater.toISOString().split('T')[0],
          is_active: false
        }
        
        resetForm({
          values: formData.value
        })
      }
    }
  }
)

// Clean up form after modal has fully closed
watch(
  () => props.show,
  (newValue) => {
    if (!newValue) {
      // Delay cleanup to allow modal transition to complete
      setTimeout(() => {
        resetForm()
        formData.value = {
          name: '',
          goal: '',
          start_date: '',
          end_date: '',
          is_active: false
        }
      }, 300) // Match the modal transition duration
    }
  }
)

const onSubmit = handleSubmit(async (values) => {
  isSubmitting.value = true
  try {
    const data: SprintForm = {
      project_id: props.projectId,
      name: values.name,
      goal: values.goal,
      start_date: values.start_date,
      end_date: values.end_date,
      is_active: values.is_active || false
    }
    
    emit('save', data)
  } finally {
    isSubmitting.value = false
  }
})

function handleClose() {
  if (!isSubmitting.value) {
    emit('close')
  }
}
</script>
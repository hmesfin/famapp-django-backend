<template>
  <BaseModal 
    :show="isOpen" 
    :title="title"
    size="sm"
    :show-close-button="false"
    :close-on-overlay-click="!loading && !persistent"
    :persistent="persistent || loading"
    @close="handleCancel"
  >
    <!-- Icon and message content -->
    <div class="flex items-start space-x-4">
      <div v-if="type !== 'basic'" class="flex-shrink-0">
        <div :class="iconContainerClasses">
          <!-- Warning icon -->
          <ExclamationTriangleIcon v-if="type === 'warning'" :class="iconClasses" />
          
          <!-- Danger icon -->
          <ExclamationCircleIcon v-else-if="type === 'danger'" :class="iconClasses" />
          
          <!-- Success icon -->
          <CheckCircleIcon v-else-if="type === 'success'" :class="iconClasses" />
          
          <!-- Info icon -->
          <InformationCircleIcon v-else-if="type === 'info'" :class="iconClasses" />
          
          <!-- Delete/Trash icon -->
          <TrashIcon v-else-if="type === 'delete'" :class="iconClasses" />
        </div>
      </div>
      
      <!-- Message content -->
      <div class="flex-1">
        <p :class="messageClasses">{{ message }}</p>
        <p v-if="description" :class="descriptionClasses">{{ description }}</p>
      </div>
    </div>

    <!-- Action buttons -->
    <template #footer>
      <BaseButton
        :variant="cancelVariant"
        :size="buttonSize"
        :disabled="loading"
        @click="handleCancel"
      >
        {{ cancelText }}
      </BaseButton>
      <BaseButton
        :variant="confirmVariant"
        :size="buttonSize"
        :loading="loading"
        :loading-text="loadingText"
        @click="handleConfirm"
      >
        {{ confirmText }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'
import BaseButton from './BaseButton.vue'
import {
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

export type ConfirmType = 'basic' | 'warning' | 'danger' | 'success' | 'info' | 'delete'
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'ghost' | 'outline'

interface Props {
  isOpen: boolean
  title?: string
  message: string
  description?: string
  type?: ConfirmType
  confirmText?: string
  cancelText?: string
  loading?: boolean
  loadingText?: string
  persistent?: boolean
  buttonSize?: ButtonSize
}

const props = withDefaults(defineProps<Props>(), {
  type: 'basic',
  title: 'Confirm Action',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loading: false,
  persistent: false,
  buttonSize: 'md'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

// Icon styling based on type
const iconContainerClasses = computed(() => {
  const baseClasses = [
    'flex',
    'h-12',
    'w-12',
    'flex-shrink-0',
    'items-center',
    'justify-center',
    'rounded-full'
  ]

  const typeClasses = {
    basic: [],
    warning: [
      'bg-warning-100',
      'dark:bg-warning-900',
      'dark:bg-opacity-20'
    ],
    danger: [
      'bg-danger-100',
      'dark:bg-danger-900',
      'dark:bg-opacity-20'
    ],
    success: [
      'bg-success-100',
      'dark:bg-success-900',
      'dark:bg-opacity-20'
    ],
    info: [
      'bg-info-100',
      'dark:bg-info-900',
      'dark:bg-opacity-20'
    ],
    delete: [
      'bg-danger-100',
      'dark:bg-danger-900',
      'dark:bg-opacity-20'
    ]
  }

  return [
    ...baseClasses,
    ...typeClasses[props.type]
  ]
})

const iconClasses = computed(() => {
  const baseClasses = [
    'h-6',
    'w-6'
  ]

  const typeClasses = {
    basic: [
      'text-secondary-600',
      'dark:text-secondary-400'
    ],
    warning: [
      'text-warning-600',
      'dark:text-warning-400'
    ],
    danger: [
      'text-danger-600',
      'dark:text-danger-400'
    ],
    success: [
      'text-success-600',
      'dark:text-success-400'
    ],
    info: [
      'text-info-600',
      'dark:text-info-400'
    ],
    delete: [
      'text-danger-600',
      'dark:text-danger-400'
    ]
  }

  return [
    ...baseClasses,
    ...typeClasses[props.type]
  ]
})

// Message styling
const messageClasses = [
  'text-sm',
  'font-medium',
  'text-secondary-900',
  'dark:text-secondary-100'
]

const descriptionClasses = [
  'mt-2',
  'text-sm',
  'text-secondary-600',
  'dark:text-secondary-400'
]

// Button variants based on type
const confirmVariant = computed((): ButtonVariant => {
  const variantMap: Record<ConfirmType, ButtonVariant> = {
    basic: 'primary',
    warning: 'warning',
    danger: 'danger',
    success: 'success',
    info: 'info',
    delete: 'danger'
  }
  return variantMap[props.type]
})

const cancelVariant: ButtonVariant = 'outline'

// Handlers
const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
  }
}
</script>
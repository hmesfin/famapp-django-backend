<template>
  <div :class="containerClasses">
    <div class="relative flex items-start">
      <div class="flex items-center h-5">
        <input
          :id="checkboxId"
          ref="checkboxRef"
          type="checkbox"
          :checked="isChecked"
          :value="value"
          :disabled="disabled"
          :required="required"
          :aria-describedby="ariaDescribedby"
          :aria-invalid="hasError"
          :class="checkboxClasses"
          v-bind="$attrs"
          @change="handleChange"
          @blur="handleBlur"
          @focus="handleFocus"
        />
      </div>
      <div v-if="label || description || $slots.default" class="ml-3 text-sm">
        <label v-if="label" :for="checkboxId" :class="labelClasses">
          {{ label }}
          <span v-if="required" class="text-danger-500 ml-1" aria-label="required">*</span>
        </label>
        <div v-if="$slots.default" :class="labelClasses">
          <slot />
        </div>
        <p v-if="description" :class="descriptionClasses">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- Error Message -->
    <p
      v-if="hasError"
      :id="`${checkboxId}-error`"
      :class="errorTextClasses"
      role="alert"
    >
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

type CheckboxSize = 'sm' | 'md' | 'lg'
type CheckboxVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger'

interface Props {
  // v-model
  modelValue?: boolean | string[] | number[]
  
  // Checkbox attributes
  value?: string | number
  disabled?: boolean
  required?: boolean
  
  // Styling
  size?: CheckboxSize
  variant?: CheckboxVariant
  
  // Content
  label?: string
  description?: string
  
  // Validation
  error?: boolean
  errorMessage?: string
  
  // Accessibility
  ariaLabel?: string
  ariaDescribedby?: string
  
  // ID
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'default',
  disabled: false,
  required: false,
  error: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean | string[] | number[]]
  change: [event: Event]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

// Refs
const checkboxRef = ref<HTMLInputElement>()
const isFocused = ref(false)

// Computed ID
const checkboxId = computed(() => props.id || `checkbox-${Math.random().toString(36).substr(2, 9)}`)

// Error state
const hasError = computed(() => props.error || !!props.errorMessage)

// Check if checkbox is checked
const isChecked = computed(() => {
  if (typeof props.modelValue === 'boolean') {
    return props.modelValue
  }
  
  if (Array.isArray(props.modelValue) && props.value !== undefined) {
    return props.modelValue.includes(props.value)
  }
  
  return false
})

// ARIA describedby
const ariaDescribedby = computed(() => {
  const ids = []
  if (hasError.value) ids.push(`${checkboxId.value}-error`)
  if (props.ariaDescribedby) ids.push(props.ariaDescribedby)
  return ids.length > 0 ? ids.join(' ') : undefined
})

// Size configurations
const sizeConfigs = {
  sm: {
    checkbox: 'h-3 w-3',
    label: 'text-sm',
    description: 'text-xs'
  },
  md: {
    checkbox: 'h-4 w-4',
    label: 'text-sm',
    description: 'text-sm'
  },
  lg: {
    checkbox: 'h-5 w-5',
    label: 'text-base',
    description: 'text-sm'
  }
}

// Variant classes
const variantClasses = {
  default: {
    checkbox: [
      'text-primary-600',
      'focus:ring-primary-500',
      'border-secondary-300',
      'dark:border-secondary-600',
      'dark:bg-secondary-800'
    ]
  },
  primary: {
    checkbox: [
      'text-primary-600',
      'focus:ring-primary-500',
      'border-primary-300',
      'dark:border-primary-600'
    ]
  },
  success: {
    checkbox: [
      'text-success-600',
      'focus:ring-success-500',
      'border-success-300',
      'dark:border-success-600'
    ]
  },
  warning: {
    checkbox: [
      'text-warning-600',
      'focus:ring-warning-500',
      'border-warning-300',
      'dark:border-warning-600'
    ]
  },
  danger: {
    checkbox: [
      'text-danger-600',
      'focus:ring-danger-500',
      'border-danger-300',
      'dark:border-danger-600'
    ]
  }
}

// Base checkbox classes
const baseCheckboxClasses = [
  'rounded',
  'transition-all',
  'duration-200',
  'ease-smooth',
  'focus:ring-2',
  'focus:ring-offset-2',
  'disabled:opacity-50',
  'disabled:cursor-not-allowed'
]

// Error state checkbox classes
const errorCheckboxClasses = [
  'border-danger-300',
  'text-danger-600',
  'focus:ring-danger-500',
  'dark:border-danger-600'
]

// Container classes
const containerClasses = ['space-y-1']

// Checkbox classes
const checkboxClasses = computed(() => [
  ...baseCheckboxClasses,
  sizeConfigs[props.size].checkbox,
  ...(hasError.value ? errorCheckboxClasses : variantClasses[props.variant].checkbox)
])

// Label classes
const labelClasses = computed(() => [
  'font-medium',
  'cursor-pointer',
  sizeConfigs[props.size].label,
  'text-secondary-900',
  'dark:text-secondary-100',
  {
    'text-secondary-500 cursor-not-allowed dark:text-secondary-600': props.disabled
  }
])

// Description classes
const descriptionClasses = computed(() => [
  'mt-1',
  sizeConfigs[props.size].description,
  'text-secondary-600',
  'dark:text-secondary-400',
  {
    'text-secondary-500 dark:text-secondary-600': props.disabled
  }
])

// Error text classes
const errorTextClasses = [
  'mt-2',
  'text-sm',
  'text-danger-600',
  'dark:text-danger-400'
]

// Methods
const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  
  if (typeof props.modelValue === 'boolean') {
    emit('update:modelValue', target.checked)
  } else if (Array.isArray(props.modelValue) && props.value !== undefined) {
    const newValue = [...props.modelValue]
    
    if (target.checked) {
      if (!newValue.includes(props.value)) {
        newValue.push(props.value)
      }
    } else {
      const index = newValue.indexOf(props.value)
      if (index > -1) {
        newValue.splice(index, 1)
      }
    }
    
    emit('update:modelValue', newValue)
  }
  
  emit('change', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

// Focus method for external use
const focus = () => {
  checkboxRef.value?.focus()
}

// Expose focus method
defineExpose({
  focus,
  checkboxRef
})
</script>
<template>
  <div :class="containerClasses">
    <!-- Label -->
    <label
      v-if="label"
      :for="selectId"
      :class="labelClasses"
    >
      {{ label }}
      <span v-if="required" class="text-danger-500 ml-1" aria-label="required">*</span>
    </label>

    <!-- Select Container -->
    <div class="relative">
      <!-- Leading Icon -->
      <div v-if="leadingIcon" :class="leadingIconClasses">
        <component :is="leadingIcon" :class="iconSizeClasses" />
      </div>

      <!-- Select Field -->
      <select
        :id="selectId"
        ref="selectRef"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :aria-describedby="ariaDescribedby"
        :aria-invalid="hasError"
        :class="selectClasses"
        v-bind="$attrs"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
      >
        <option v-if="placeholder" value="" disabled>
          {{ placeholder }}
        </option>
        <option
          v-for="option in normalizedOptions"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>

      <!-- Chevron Icon -->
      <div :class="chevronClasses">
        <ChevronUpDownIcon :class="iconSizeClasses" />
      </div>
    </div>

    <!-- Help Text -->
    <p
      v-if="helpText && !hasError"
      :id="`${selectId}-help`"
      :class="helpTextClasses"
    >
      {{ helpText }}
    </p>

    <!-- Error Message -->
    <p
      v-if="hasError"
      :id="`${selectId}-error`"
      :class="errorTextClasses"
      role="alert"
    >
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronUpDownIcon } from '@heroicons/vue/24/outline'
import type { Component } from 'vue'

type SelectSize = 'sm' | 'md' | 'lg'

interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

interface Props {
  // v-model
  modelValue?: string | number
  
  // Options
  options?: SelectOption[] | string[] | number[]
  
  // Input attributes
  placeholder?: string
  disabled?: boolean
  required?: boolean
  multiple?: boolean
  
  // Styling
  size?: SelectSize
  
  // Label and help
  label?: string
  helpText?: string
  
  // Validation
  error?: boolean
  errorMessage?: string
  
  // Icons
  leadingIcon?: Component
  
  // Accessibility
  ariaLabel?: string
  ariaDescribedby?: string
  
  // ID
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  error: false,
  disabled: false,
  required: false,
  multiple: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | string[] | number[]]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  change: [event: Event]
}>()

// Refs
const selectRef = ref<HTMLSelectElement>()
const isFocused = ref(false)

// Computed ID
const selectId = computed(() => props.id || `select-${Math.random().toString(36).substr(2, 9)}`)

// Error state
const hasError = computed(() => props.error || !!props.errorMessage)

// Normalize options
const normalizedOptions = computed(() => {
  if (!props.options) return []
  
  return props.options.map(option => {
    if (typeof option === 'object' && option !== null) {
      return option as SelectOption
    }
    return {
      label: String(option),
      value: option,
      disabled: false
    }
  })
})

// ARIA describedby
const ariaDescribedby = computed(() => {
  const ids = []
  if (props.helpText && !hasError.value) ids.push(`${selectId.value}-help`)
  if (hasError.value) ids.push(`${selectId.value}-error`)
  if (props.ariaDescribedby) ids.push(props.ariaDescribedby)
  return ids.length > 0 ? ids.join(' ') : undefined
})

// Size-based classes
const sizeClasses = {
  sm: {
    select: 'px-3 py-2 text-sm min-h-[32px]',
    withLeading: 'pl-9',
    icon: 'h-4 w-4',
    iconContainer: 'left-0 pl-3',
    chevronContainer: 'right-0 pr-2'
  },
  md: {
    select: 'px-4 py-2.5 text-sm min-h-[40px]',
    withLeading: 'pl-11',
    icon: 'h-5 w-5',
    iconContainer: 'left-0 pl-3',
    chevronContainer: 'right-0 pr-3'
  },
  lg: {
    select: 'px-4 py-3 text-base min-h-[44px]',
    withLeading: 'pl-12',
    icon: 'h-5 w-5',
    iconContainer: 'left-0 pl-4',
    chevronContainer: 'right-0 pr-4'
  }
}

// Base select classes
const baseSelectClasses = [
  'block',
  'w-full',
  'border',
  'rounded-md',
  'transition-all',
  'duration-200',
  'ease-smooth',
  'bg-white',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-offset-0',
  'disabled:bg-secondary-50',
  'disabled:text-secondary-500',
  'disabled:cursor-not-allowed',
  'disabled:border-secondary-200',
  'dark:bg-secondary-800',
  'dark:border-secondary-600',
  'dark:text-secondary-100',
  'dark:disabled:bg-secondary-900',
  'dark:disabled:border-secondary-700',
  'appearance-none'
]

// State-based select classes
const stateSelectClasses = computed(() => {
  if (hasError.value) {
    return [
      'border-danger-300',
      'text-danger-900',
      'focus:ring-danger-500',
      'focus:border-danger-500',
      'dark:border-danger-600',
      'dark:text-danger-100'
    ]
  }
  
  if (isFocused.value) {
    return [
      'border-primary-300',
      'ring-2',
      'ring-primary-500',
      'ring-opacity-20'
    ]
  }
  
  return [
    'border-secondary-300',
    'focus:ring-primary-500',
    'focus:border-primary-500',
    'hover:border-secondary-400',
    'dark:border-secondary-600',
    'dark:hover:border-secondary-500'
  ]
})

// Container classes
const containerClasses = ['space-y-1']

// Label classes
const labelClasses = [
  'block',
  'text-sm',
  'font-medium',
  'text-secondary-700',
  'dark:text-secondary-300'
]

// Select classes
const selectClasses = computed(() => [
  ...baseSelectClasses,
  ...stateSelectClasses.value,
  sizeClasses[props.size].select,
  {
    [sizeClasses[props.size].withLeading]: props.leadingIcon,
    'pr-10': true // Always make room for chevron
  }
])

// Icon classes
const iconSizeClasses = computed(() => sizeClasses[props.size].icon)

const leadingIconClasses = [
  'absolute',
  'inset-y-0',
  'left-0',
  'flex',
  'items-center',
  'pl-3',
  'text-secondary-400',
  'dark:text-secondary-500'
]

const chevronClasses = [
  'absolute',
  'inset-y-0',
  'right-0',
  'flex',
  'items-center',
  'pr-3',
  'text-secondary-400',
  'pointer-events-none',
  'dark:text-secondary-500'
]

// Help text classes
const helpTextClasses = [
  'text-sm',
  'text-secondary-600',
  'dark:text-secondary-400'
]

// Error text classes
const errorTextClasses = [
  'text-sm',
  'text-danger-600',
  'dark:text-danger-400'
]

// Methods
const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  let value: string | number | string[] | number[] = target.value
  
  if (props.multiple) {
    value = Array.from(target.selectedOptions).map(option => option.value)
  }
  
  emit('update:modelValue', value)
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
  selectRef.value?.focus()
}

// Expose focus method
defineExpose({
  focus,
  selectRef
})
</script>
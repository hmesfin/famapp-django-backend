<template>
  <div :class="containerClasses">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      :class="labelClasses"
    >
      {{ label }}
      <span v-if="required" class="text-danger-500 ml-1" aria-label="required">*</span>
    </label>

    <!-- Input Container -->
    <div class="relative">
      <!-- Leading Icon -->
      <div v-if="leadingIcon" :class="leadingIconClasses">
        <component :is="leadingIcon" :class="iconSizeClasses" />
      </div>

      <!-- Input Field -->
      <component
        :is="inputComponent"
        :id="inputId"
        ref="inputRef"
        :value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :aria-describedby="ariaDescribedby"
        :aria-invalid="hasError"
        :class="inputClasses"
        :rows="type === 'textarea' ? rows : undefined"
        :maxlength="maxlength"
        :minlength="minlength"
        :min="min"
        :max="max"
        :step="step"
        v-bind="$attrs"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />

      <!-- Trailing Icon -->
      <div v-if="trailingIcon || showPasswordToggle" :class="trailingIconClasses">
        <!-- Password Toggle -->
        <button
          v-if="showPasswordToggle"
          type="button"
          :class="passwordToggleClasses"
          @click="togglePasswordVisibility"
          :aria-label="isPasswordVisible ? 'Hide password' : 'Show password'"
        >
          <EyeIcon v-if="!isPasswordVisible" :class="iconSizeClasses" />
          <EyeSlashIcon v-else :class="iconSizeClasses" />
        </button>
        
        <!-- Custom Trailing Icon -->
        <component
          v-else-if="trailingIcon"
          :is="trailingIcon"
          :class="iconSizeClasses"
        />
      </div>

      <!-- Clear Button -->
      <button
        v-if="clearable && modelValue && !disabled && !readonly"
        type="button"
        :class="clearButtonClasses"
        @click="clearInput"
        aria-label="Clear input"
      >
        <XMarkIcon :class="iconSizeClasses" />
      </button>
    </div>

    <!-- Help Text -->
    <p
      v-if="helpText && !hasError"
      :id="`${inputId}-help`"
      :class="helpTextClasses"
    >
      {{ helpText }}
    </p>

    <!-- Error Message -->
    <p
      v-if="hasError"
      :id="`${inputId}-error`"
      :class="errorTextClasses"
      role="alert"
    >
      {{ errorMessage }}
    </p>

    <!-- Character Count -->
    <p
      v-if="showCharacterCount && maxlength"
      :class="characterCountClasses"
    >
      {{ characterCount }}/{{ maxlength }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
import { EyeIcon, EyeSlashIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import type { Component } from 'vue'

type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'textarea'
type InputSize = 'sm' | 'md' | 'lg'

interface Props {
  // v-model
  modelValue?: string | number
  
  // Input attributes
  type?: InputType
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  autocomplete?: string
  maxlength?: number
  minlength?: number
  min?: number | string
  max?: number | string
  step?: number | string
  
  // Textarea specific
  rows?: number
  
  // Styling
  size?: InputSize
  
  // Label and help
  label?: string
  helpText?: string
  
  // Validation
  error?: boolean
  errorMessage?: string
  
  // Icons
  leadingIcon?: Component
  trailingIcon?: Component
  
  // Features
  clearable?: boolean
  showCharacterCount?: boolean
  
  // Accessibility
  ariaLabel?: string
  ariaDescribedby?: string
  
  // ID
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
  error: false,
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  showCharacterCount: false,
  rows: 3
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  keydown: [event: KeyboardEvent]
  clear: []
}>()

// Refs
const inputRef = ref<HTMLInputElement | HTMLTextAreaElement>()
const isPasswordVisible = ref(false)
const isFocused = ref(false)

// Computed ID
const inputId = computed(() => props.id || `input-${Math.random().toString(36).substr(2, 9)}`)

// Input component type
const inputComponent = computed(() => props.type === 'textarea' ? 'textarea' : 'input')

// Password toggle
const showPasswordToggle = computed(() => props.type === 'password')

// Actual input type (for password toggle)
const actualType = computed(() => {
  if (props.type === 'password') {
    return isPasswordVisible.value ? 'text' : 'password'
  }
  return props.type === 'textarea' ? undefined : props.type
})

// Error state
const hasError = computed(() => props.error || !!props.errorMessage)

// Character count
const characterCount = computed(() => {
  if (typeof props.modelValue === 'string') {
    return props.modelValue.length
  }
  return 0
})

// ARIA describedby
const ariaDescribedby = computed(() => {
  const ids = []
  if (props.helpText && !hasError.value) ids.push(`${inputId.value}-help`)
  if (hasError.value) ids.push(`${inputId.value}-error`)
  if (props.ariaDescribedby) ids.push(props.ariaDescribedby)
  return ids.length > 0 ? ids.join(' ') : undefined
})

// Size-based classes
const sizeClasses = {
  sm: {
    input: 'px-3 py-2 text-sm min-h-[32px]',
    textarea: 'px-3 py-2 text-sm',
    withLeading: 'pl-9',
    withTrailing: 'pr-9',
    icon: 'h-4 w-4',
    iconContainer: 'left-0 pl-3',
    trailingContainer: 'right-0 pr-3'
  },
  md: {
    input: 'px-4 py-2.5 text-sm min-h-[40px]',
    textarea: 'px-4 py-2.5 text-sm',
    withLeading: 'pl-11',
    withTrailing: 'pr-11',
    icon: 'h-5 w-5',
    iconContainer: 'left-0 pl-3',
    trailingContainer: 'right-0 pr-3'
  },
  lg: {
    input: 'px-4 py-3 text-base min-h-[44px]',
    textarea: 'px-4 py-3 text-base',
    withLeading: 'pl-12',
    withTrailing: 'pr-12',
    icon: 'h-5 w-5',
    iconContainer: 'left-0 pl-4',
    trailingContainer: 'right-0 pr-4'
  }
}

// Base input classes
const baseInputClasses = [
  'block',
  'w-full',
  'border',
  'rounded-md',
  'transition-all',
  'duration-200',
  'ease-smooth',
  'placeholder-secondary-400',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-offset-0',
  'disabled:bg-secondary-50',
  'disabled:text-secondary-500',
  'disabled:cursor-not-allowed',
  'disabled:border-secondary-200',
  'readonly:bg-secondary-50',
  'readonly:cursor-default',
  'dark:bg-secondary-800',
  'dark:border-secondary-600',
  'dark:text-secondary-100',
  'dark:placeholder-secondary-500',
  'dark:disabled:bg-secondary-900',
  'dark:disabled:border-secondary-700',
  'dark:readonly:bg-secondary-900'
]

// State-based input classes
const stateInputClasses = computed(() => {
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

// Input classes
const inputClasses = computed(() => [
  ...baseInputClasses,
  ...stateInputClasses.value,
  sizeClasses[props.size][props.type === 'textarea' ? 'textarea' : 'input'],
  {
    [sizeClasses[props.size].withLeading]: props.leadingIcon,
    [sizeClasses[props.size].withTrailing]: props.trailingIcon || showPasswordToggle.value || props.clearable,
    'form-input': props.type !== 'textarea',
    'form-textarea': props.type === 'textarea'
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

const trailingIconClasses = [
  'absolute',
  'inset-y-0',
  'right-0',
  'flex',
  'items-center',
  'pr-3',
  'text-secondary-400',
  'dark:text-secondary-500'
]

const passwordToggleClasses = [
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-primary-500',
  'focus:ring-offset-2',
  'rounded',
  'p-1',
  'hover:text-secondary-600',
  'dark:hover:text-secondary-300'
]

const clearButtonClasses = [
  'absolute',
  'inset-y-0',
  'right-0',
  'flex',
  'items-center',
  'pr-3',
  'text-secondary-400',
  'hover:text-secondary-600',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-primary-500',
  'focus:ring-offset-2',
  'rounded',
  'p-1',
  'dark:text-secondary-500',
  'dark:hover:text-secondary-300'
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

// Character count classes
const characterCountClasses = computed(() => [
  'text-sm',
  'text-right',
  {
    'text-secondary-600 dark:text-secondary-400': !props.maxlength || characterCount.value <= props.maxlength,
    'text-danger-600 dark:text-danger-400': props.maxlength && characterCount.value > props.maxlength
  }
])

// Methods
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement
  let value: string | number = target.value
  
  if (props.type === 'number' && 'valueAsNumber' in target) {
    value = target.valueAsNumber
  }
  
  emit('update:modelValue', value)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

const clearInput = () => {
  emit('update:modelValue', '')
  emit('clear')
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// Focus method for external use
const focus = () => {
  inputRef.value?.focus()
}

// Expose focus method
defineExpose({
  focus,
  inputRef
})

// Watch for actual type changes (password toggle)
watch(() => actualType.value, (newType) => {
  if (inputRef.value && 'type' in inputRef.value && newType) {
    ;(inputRef.value as HTMLInputElement).type = newType
  }
}, { immediate: true })
</script>
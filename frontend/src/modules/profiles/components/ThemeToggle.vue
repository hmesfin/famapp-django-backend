<template>
  <div :class="containerClasses">
    <!-- Simple Toggle Button -->
    <button
      v-if="variant === 'simple'"
      type="button"
      :class="toggleButtonClasses"
      @click="cycleTheme"
      :aria-label="ariaLabel"
      :title="tooltipText"
    >
      <component 
        :is="currentThemeIcon" 
        :class="iconClasses"
      />
      <span v-if="showLabel" class="ml-2 text-sm font-medium">
        {{ currentThemeLabel }}
      </span>
    </button>

    <!-- Dropdown Menu -->
    <div v-else-if="variant === 'dropdown'" class="relative">
      <button
        type="button"
        :class="dropdownButtonClasses"
        @click="showDropdown = !showDropdown"
        :aria-expanded="showDropdown"
        :aria-haspopup="true"
        :aria-label="ariaLabel"
      >
        <component 
          :is="currentThemeIcon" 
          :class="iconClasses"
        />
        <span v-if="showLabel" class="ml-2 text-sm font-medium">
          {{ currentThemeLabel }}
        </span>
        <ChevronDownIcon 
          v-if="!showLabel"
          class="w-4 h-4 ml-1 opacity-60"
        />
      </button>

      <!-- Dropdown Menu -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showDropdown"
          :class="dropdownMenuClasses"
          role="menu"
        >
          <button
            v-for="option in themeOptions"
            :key="option.value"
            type="button"
            :class="[
              ...dropdownItemClasses,
              {
                'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300': 
                  settingsStore.userSettings?.theme === option.value
              }
            ]"
            @click="selectTheme(option.value)"
            role="menuitem"
          >
            <component 
              :is="option.icon" 
              class="w-4 h-4 mr-3"
            />
            <div class="flex-1 text-left">
              <div class="font-medium">{{ option.label }}</div>
              <div class="text-xs text-secondary-600 dark:text-secondary-400">
                {{ option.description }}
              </div>
            </div>
            <CheckIcon
              v-if="settingsStore.userSettings?.theme === option.value"
              class="w-4 h-4 text-primary-600 dark:text-primary-400"
            />
          </button>
        </div>
      </Transition>
    </div>

    <!-- Radio Group -->
    <fieldset v-else-if="variant === 'radio'" class="space-y-2">
      <legend v-if="showLabel" class="text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-3">
        Theme Preference
      </legend>
      <div class="space-y-2">
        <label
          v-for="option in themeOptions"
          :key="option.value"
          :class="radioOptionClasses"
        >
          <input
            type="radio"
            :name="`theme-${componentId}`"
            :value="option.value"
            :checked="settingsStore.userSettings?.theme === option.value"
            @change="selectTheme(option.value)"
            class="sr-only"
          />
          <div :class="radioIndicatorClasses(option.value)">
            <div :class="radioInnerClasses(option.value)"></div>
          </div>
          <component 
            :is="option.icon" 
            class="w-5 h-5 text-secondary-600 dark:text-secondary-400"
          />
          <div class="flex-1">
            <div class="font-medium text-secondary-900 dark:text-secondary-100">
              {{ option.label }}
            </div>
            <div class="text-sm text-secondary-600 dark:text-secondary-400">
              {{ option.description }}
            </div>
          </div>
        </label>
      </div>
    </fieldset>

    <!-- Loading State -->
    <div 
      v-if="settingsStore.loading" 
      class="flex items-center space-x-2 text-sm text-secondary-600 dark:text-secondary-400"
    >
      <div class="animate-spin rounded-full h-4 w-4 border-2 border-primary-500 border-t-transparent"></div>
      <span>Updating theme...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  SunIcon, 
  MoonIcon, 
  ComputerDesktopIcon,
  ChevronDownIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'
import { useDebounce, DEBOUNCE_DELAYS } from '@/composables/useDebounce'
import { useSettingsStore } from '../stores/settingsStore'
import type { ThemeOption } from '../types/profile.types'
import type { Component } from 'vue'

type ThemeToggleVariant = 'simple' | 'dropdown' | 'radio'
type Size = 'sm' | 'md' | 'lg'

interface ThemeOptionData {
  value: ThemeOption
  label: string
  description: string
  icon: Component
}

interface Props {
  variant?: ThemeToggleVariant
  size?: Size
  showLabel?: boolean
  disabled?: boolean
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'simple',
  size: 'md',
  showLabel: false,
  disabled: false
})

const emit = defineEmits<{
  change: [theme: ThemeOption]
}>()

// Store
const settingsStore = useSettingsStore()

// Refs
const showDropdown = ref(false)
const componentId = ref(Math.random().toString(36).substring(2, 9))

// Debounced theme update to prevent excessive API calls
const debouncedSetTheme = useDebounce(async (theme: ThemeOption) => {
  await settingsStore.setTheme(theme)
}, DEBOUNCE_DELAYS.SETTINGS)

// Theme options
const themeOptions: ThemeOptionData[] = [
  {
    value: 'light',
    label: 'Light',
    description: 'Light theme with bright colors',
    icon: SunIcon
  },
  {
    value: 'dark',
    label: 'Dark', 
    description: 'Dark theme with muted colors',
    icon: MoonIcon
  },
  {
    value: 'auto',
    label: 'System',
    description: 'Follow system preference',
    icon: ComputerDesktopIcon
  }
]

// Computed
const currentThemeOption = computed(() => {
  const theme = settingsStore.userSettings?.theme || 'auto'
  return themeOptions.find(option => option.value === theme) || themeOptions[2]
})

const currentThemeIcon = computed(() => currentThemeOption.value.icon)
const currentThemeLabel = computed(() => currentThemeOption.value.label)

const ariaLabel = computed(() => {
  if (props.variant === 'simple') {
    return `Switch to ${getNextTheme()} theme`
  }
  return `Current theme: ${currentThemeLabel.value}. Click to change theme`
})

const tooltipText = computed(() => {
  if (props.variant === 'simple') {
    return `Currently ${currentThemeLabel.value.toLowerCase()}. Click to switch to ${getNextTheme()}`
  }
  return `Theme: ${currentThemeLabel.value}`
})

// Size classes
const sizeClasses = {
  sm: {
    button: 'p-1.5',
    icon: 'w-4 h-4',
    text: 'text-xs'
  },
  md: {
    button: 'p-2',
    icon: 'w-5 h-5',
    text: 'text-sm'
  },
  lg: {
    button: 'p-2.5',
    icon: 'w-6 h-6',
    text: 'text-base'
  }
}

// Style classes
const containerClasses = computed(() => [
  'theme-toggle',
  props.class
])

const toggleButtonClasses = computed(() => [
  'inline-flex',
  'items-center',
  'justify-center',
  'rounded-md',
  'border',
  'border-secondary-300',
  'bg-white',
  'text-secondary-700',
  'transition-all',
  'duration-200',
  'hover:bg-secondary-50',
  'hover:border-secondary-400',
  'focus:outline-none',
  'focus:ring-2',
  'focus:ring-primary-500',
  'focus:ring-offset-2',
  'disabled:opacity-50',
  'disabled:cursor-not-allowed',
  'dark:bg-secondary-800',
  'dark:border-secondary-600',
  'dark:text-secondary-300',
  'dark:hover:bg-secondary-700',
  'dark:hover:border-secondary-500',
  sizeClasses[props.size].button
])

const dropdownButtonClasses = computed(() => [
  ...toggleButtonClasses.value
])

const dropdownMenuClasses = [
  'absolute',
  'right-0',
  'z-50',
  'mt-2',
  'w-64',
  'bg-white',
  'border',
  'border-secondary-200',
  'rounded-md',
  'shadow-lg',
  'ring-1',
  'ring-black',
  'ring-opacity-5',
  'focus:outline-none',
  'dark:bg-secondary-800',
  'dark:border-secondary-700'
]

const dropdownItemClasses = [
  'flex',
  'items-start',
  'w-full',
  'px-4',
  'py-3',
  'text-left',
  'text-secondary-700',
  'hover:bg-secondary-50',
  'focus:outline-none',
  'focus:bg-secondary-50',
  'transition-colors',
  'duration-150',
  'dark:text-secondary-300',
  'dark:hover:bg-secondary-700',
  'dark:focus:bg-secondary-700',
  'first:rounded-t-md',
  'last:rounded-b-md'
]

const radioOptionClasses = [
  'relative',
  'flex',
  'items-start',
  'space-x-3',
  'p-3',
  'rounded-lg',
  'border',
  'border-secondary-200',
  'bg-white',
  'cursor-pointer',
  'transition-all',
  'duration-200',
  'hover:bg-secondary-50',
  'hover:border-secondary-300',
  'dark:bg-secondary-800',
  'dark:border-secondary-700',
  'dark:hover:bg-secondary-700'
]

const iconClasses = computed(() => [
  sizeClasses[props.size].icon,
  'transition-colors',
  'duration-200'
])

// Methods
const radioIndicatorClasses = (value: ThemeOption) => [
  'flex',
  'items-center',
  'justify-center',
  'w-5',
  'h-5',
  'rounded-full',
  'border-2',
  'transition-all',
  'duration-200',
  {
    'border-primary-600 bg-primary-600': settingsStore.userSettings?.theme === value,
    'border-secondary-300 bg-white dark:border-secondary-600 dark:bg-secondary-800': 
      settingsStore.userSettings?.theme !== value
  }
]

const radioInnerClasses = (value: ThemeOption) => [
  'w-2',
  'h-2',
  'rounded-full',
  'transition-all',
  'duration-200',
  {
    'bg-white': settingsStore.userSettings?.theme === value,
    'bg-transparent': settingsStore.userSettings?.theme !== value
  }
]

const getNextTheme = (): string => {
  const currentTheme = settingsStore.userSettings?.theme || 'auto'
  const currentIndex = themeOptions.findIndex(option => option.value === currentTheme)
  const nextIndex = (currentIndex + 1) % themeOptions.length
  return themeOptions[nextIndex].label.toLowerCase()
}

const cycleTheme = async () => {
  if (props.disabled || settingsStore.loading) return
  
  const currentTheme = settingsStore.userSettings?.theme || 'auto'
  const currentIndex = themeOptions.findIndex(option => option.value === currentTheme)
  const nextIndex = (currentIndex + 1) % themeOptions.length
  const nextTheme = themeOptions[nextIndex].value
  
  await selectTheme(nextTheme)
}

const selectTheme = async (theme: ThemeOption) => {
  if (props.disabled || settingsStore.loading) return
  
  showDropdown.value = false
  debouncedSetTheme(theme)
  emit('change', theme)
}

// Close dropdown when clicking outside
const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.theme-toggle')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
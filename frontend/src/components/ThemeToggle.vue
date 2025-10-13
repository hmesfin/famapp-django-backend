<template>
  <div class="relative">
    <!-- Desktop: Button group -->
    <div class="hidden sm:flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
      <button
        v-for="option in themeOptions"
        :key="option.value"
        @click="setTheme(option.value)"
        :class="[
          'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all',
          theme === option.value
            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
        ]"
        :title="option.label"
      >
        <component :is="option.icon" class="w-4 h-4" />
        <span class="hidden lg:inline">{{ option.label }}</span>
      </button>
    </div>

    <!-- Mobile: Dropdown -->
    <div class="sm:hidden">
      <button
        @click="showDropdown = !showDropdown"
        class="flex items-center gap-2 px-3 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        :title="`Current theme: ${currentThemeLabel}`"
      >
        <component :is="currentThemeIcon" class="w-5 h-5" />
      </button>

      <!-- Dropdown menu -->
      <Transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div
          v-if="showDropdown"
          class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 z-50"
        >
          <div class="py-1">
            <button
              v-for="option in themeOptions"
              :key="option.value"
              @click="selectTheme(option.value)"
              :class="[
                'flex items-center gap-3 w-full px-4 py-2 text-sm transition-colors',
                theme === option.value
                  ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              ]"
            >
              <component :is="option.icon" class="w-4 h-4" />
              <span>{{ option.label }}</span>
              <svg
                v-if="theme === option.value"
                class="w-4 h-4 ml-auto text-blue-600 dark:text-blue-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useThemeStore } from '@/stores/theme'
import type { Theme } from '@/stores/theme'

const themeStore = useThemeStore()
const showDropdown = ref(false)

const theme = computed(() => themeStore.theme)

// Theme options with icons
const themeOptions = [
  {
    value: 'light' as Theme,
    label: 'Light',
    icon: h('svg', {
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': 2
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z'
      })
    ])
  },
  {
    value: 'dark' as Theme,
    label: 'Dark',
    icon: h('svg', {
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': 2
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z'
      })
    ])
  },
  {
    value: 'system' as Theme,
    label: 'System',
    icon: h('svg', {
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': 2
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
      })
    ])
  }
]

const currentThemeOption = computed(() => 
  themeOptions.find(opt => opt.value === theme.value) || themeOptions[0]
)

const currentThemeIcon = computed(() => currentThemeOption.value.icon)
const currentThemeLabel = computed(() => currentThemeOption.value.label)

const setTheme = (value: Theme) => {
  themeStore.setTheme(value)
}

const selectTheme = (value: Theme) => {
  setTheme(value)
  showDropdown.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showDropdown.value = false
  }
}

// Add/remove click listener
if (typeof window !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}
</script>
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export type Theme = 'light' | 'dark' | 'system'

export const useThemeStore = defineStore('theme', () => {
  // State
  const theme = ref<Theme>('system')
  const systemPreference = ref<'light' | 'dark'>('light')
  
  // Load saved theme from localStorage on init
  const savedTheme = localStorage.getItem('theme') as Theme | null
  if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
    theme.value = savedTheme
  }
  
  // Detect system preference
  const detectSystemPreference = () => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      systemPreference.value = 'dark'
    } else {
      systemPreference.value = 'light'
    }
  }
  
  // Initial system detection
  detectSystemPreference()
  
  // Listen for system theme changes
  if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      systemPreference.value = e.matches ? 'dark' : 'light'
      applyTheme()
    })
  }
  
  // Computed: what theme is actually active
  const activeTheme = computed(() => {
    if (theme.value === 'system') {
      return systemPreference.value
    }
    return theme.value
  })
  
  // Apply theme to DOM
  const applyTheme = () => {
    const root = document.documentElement
    
    // Remove transition class temporarily to prevent flash
    root.classList.add('theme-transition-none')
    
    if (activeTheme.value === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    
    // Re-enable transitions after a frame
    requestAnimationFrame(() => {
      root.classList.remove('theme-transition-none')
    })
  }
  
  // Watch for theme changes
  watch(theme, (newTheme) => {
    localStorage.setItem('theme', newTheme)
    applyTheme()
  })
  
  // Watch for active theme changes (when system preference changes)
  watch(activeTheme, () => {
    applyTheme()
  })
  
  // Actions
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme
  }
  
  const toggleTheme = () => {
    // Cycle through: light -> dark -> system
    if (theme.value === 'light') {
      theme.value = 'dark'
    } else if (theme.value === 'dark') {
      theme.value = 'system'
    } else {
      theme.value = 'light'
    }
  }
  
  // Initialize theme on store creation
  applyTheme()
  
  return {
    // State
    theme,
    activeTheme,
    systemPreference,
    
    // Actions
    setTheme,
    toggleTheme,
  }
})
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
import './utils/veeValidate' // Initialize VeeValidate configuration
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Initialize auth store BEFORE router to ensure auth state is ready
const authStore = useAuthStore()

// Initialize theme store to apply saved theme immediately
const themeStore = useThemeStore()

// Wait for auth initialization before mounting the app
// This prevents the login flash on authenticated page refresh
authStore.initializeAuth().then(() => {
  // Now that auth is initialized, add the router
  app.use(router)
  
  // Mount the app
  app.mount('#app')
})

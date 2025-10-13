import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import AutoImport from 'unplugin-auto-import/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        '@vueuse/core',
        {
          'pinia': ['defineStore', 'storeToRefs'],
          '@tanstack/vue-query': ['useQuery', 'useMutation', 'useQueryClient'],
          'vee-validate': ['useField', 'useForm', 'defineRule', 'configure'],
          'date-fns': ['format', 'parseISO', 'isAfter', 'isBefore', 'addDays', 'subDays']
        }
      ],
      dts: true, // Generate type definitions
      eslintrc: {
        enabled: true, // Generate .eslintrc-auto-import.json
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})

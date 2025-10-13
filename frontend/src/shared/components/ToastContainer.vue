<template>
  <teleport to="body">
    <!-- Toast container -->
    <div
      aria-live="assertive"
      class="pointer-events-none fixed inset-0 z-[9999] flex items-end px-4 py-6 sm:items-start sm:p-6"
    >
      <div class="flex w-full flex-col items-center space-y-4 sm:items-end">
        <!-- Individual toasts -->
        <TransitionGroup
          name="toast-list"
          tag="div"
          class="w-full space-y-4"
        >
          <Toast
            v-for="toast in toasts"
            :key="toast.id"
            :toast="toast"
            @close="removeToast(toast.id)"
          />
        </TransitionGroup>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useToastStore } from '@/stores/toast'
import Toast from './Toast.vue'

const toastStore = useToastStore()
const { toasts } = storeToRefs(toastStore)
const { removeToast } = toastStore
</script>

<style scoped>
.toast-list-move,
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.toast-list-leave-active {
  position: absolute;
  right: 0;
}
</style>
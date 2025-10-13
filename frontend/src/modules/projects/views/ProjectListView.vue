<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="md:flex md:items-center md:justify-between mb-8">
        <div class="flex-1 min-w-0">
          <h2
            class="text-3xl font-bold leading-7 text-gray-900 dark:text-gray-100 sm:text-4xl sm:truncate"
          >
            Projects
          </h2>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Manage your development projects and track progress
          </p>
        </div>
        <div class="mt-4 flex md:mt-0 md:ml-4 space-x-3">
          <!-- Filter dropdown -->
          <BaseSelect
            v-model="statusFilter"
            :options="filterOptions"
            placeholder="All Projects"
            @update:model-value="handleFilterChange"
          />

          <!-- Search -->
          <BaseInput
            v-model="searchQuery"
            type="search"
            placeholder="Search projects..."
            :leading-icon="MagnifyingGlassIcon"
            @input="handleSearch"
            class="w-80"
          />

          <!-- New Project Button -->
          <BaseButton
            variant="primary"
            :leading-icon="PlusIcon"
            @click="showCreateModal = true"
          >
            New Project
          </BaseButton>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatCard
          title="Total Projects"
          :value="totalProjects"
          :icon="FolderIcon"
          variant="secondary"
        />
        
        <StatCard
          title="Active"
          :value="activeCount"
          :icon="PlayIcon"
          variant="success"
        />
        
        <StatCard
          title="Completed"
          :value="completedCount"
          :icon="CheckCircleIcon"
          variant="info"
        />
        
        <StatCard
          title="Planning"
          :value="planningCount"
          :icon="ClockIcon"
          variant="warning"
        />
      </div>

      <!-- Project List -->
      <ProjectList
        :projects="projectStore.projects"
        :loading="projectStore.loading"
        @create="showCreateModal = true"
      />

      <!-- Create Project Modal -->
      <ProjectFormModal
        ref="modalRef"
        :show="showCreateModal"
        @close="showCreateModal = false"
        @save="handleCreateProject"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FolderIcon,
  PlayIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'
import BaseButton from '@/shared/components/BaseButton.vue'
import BaseInput from '@/shared/components/BaseInput.vue'
import BaseSelect from '@/shared/components/BaseSelect.vue'
import StatCard from '@/shared/components/StatCard.vue'
import { useProjectStore } from '../stores/projectStore'
import ProjectList from '../components/ProjectList.vue'
import ProjectFormModal from '../components/ProjectFormModal.vue'
import type { ProjectForm } from '../types/project.types'

const projectStore = useProjectStore()

// State
const showCreateModal = ref(false)
const statusFilter = ref('')
const searchQuery = ref('')
const searchTimeout = ref<ReturnType<typeof setTimeout>>()
import type { ComponentPublicInstance } from 'vue'
const modalRef = ref<ComponentPublicInstance | null>(null)

// Filter options for select component
const filterOptions = [
  { value: '', label: 'All Projects' },
  { value: 'planning', label: 'Planning' },
  { value: 'active', label: 'Active' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' }
]

// Computed
const totalProjects = computed(() => projectStore.projects?.length || 0)
const activeCount = computed(
  () => projectStore.projects?.filter((p) => p.status === 'active').length || 0,
)
const completedCount = computed(
  () => projectStore.projects?.filter((p) => p.status === 'completed').length || 0,
)
const planningCount = computed(
  () => projectStore.projects?.filter((p) => p.status === 'planning').length || 0,
)

async function loadProjects() {
  const filters: Record<string, string> = {}
  if (statusFilter.value) filters.status = statusFilter.value
  if (searchQuery.value) filters.search = searchQuery.value

  await projectStore.fetchProjects(filters)
}

function handleFilterChange() {
  loadProjects()
}

function handleSearch() {
  // Debounce search
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    loadProjects()
  }, 300)
}
async function handleCreateProject(data: ProjectForm) {
  try {
    const result = await projectStore.createProject(data)
    if (result) {
      // Close modal immediately on success
      showCreateModal.value = false
      // Clear modal loading state
      if (modalRef.value) {
        modalRef.value.loading = false
      }
      // Force a full refresh of the projects list
      // This ensures we get the complete data with nested objects
      await loadProjects()
    }
  } catch (error: unknown) {
    console.error('Failed to create project:', error)
    // Pass server validation errors to modal
    if (
      modalRef.value &&
      typeof error === 'object' &&
      error !== null &&
      'response' in error &&
      (error as any).response?.data
    ) {
      modalRef.value.handleServerError((error as any).response.data)
    } else if (modalRef.value) {
      // Clear loading state even on unexpected errors
      modalRef.value.loading = false
    }
    // Keep modal open on error so user can fix and retry
  }
}

// Lifecycle
onMounted(() => {
  loadProjects()
})
</script>

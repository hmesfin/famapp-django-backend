<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ProjectCardSkeleton
        v-for="i in skeletonCount"
        :key="i"
      />
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else-if="!projects || projects.length === 0"
      :icon="FolderIcon"
      title="No projects found"
      description="Get started by creating your first project."
      :primary-action="{
        label: 'New Project',
        icon: PlusIcon,
        onClick: () => $emit('create')
      }"
    />

    <!-- Project grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ProjectCard
        v-for="project in (projects || [])"
        :key="project.public_id"
        :project="project"
        :can-edit="canEditProject(project)"
        :can-delete="canDeleteProject(project)"
        @click="handleProjectClick"
        @edit="handleProjectEdit"
        @delete="handleProjectDelete"
      />
    </div>

    <!-- Pagination -->
    <Pagination
      v-if="showPagination && !loading"
      :current-page="currentPage"
      :has-previous="hasPrevious"
      :has-next="hasNext"
      @prev-page="$emit('prev-page')"
      @next-page="$emit('next-page')"
      class="mt-6"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FolderIcon, PlusIcon } from '@heroicons/vue/24/outline'
import ProjectCard from './ProjectCard.vue'
import ProjectCardSkeleton from './ProjectCardSkeleton.vue'
import EmptyState from '@/shared/components/EmptyState.vue'
import Pagination from '@/shared/components/Pagination.vue'
import type { Project } from '../types/project.types'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

interface Props {
  projects?: Project[]
  loading?: boolean
  currentPage?: number
  hasNext?: boolean
  hasPrevious?: boolean
  showPagination?: boolean
  skeletonCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  projects: () => [],
  loading: false,
  currentPage: 1,
  hasNext: false,
  hasPrevious: false,
  showPagination: false,
  skeletonCount: 6
})

const emit = defineEmits<{
  create: []
  'prev-page': []
  'next-page': []
}>()

const authStore = useAuthStore()
const router = useRouter()

// Check permissions
function canEditProject(project: Project): boolean {
  if (!project) return false
  const user = authStore.user
  if (!user || !user.public_id) return false
  
  // Owner can always edit
  if (project.owner?.public_id === user.public_id) return true
  
  // Check if user is a manager
  const membership = project.memberships?.find(m => m.user?.public_id === user.public_id)
  return membership?.role === 'manager' || false
}

function canDeleteProject(project: Project): boolean {
  if (!project) return false
  const user = authStore.user
  if (!user || !user.public_id) return false
  
  // Only owner can delete
  return project.owner?.public_id === user.public_id || false
}

// Handlers
function handleProjectClick(project: Project) {
  router.push({ 
    name: 'project-detail', 
    params: { id: project.public_id } 
  })
}

function handleProjectEdit(project: Project) {
  router.push({ 
    name: 'project-edit', 
    params: { id: project.public_id } 
  })
}

async function handleProjectDelete(project: Project) {
  // This would typically show a confirmation dialog
  // For now, we'll emit an event for the parent to handle
  const confirmed = confirm(`Are you sure you want to delete "${project.name}"?`)
  if (confirmed) {
    // Parent component should handle the actual deletion
    console.log('Delete project:', project.public_id)
  }
}
</script>
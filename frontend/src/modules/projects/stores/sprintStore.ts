/**
 * Sprint Store - Pinia State Management
 * Ham Dog & TC's focused sprint management store!
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import projectService from '../services/projectService'
import { useToastStore } from '@/stores/toast'
import type {
  Sprint,
  SprintForm
} from '../types/project.types'

export const useSprintStore = defineStore('sprint', () => {
  const toastStore = useToastStore()

  // State
  const projectSprints = ref<Sprint[]>([])
  const currentSprint = ref<Sprint | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeSprint = computed(() =>
    projectSprints.value.find(s => s.is_active)
  )

  const completedSprints = computed(() =>
    projectSprints.value.filter(s => !s.is_active && new Date(s.end_date) < new Date())
  )

  const upcomingSprints = computed(() =>
    projectSprints.value.filter(s => !s.is_active && new Date(s.start_date) > new Date())
  )

  // Actions
  async function fetchProjectSprints(projectId: string) {
    loading.value = true
    error.value = null
    
    try {
      projectSprints.value = await projectService.listSprints(projectId)
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch sprints'
      toastStore.error('Failed to load sprints')
    } finally {
      loading.value = false
    }
  }

  async function createSprint(data: SprintForm) {
    loading.value = true
    error.value = null
    
    try {
      const newSprint = await projectService.createSprint(data)
      
      // Add to list
      projectSprints.value.push(newSprint)
      
      toastStore.success('Sprint created successfully!')
      return newSprint
    } catch (err: any) {
      error.value = err.message || 'Failed to create sprint'
      toastStore.error('Failed to create sprint')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateSprint(publicId: string, data: Partial<SprintForm>) {
    loading.value = true
    error.value = null
    
    try {
      const updatedSprint = await projectService.updateSprint(publicId, data)
      
      // Update in list
      const index = projectSprints.value.findIndex(s => s.public_id === publicId)
      if (index !== -1) {
        projectSprints.value[index] = updatedSprint
      }
      
      // Update current if it's the same
      if (currentSprint.value?.public_id === publicId) {
        currentSprint.value = updatedSprint
      }
      
      toastStore.success('Sprint updated successfully!')
      return updatedSprint
    } catch (err: any) {
      error.value = err.message || 'Failed to update sprint'
      toastStore.error('Failed to update sprint')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteSprint(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      await projectService.deleteSprint(publicId)
      
      // Remove from list
      projectSprints.value = projectSprints.value.filter(s => s.public_id !== publicId)
      
      // Clear current if it was deleted
      if (currentSprint.value?.public_id === publicId) {
        currentSprint.value = null
      }
      
      toastStore.success('Sprint deleted successfully!')
    } catch (err: any) {
      error.value = err.message || 'Failed to delete sprint'
      toastStore.error('Failed to delete sprint')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function activateSprint(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      const activatedSprint = await projectService.activateSprint(publicId)
      
      // Update all sprints (deactivate others, activate this one)
      projectSprints.value = projectSprints.value.map(sprint => ({
        ...sprint,
        is_active: sprint.public_id === publicId
      }))
      
      toastStore.success('Sprint activated successfully!')
      return activatedSprint
    } catch (err: any) {
      error.value = err.message || 'Failed to activate sprint'
      toastStore.error('Failed to activate sprint')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deactivateSprint(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      const deactivatedSprint = await projectService.deactivateSprint(publicId)
      
      // Update sprint in list
      const index = projectSprints.value.findIndex(s => s.public_id === publicId)
      if (index !== -1) {
        projectSprints.value[index] = { ...projectSprints.value[index], is_active: false }
      }
      
      // Clear current if it was deactivated
      if (currentSprint.value?.public_id === publicId) {
        currentSprint.value = { ...currentSprint.value, is_active: false }
      }
      
      toastStore.success('Sprint deactivated successfully!')
      return deactivatedSprint
    } catch (err: any) {
      error.value = err.message || 'Failed to deactivate sprint'
      toastStore.error('Failed to deactivate sprint')
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset store
  function resetSprintStore() {
    projectSprints.value = []
    currentSprint.value = null
    loading.value = false
    error.value = null
  }

  return {
    // State
    projectSprints,
    currentSprint,
    loading,
    error,

    // Computed
    activeSprint,
    completedSprints,
    upcomingSprints,

    // Actions
    fetchProjectSprints,
    createSprint,
    updateSprint,
    deleteSprint,
    activateSprint,
    deactivateSprint,

    // Utils
    resetSprintStore
  }
})
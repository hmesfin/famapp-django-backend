/**
 * Project Store - Pinia State Management
 * Ham Dog & TC's centralized state for all things projects!
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import projectService from '../services/projectService'
import { useToastStore } from '@/stores/toast'
import type {
  Project,
  ProjectForm,
  ProjectFilters
} from '../types/project.types'

export const useProjectStore = defineStore('project', () => {
  const toastStore = useToastStore()

  // State
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Filters
  const projectFilters = ref<ProjectFilters>({})

  // Computed
  const activeProjects = computed(() =>
    projects.value.filter(p => p.status === 'active')
  )

  const completedProjects = computed(() =>
    projects.value.filter(p => p.status === 'completed')
  )

  const projectCount = computed(() => projects.value.length)

  // Actions - Projects
  async function fetchProjects(filters?: ProjectFilters) {
    loading.value = true
    error.value = null
    
    try {
      const response = await projectService.listProjects(filters)
      // Handle both paginated and non-paginated responses
      projects.value = response.results || response || []
      projectFilters.value = filters || {}
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch projects'
      toastStore.error('Failed to load projects')
      projects.value = [] // Ensure projects is always an array
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      currentProject.value = await projectService.getProject(publicId)
      // Project fetched successfully - related data will be fetched by dedicated stores
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch project'
      toastStore.error('Failed to load project details')
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: ProjectForm) {
    loading.value = true
    error.value = null
    
    try {
      const newProject = await projectService.createProject(data)
      // Don't add the raw response - it doesn't have all the nested data
      // Instead, we'll let the parent component reload the full list
      toastStore.success('Project created successfully!')
      return newProject
    } catch (err: any) {
      // Extract meaningful error message
      let errorMessage = 'Failed to create project'
      
      if (err.response?.data) {
        const data = err.response.data
        
        // Check for specific field errors
        if (data.name) {
          errorMessage = Array.isArray(data.name) ? data.name[0] : data.name
        } else if (data.non_field_errors) {
          errorMessage = Array.isArray(data.non_field_errors) 
            ? data.non_field_errors[0] 
            : data.non_field_errors
        } else if (data.detail) {
          errorMessage = data.detail
        } else if (data.end_date) {
          errorMessage = Array.isArray(data.end_date) ? data.end_date[0] : data.end_date
        } else if (data.start_date) {
          errorMessage = Array.isArray(data.start_date) ? data.start_date[0] : data.start_date
        } else if (data.status) {
          errorMessage = Array.isArray(data.status) ? data.status[0] : data.status
        } else if (data.description) {
          errorMessage = Array.isArray(data.description) ? data.description[0] : data.description
        }
        
        // Make message more user-friendly
        if (errorMessage.includes('unique_project_name_per_owner')) {
          errorMessage = `You already have a project named "${data.name}". Please choose a different name.`
        } else if (errorMessage.includes('constraint')) {
          errorMessage = 'This project name is already taken. Please choose another.'
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      // NEVER show HTTP status codes to users!
      if (errorMessage.startsWith('HTTP ')) {
        // Extract any field errors we might have missed
        if (err.response?.data && typeof err.response.data === 'object') {
          const fieldNames: Record<string, string> = {
            name: 'Project name',
            description: 'Description', 
            start_date: 'Start date',
            end_date: 'End date',
            status: 'Status'
          }
          
          const errors = Object.entries(err.response.data)
            .filter(([field]) => field !== 'detail' && field !== 'non_field_errors')
            .map(([field, msg]) => {
              const message = Array.isArray(msg) ? msg[0] : msg
              const fieldLabel = fieldNames[field] || field.replace(/_/g, ' ')
              return `${fieldLabel}: ${message}`
            })
          
          if (errors.length > 0) {
            errorMessage = errors.length === 1 ? errors[0] : `Please fix these issues: ${errors.join('; ')}`
          } else {
            errorMessage = 'Something went wrong. Please check your information and try again.'
          }
        } else {
          errorMessage = 'Something went wrong. Please check your information and try again.'
        }
      }
      
      error.value = errorMessage
      toastStore.error(errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProject(publicId: string, data: Partial<ProjectForm>) {
    loading.value = true
    error.value = null
    
    try {
      const updatedProject = await projectService.updateProject(publicId, data)
      
      // Update in list
      const index = projects.value.findIndex(p => p.public_id === publicId)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      
      // Update current if it's the same
      if (currentProject.value?.public_id === publicId) {
        currentProject.value = updatedProject
      }
      
      toastStore.success('Project updated successfully!')
      return updatedProject
    } catch (err: any) {
      error.value = err.message || 'Failed to update project'
      toastStore.error('Failed to update project')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteProject(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      await projectService.deleteProject(publicId)
      projects.value = projects.value.filter(p => p.public_id !== publicId)
      
      if (currentProject.value?.public_id === publicId) {
        currentProject.value = null
      }
      
      toastStore.success('Project deleted successfully!')
    } catch (err: any) {
      error.value = err.message || 'Failed to delete project'
      toastStore.error('Failed to delete project')
      throw err
    } finally {
      loading.value = false
    }
  }


  // Actions - Team Management
  async function addProjectMember(projectId: string, userId: string, role: string) {
    try {
      const newMember = await projectService.addProjectMember(projectId, userId, role)
      
      // Update current project's memberships if it's the same project
      if (currentProject.value?.public_id === projectId && currentProject.value.memberships) {
        currentProject.value.memberships.push(newMember)
      }
      
      return newMember
    } catch (err: any) {
      toastStore.error('Failed to add team member')
      throw err
    }
  }

  async function removeProjectMember(projectId: string, userId: string) {
    try {
      await projectService.removeProjectMember(projectId, userId)
      
      // Update current project's memberships if it's the same project
      if (currentProject.value?.public_id === projectId && currentProject.value.memberships) {
        currentProject.value.memberships = currentProject.value.memberships.filter(
          m => m.user?.public_id !== userId
        )
      }
    } catch (err: any) {
      toastStore.error('Failed to remove team member')
      throw err
    }
  }


  // Reset store
  function resetProjectStore() {
    projects.value = []
    currentProject.value = null
    loading.value = false
    error.value = null
    projectFilters.value = {}
  }

  return {
    // State
    projects,
    currentProject,
    loading,
    error,
    projectFilters,

    // Computed
    activeProjects,
    completedProjects,
    projectCount,

    // Actions - Projects
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,

    // Actions - Team Management
    addProjectMember,
    removeProjectMember,

    // Utils
    resetProjectStore
  }
})
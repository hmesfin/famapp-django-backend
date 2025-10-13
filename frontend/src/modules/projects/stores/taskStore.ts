/**
 * Task Store - Pinia State Management
 * Ham Dog & TC's focused task management store!
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import projectService from '../services/projectService'
import { useToastStore } from '@/stores/toast'
import type {
  Task,
  TaskForm,
  TaskFilters,
  TaskStatus
} from '../types/project.types'

export const useTaskStore = defineStore('task', () => {
  const toastStore = useToastStore()

  // State
  const projectTasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const taskFilters = ref<TaskFilters>({})

  // Computed
  const tasksByStatus = computed(() => {
    const grouped: Record<TaskStatus, Task[]> = {
      todo: [],
      in_progress: [],
      review: [],
      done: [],
      blocked: []
    }

    projectTasks.value.forEach(task => {
      grouped[task.status].push(task)
    })

    return grouped
  })

  const completedTasksCount = computed(() =>
    projectTasks.value.filter(t => t.status === 'done').length
  )

  const inProgressTasksCount = computed(() =>
    projectTasks.value.filter(t => t.status === 'in_progress').length
  )

  const blockedTasksCount = computed(() =>
    projectTasks.value.filter(t => t.status === 'blocked').length
  )

  // Actions
  async function fetchProjectTasks(projectId: string, filters?: TaskFilters) {
    loading.value = true
    error.value = null
    
    try {
      const tasks = await projectService.getProjectTasks(projectId, filters)
      projectTasks.value = tasks || []
      taskFilters.value = filters || {}
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch tasks'
      toastStore.error('Failed to load tasks')
      projectTasks.value = [] // Ensure it's always an array
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      currentTask.value = await projectService.getTask(publicId)
      return currentTask.value
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch task'
      toastStore.error('Failed to load task details')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: TaskForm) {
    loading.value = true
    error.value = null
    
    try {
      const newTask = await projectService.createTask(data)
      
      // Debug logging
      console.log('Current projectTasks before adding:', projectTasks.value)
      console.log('New task to add:', newTask)
      
      // Ensure projectTasks is initialized as an array using a new array
      // This forces Vue reactivity to work properly
      const currentTasks = projectTasks.value || []
      projectTasks.value = [newTask, ...currentTasks]
      
      console.log('projectTasks after adding:', projectTasks.value)
      
      toastStore.success('Task created successfully!')
      return newTask
    } catch (err: any) {
      error.value = err.message || 'Failed to create task'
      toastStore.error('Failed to create task')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTask(publicId: string, data: Partial<TaskForm>) {
    loading.value = true
    error.value = null
    
    try {
      const updatedTask = await projectService.updateTask(publicId, data)
      
      // Update in list
      const index = projectTasks.value.findIndex(t => t.public_id === publicId)
      if (index !== -1) {
        projectTasks.value[index] = updatedTask
      }
      
      // Update current if it's the same
      if (currentTask.value?.public_id === publicId) {
        currentTask.value = updatedTask
      }
      
      toastStore.success('Task updated successfully!')
      return updatedTask
    } catch (err: any) {
      error.value = err.message || 'Failed to update task'
      toastStore.error('Failed to update task')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTaskStatus(publicId: string, status: TaskStatus) {
    try {
      const updatedTask = await projectService.updateTaskStatus(publicId, status)
      
      // Update in list
      const index = projectTasks.value.findIndex(t => t.public_id === publicId)
      if (index !== -1) {
        projectTasks.value[index] = updatedTask
      }
      
      toastStore.success(`Task moved to ${status.replace('_', ' ')}`)
      return updatedTask
    } catch (err: any) {
      toastStore.error('Failed to update task status')
      throw err
    }
  }

  async function deleteTask(publicId: string) {
    loading.value = true
    error.value = null
    
    try {
      await projectService.deleteTask(publicId)
      projectTasks.value = projectTasks.value.filter(t => t.public_id !== publicId)
      
      if (currentTask.value?.public_id === publicId) {
        currentTask.value = null
      }
      
      toastStore.success('Task deleted successfully!')
    } catch (err: any) {
      error.value = err.message || 'Failed to delete task'
      toastStore.error('Failed to delete task')
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset store
  function resetTaskStore() {
    projectTasks.value = []
    currentTask.value = null
    loading.value = false
    error.value = null
    taskFilters.value = {}
  }

  return {
    // State
    projectTasks,
    currentTask,
    loading,
    error,
    taskFilters,

    // Computed
    tasksByStatus,
    completedTasksCount,
    inProgressTasksCount,
    blockedTasksCount,

    // Actions
    fetchProjectTasks,
    fetchTask,
    createTask,
    updateTask,
    updateTaskStatus,
    deleteTask,

    // Utils
    resetTaskStore
  }
})
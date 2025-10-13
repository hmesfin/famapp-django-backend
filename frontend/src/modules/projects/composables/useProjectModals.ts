/**
 * Composable for managing project-related modals
 * Extracted by RefactorX from ProjectDetailView
 */

import { ref, type Ref } from 'vue'
import type { Task } from '../types/project.types'

interface ProjectModals {
  // Modal visibility states
  showEditModal: Ref<boolean>
  showTaskModal: Ref<boolean>
  showTaskDetailModal: Ref<boolean>
  showTeamModal: Ref<boolean>
  showDeleteModal: Ref<boolean>
  showSprintModal: Ref<boolean>
  
  // Selected items for modals
  selectedTask: Ref<Task | null>
  editingTask: Ref<Task | null>
  
  // Modal control functions
  openEditModal: () => void
  closeEditModal: () => void
  openTaskModal: (task?: Task) => void
  closeTaskModal: () => void
  openTaskDetailModal: (task: Task) => void
  closeTaskDetailModal: () => void
  openTeamModal: () => void
  closeTeamModal: () => void
  openDeleteModal: () => void
  closeDeleteModal: () => void
  openSprintModal: () => void
  closeSprintModal: () => void
  
  // Reset all modals
  closeAllModals: () => void
}

/**
 * Returns reactive modal management for project views
 */
export function useProjectModals(): ProjectModals {
  // Modal visibility states
  const showEditModal = ref(false)
  const showTaskModal = ref(false)
  const showTaskDetailModal = ref(false)
  const showTeamModal = ref(false)
  const showDeleteModal = ref(false)
  const showSprintModal = ref(false)
  
  // Selected items
  const selectedTask = ref<Task | null>(null)
  const editingTask = ref<Task | null>(null)
  
  // Modal control functions
  const openEditModal = () => {
    showEditModal.value = true
  }
  
  const closeEditModal = () => {
    showEditModal.value = false
  }
  
  const openTaskModal = (task?: Task) => {
    if (task) {
      editingTask.value = task
    } else {
      editingTask.value = null
    }
    showTaskModal.value = true
  }
  
  const closeTaskModal = () => {
    showTaskModal.value = false
    editingTask.value = null
  }
  
  const openTaskDetailModal = (task: Task) => {
    selectedTask.value = task
    showTaskDetailModal.value = true
  }
  
  const closeTaskDetailModal = () => {
    showTaskDetailModal.value = false
    selectedTask.value = null
  }
  
  const openTeamModal = () => {
    showTeamModal.value = true
  }
  
  const closeTeamModal = () => {
    showTeamModal.value = false
  }
  
  const openDeleteModal = () => {
    showDeleteModal.value = true
  }
  
  const closeDeleteModal = () => {
    showDeleteModal.value = false
  }
  
  const openSprintModal = () => {
    showSprintModal.value = true
  }
  
  const closeSprintModal = () => {
    showSprintModal.value = false
  }
  
  const closeAllModals = () => {
    showEditModal.value = false
    showTaskModal.value = false
    showTaskDetailModal.value = false
    showTeamModal.value = false
    showDeleteModal.value = false
    showSprintModal.value = false
    selectedTask.value = null
    editingTask.value = null
  }
  
  return {
    // States
    showEditModal,
    showTaskModal,
    showTaskDetailModal,
    showTeamModal,
    showDeleteModal,
    showSprintModal,
    selectedTask,
    editingTask,
    
    // Functions
    openEditModal,
    closeEditModal,
    openTaskModal,
    closeTaskModal,
    openTaskDetailModal,
    closeTaskDetailModal,
    openTeamModal,
    closeTeamModal,
    openDeleteModal,
    closeDeleteModal,
    openSprintModal,
    closeSprintModal,
    closeAllModals
  }
}
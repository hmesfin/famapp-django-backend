/**
 * Composable for managing project permissions
 * Extracted by RefactorX from ProjectDetailView
 */

import { computed, type ComputedRef } from 'vue'
import type { Project, UserSummary } from '../types/project.types'
import { useAuthStore } from '@/stores/auth'

interface ProjectPermissions {
  canEdit: ComputedRef<boolean>
  canManageTeam: ComputedRef<boolean>
  canDelete: ComputedRef<boolean>
  canAddTasks: ComputedRef<boolean>
  canManageSprints: ComputedRef<boolean>
  isOwner: ComputedRef<boolean>
  isMember: ComputedRef<boolean>
}

/**
 * Returns computed permissions for a project based on current user
 */
export function useProjectPermissions(
  project: ComputedRef<Project | null | undefined>
): ProjectPermissions {
  const authStore = useAuthStore()

  const isOwner = computed(() => {
    if (!project.value || !authStore.user) return false
    return project.value.owner?.public_id === authStore.user.public_id
  })

  const isMember = computed(() => {
    if (!project.value || !authStore.user) return false
    
    // Owner is always a member
    if (isOwner.value) return true
    
    // Check if user is in memberships
    const memberships = project.value.memberships || []
    return memberships.some(
      membership => membership.user?.public_id === authStore.user?.public_id
    )
  })

  const canEdit = computed(() => {
    if (!project.value || !authStore.user) return false
    
    // Owner can always edit
    if (isOwner.value) return true
    
    // Check if user has admin or manager role in the project
    const memberships = project.value.memberships || []
    const userMembership = memberships.find(
      m => m.user?.public_id === authStore.user?.public_id
    )
    
    return userMembership?.role === 'admin' || userMembership?.role === 'manager'
  })

  const canManageTeam = computed(() => {
    if (!project.value || !authStore.user) return false
    
    // Only owner and admins can manage team
    if (isOwner.value) return true
    
    const memberships = project.value.memberships || []
    const userMembership = memberships.find(
      m => m.user?.public_id === authStore.user?.public_id
    )
    
    return userMembership?.role === 'admin'
  })

  const canDelete = computed(() => {
    // Only owner can delete the project
    return isOwner.value
  })

  const canAddTasks = computed(() => {
    // Any member can add tasks
    return isMember.value
  })

  const canManageSprints = computed(() => {
    // Owner, admin, and manager can manage sprints
    return canEdit.value
  })

  return {
    canEdit,
    canManageTeam,
    canDelete,
    canAddTasks,
    canManageSprints,
    isOwner,
    isMember
  }
}

/**
 * Check if a user can perform an action on a task
 */
export function useTaskPermissions(
  task: ComputedRef<{ assignee?: UserSummary | null } | null>,
  projectPermissions: ProjectPermissions
) {
  const authStore = useAuthStore()

  const isAssignee = computed(() => {
    if (!task.value || !authStore.user) return false
    return task.value.assignee?.public_id === authStore.user.public_id
  })

  const canEditTask = computed(() => {
    // Project editors, task assignee can edit
    return projectPermissions.canEdit.value || isAssignee.value
  })

  const canDeleteTask = computed(() => {
    // Only project editors can delete tasks
    return projectPermissions.canEdit.value
  })

  const canAssignTask = computed(() => {
    // Project editors can assign tasks
    return projectPermissions.canEdit.value
  })

  const canChangeTaskStatus = computed(() => {
    // Assignee and project editors can change status
    return isAssignee.value || projectPermissions.canEdit.value
  })

  return {
    isAssignee,
    canEditTask,
    canDeleteTask,
    canAssignTask,
    canChangeTaskStatus
  }
}
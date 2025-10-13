<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Project Detail -->
    <div v-else-if="project" class="py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Header -->
        <ProjectHeader
          :project="project"
          :can-edit="permissions.canEdit.value"
          :can-manage-team="permissions.canManageTeam.value"
          @manage-team="modals.openTeamModal"
          @edit-project="modals.openEditModal"
          @add-task="modals.openTaskModal"
        />

        <!-- Tabs -->
        <div class="mt-8">
          <ProjectTabs
            :tabs="tabs"
            :active-tab="activeTab"
            @update:active-tab="activeTab = $event"
          />
        </div>

        <!-- Tab Content -->
        <div class="mt-8">
          <!-- Tasks Tab -->
          <div v-if="activeTab === 'tasks'">
            <TaskBoard
              :tasks="taskStore.projectTasks || []"
              :loading="taskStore.loading"
              @update-status="handleTaskStatusUpdate"
              @create-task="handleCreateTask"
              @edit-task="handleEditTask"
              @duplicate-task="handleDuplicateTask"
              @delete-task="handleDeleteTask"
              @task-click="handleTaskClick"
            />
          </div>

          <!-- Team Tab -->
          <div v-else-if="activeTab === 'team'">
            <TeamMembersList
              :members="project.memberships || []"
              :can-manage="permissions.canManageTeam.value"
              @remove="handleRemoveMember"
            />
          </div>

          <!-- Sprints Tab -->
          <div v-else-if="activeTab === 'sprints'">
            <SprintList
              :sprints="sprintStore.projectSprints"
              :can-manage="permissions.canEdit.value"
              :loading="sprintStore.loading"
              @create="handleCreateSprint"
              @edit="handleEditSprint"
              @delete="handleDeleteSprint"
              @activate="handleActivateSprint"
              @deactivate="handleDeactivateSprint"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <ProjectFormModal
      :show="modals.showEditModal.value"
      :project="project"
      @close="modals.closeEditModal"
      @save="handleUpdateProject"
    />

    <!-- Task Form Modal -->
    <TaskFormModal
      ref="taskModalRef"
      :show="modals.showTaskModal.value"
      :task="modals.editingTask.value"
      :project-id="project?.public_id || ''"
      :available-assignees="project?.memberships?.map((m) => m.user).filter(Boolean) || []"
      @close="modals.closeTaskModal"
      @save="handleSaveTask"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      :is-open="showDeleteConfirm"
      :title="deleteConfirmTitle"
      :message="deleteConfirmMessage"
      type="danger"
      confirm-text="Delete"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />

    <!-- Team Management Modal -->
    <TeamManagementModal
      :show="modals.showTeamModal.value"
      :project-id="project?.public_id || ''"
      :members="project?.memberships || []"
      @close="modals.closeTeamModal"
      @member-added="handleMemberAdded"
      @member-removed="handleMemberRemoved"
      @member-updated="handleMemberUpdated"
    />

    <!-- Sprint Form Modal -->
    <SprintFormModal
      :show="modals.showSprintModal.value"
      :sprint="editingSprint"
      :project-id="project?.public_id || ''"
      @close="closeSprintModal"
      @save="handleSaveSprint"
    />

    <!-- Sprint Delete Confirmation -->
    <ConfirmDialog
      :is-open="showSprintDeleteConfirm"
      title="Delete Sprint"
      :message="sprintDeleteMessage"
      type="danger"
      confirm-text="Delete"
      @confirm="confirmDeleteSprint"
      @cancel="cancelDeleteSprint"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'
import { useTaskStore } from '../stores/taskStore'
import { useSprintStore } from '../stores/sprintStore'
import { useAuthStore } from '@/stores/auth'
import { useProjectPermissions } from '../composables/useProjectPermissions'
import { useProjectModals } from '../composables/useProjectModals'
import ProjectHeader from '../components/ProjectHeader.vue'
import ProjectTabs from '../components/ProjectTabs.vue'
import ProjectFormModal from '../components/ProjectFormModal.vue'
import TaskBoard from '../components/TaskBoard.vue'
import TaskFormModal from '../components/TaskFormModal.vue'
import TeamMembersList from '../components/TeamMembersList.vue'
import SprintList from '../components/SprintList.vue'
import TeamManagementModal from '../components/TeamManagementModal.vue'
import SprintFormModal from '../components/SprintFormModal.vue'
import ConfirmDialog from '@/shared/components/ConfirmDialog.vue'
import type {
  ProjectForm,
  TaskStatus,
  Task,
  TaskForm,
  ProjectMembership,
  Sprint,
  SprintForm,
} from '../types/project.types'
import { getUserDisplayName } from '@/utils/userHelpers'
import { formatDate } from '@/utils/dateHelpers'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const sprintStore = useSprintStore()
const authStore = useAuthStore()

// State
const loading = ref(true)
const activeTab = ref('tasks')
const taskModalRef = ref()
const initialTaskStatus = ref<TaskStatus>('todo')

// Delete confirmation state
const showDeleteConfirm = ref(false)
const deletingTask = ref<Task | null>(null)
const deleteConfirmTitle = ref('')
const deleteConfirmMessage = ref('')

// Sprint-related state
const editingSprint = ref<Sprint | null>(null)
const showSprintDeleteConfirm = ref(false)
const deletingSprint = ref<Sprint | null>(null)
const sprintDeleteMessage = ref('')

// Computed
const project = computed(() => projectStore.currentProject)

// Composables
const permissions = useProjectPermissions(project)
const modals = useProjectModals()

const tabs = computed(() => [
  {
    id: 'tasks',
    name: 'Tasks',
    count: taskStore.projectTasks?.length || 0,
  },
  {
    id: 'team',
    name: 'Team',
    count: project.value?.memberships?.length || 0,
  },
  {
    id: 'sprints',
    name: 'Sprints',
    count: sprintStore.projectSprints?.length || 0,
  },
])

// Methods
async function loadProject() {
  loading.value = true
  try {
    const projectId = route.params.id as string
    await projectStore.fetchProject(projectId)
    // Fetch related data with the specialized stores
    await Promise.all([
      taskStore.fetchProjectTasks(projectId),
      sprintStore.fetchProjectSprints(projectId)
    ])
  } catch (error) {
    console.error('Failed to load project:', error)
    router.push({ name: 'projects' })
  } finally {
    loading.value = false
  }
}

async function handleUpdateProject(data: ProjectForm) {
  if (!project.value) return

  try {
    await projectStore.updateProject(project.value.public_id, data)
    // Close modal first
    modals.closeEditModal()
    // Wait for next tick before any UI updates
    await nextTick()
  } catch (error) {
    console.error('Failed to update project:', error)
  }
}

async function handleTaskStatusUpdate(taskId: string, status: TaskStatus) {
  await taskStore.updateTaskStatus(taskId, status)
}

// Task CRUD handlers
function handleCreateTask(initialStatus?: TaskStatus) {
  initialTaskStatus.value = initialStatus || 'todo'
  modals.openTaskModal()
}

function handleEditTask(task: Task) {
  modals.openTaskModal(task)
}

function handleDuplicateTask(task: Task) {
  // Create a copy without the ID and timestamps
  const duplicatedTask = {
    ...task,
    public_id: '', // Will be generated by backend
    title: `${task.title} (Copy)`,
    created_at: '',
    updated_at: '',
  }
  modals.openTaskModal(duplicatedTask)
}

function handleDeleteTask(task: Task) {
  deletingTask.value = task
  deleteConfirmTitle.value = 'Delete Task'
  deleteConfirmMessage.value = `Are you sure you want to delete "${task.title}"? This action cannot be undone.`
  showDeleteConfirm.value = true
}

function handleTaskClick(task: Task) {
  // Task click is handled by TaskBoard's TaskDetailModal
  console.log('Task clicked:', task.title)
}

function closeTaskModal() {
  modals.closeTaskModal()
  initialTaskStatus.value = 'todo'
}

async function handleSaveTask(taskData: TaskForm) {
  try {
    if (modals.editingTask.value) {
      // Update existing task
      await taskStore.updateTask(modals.editingTask.value.public_id, taskData)
    } else {
      // Create new task
      const formData = {
        ...taskData,
        status: initialTaskStatus.value,
        project_id: project.value?.public_id || '',
      }
      await taskStore.createTask(formData)
    }
    closeTaskModal()
  } catch (error: any) {
    console.error('Failed to save task:', error)
    // Pass server validation errors to modal
    if (taskModalRef.value && error.response?.data) {
      taskModalRef.value.handleServerError(error.response.data)
    } else if (taskModalRef.value) {
      // Clear loading state even on unexpected errors
      taskModalRef.value.loading = false
    }
  }
}

async function confirmDelete() {
  if (deletingTask.value) {
    try {
      await taskStore.deleteTask(deletingTask.value.public_id)
      cancelDelete()
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }
}

function cancelDelete() {
  showDeleteConfirm.value = false
  deletingTask.value = null
  deleteConfirmTitle.value = ''
  deleteConfirmMessage.value = ''
}

async function handleRemoveMember(memberId: string) {
  // This is called from TeamMembersList component
  if (!project.value) return

  try {
    await projectStore.removeProjectMember(project.value.public_id, memberId)
    await loadProject() // Reload to get updated memberships
  } catch (error) {
    console.error('Failed to remove member:', error)
  }
}

// Team Management Modal handlers
function handleMemberAdded(member: ProjectMembership) {
  // Add the new member to the current project's memberships
  if (project.value && project.value.memberships) {
    project.value.memberships.push(member)
  }
}

function handleMemberRemoved(memberId: string) {
  // Remove the member from the current project's memberships
  if (project.value && project.value.memberships) {
    project.value.memberships = project.value.memberships.filter((m) => m.public_id !== memberId)
  }
}

function handleMemberUpdated(updatedMember: ProjectMembership) {
  // Update the member's role in the current project's memberships
  if (project.value && project.value.memberships) {
    const index = project.value.memberships.findIndex(
      (m) => m.public_id === updatedMember.public_id,
    )
    if (index !== -1) {
      project.value.memberships[index] = updatedMember
    }
  }
}

// Sprint CRUD handlers
function handleCreateSprint() {
  editingSprint.value = null
  modals.openSprintModal()
}

function handleEditSprint(sprint: Sprint) {
  editingSprint.value = sprint
  modals.openSprintModal()
}

function handleDeleteSprint(sprint: Sprint) {
  deletingSprint.value = sprint
  sprintDeleteMessage.value = `Are you sure you want to delete sprint "${sprint.name}"? This action cannot be undone.`
  showSprintDeleteConfirm.value = true
}

async function handleActivateSprint(sprintId: string) {
  try {
    await sprintStore.activateSprint(sprintId)
  } catch (error) {
    console.error('Failed to activate sprint:', error)
  }
}

async function handleDeactivateSprint(sprintId: string) {
  try {
    await sprintStore.deactivateSprint(sprintId)
  } catch (error) {
    console.error('Failed to deactivate sprint:', error)
  }
}

function closeSprintModal() {
  modals.closeSprintModal()
  editingSprint.value = null
}

async function handleSaveSprint(sprintData: SprintForm) {
  try {
    if (editingSprint.value) {
      await sprintStore.updateSprint(editingSprint.value.public_id, sprintData)
    } else {
      await sprintStore.createSprint(sprintData)
    }
    closeSprintModal()
  } catch (error) {
    console.error('Failed to save sprint:', error)
    throw error // Re-throw to let the modal handle the error
  }
}

async function confirmDeleteSprint() {
  if (deletingSprint.value) {
    try {
      await sprintStore.deleteSprint(deletingSprint.value.public_id)
      cancelDeleteSprint()
    } catch (error) {
      console.error('Failed to delete sprint:', error)
    }
  }
}

function cancelDeleteSprint() {
  showSprintDeleteConfirm.value = false
  deletingSprint.value = null
  sprintDeleteMessage.value = ''
}


// Lifecycle
onMounted(() => {
  loadProject()
})

// Watch for route changes
watch(
  () => route.params.id,
  () => {
    if (route.name === 'project-detail') {
      loadProject()
    }
  },
)
</script>

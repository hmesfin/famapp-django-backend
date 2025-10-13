/**
 * Project Service Layer
 * Ham Dog & TC's API communication hub for projects!
 */
import api from '@/services/api'
import type {
  Project,
  ProjectForm,
  ProjectFilters,
  ProjectListResponse,
  ProjectMembership,
  Sprint,
  SprintForm,
  Task,
  TaskForm,
  TaskFilters,
  TaskListResponse,
  Comment,
  CommentForm,
  ProjectStats,
} from '../types/project.types'

class ProjectService {
  // Project CRUD operations
  async listProjects(filters?: ProjectFilters): Promise<ProjectListResponse> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.owner) params.append('owner', filters.owner)
    if (filters?.search) params.append('search', filters.search)

    const response = await api.get(`/projects/projects/?${params}`)
    return response
  }

  async getProject(publicId: string): Promise<Project> {
    const response = await api.get(`/projects/projects/${publicId}/`)
    return response
  }

  async createProject(data: ProjectForm): Promise<Project> {
    const response = await api.post(`/projects/projects/`, data)
    return response
  }

  async updateProject(publicId: string, data: Partial<ProjectForm>): Promise<Project> {
    const response = await api.patch(`/projects/projects/${publicId}/`, data)
    return response
  }

  async deleteProject(publicId: string): Promise<void> {
    await api.delete(`/projects/projects/${publicId}/`)
  }

  // Project team management
  async addProjectMember(
    projectId: string,
    userId: string,
    role: string,
  ): Promise<ProjectMembership> {
    const response = await api.post(`/projects/projects/${projectId}/add_member/`, {
      user_id: userId,
      role,
    })
    return response
  }

  async removeProjectMember(projectId: string, userId: string): Promise<void> {
    await api.delete(`/projects/projects/${projectId}/remove_member/`, {
      data: { user_id: userId },
    })
  }

  // Project statistics
  async getProjectStats(projectId: string): Promise<ProjectStats> {
    const response = await api.get(`/projects/projects/${projectId}/stats/`)
    return response
  }

  // Sprint operations
  async listSprints(projectId?: string): Promise<Sprint[]> {
    const params = projectId ? `?project=${projectId}` : ''
    const response = await api.get(`/projects/sprints/${params}`)
    // Handle both paginated and non-paginated responses
    if (Array.isArray(response)) {
      return response
    }
    return response?.results || response || []
  }

  async getSprint(publicId: string): Promise<Sprint> {
    const response = await api.get(`/projects/sprints/${publicId}/`)
    return response
  }

  async createSprint(data: SprintForm): Promise<Sprint> {
    const response = await api.post(`/projects/sprints/`, data)
    return response
  }

  async updateSprint(publicId: string, data: Partial<SprintForm>): Promise<Sprint> {
    const response = await api.patch(`/projects/sprints/${publicId}/`, data)
    return response
  }

  async activateSprint(publicId: string): Promise<Sprint> {
    const response = await api.post(`/projects/sprints/${publicId}/activate/`)
    return response
  }

  async deactivateSprint(publicId: string): Promise<Sprint> {
    const response = await api.post(`/projects/sprints/${publicId}/deactivate/`)
    return response
  }

  async deleteSprint(publicId: string): Promise<void> {
    await api.delete(`/projects/sprints/${publicId}/`)
  }

  // Task operations
  async listTasks(filters?: TaskFilters): Promise<TaskListResponse> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.assignee) params.append('assignee', filters.assignee)
    if (filters?.project) params.append('project', filters.project)
    if (filters?.sprint) params.append('sprint', filters.sprint)
    if (filters?.search) params.append('search', filters.search)

    const response = await api.get(`/projects/tasks/?${params}`)
    return response
  }

  async getTask(publicId: string): Promise<Task> {
    const response = await api.get(`/projects/tasks/${publicId}/`)
    return response
  }

  async createTask(data: TaskForm): Promise<Task> {
    const response = await api.post(`/projects/tasks/`, data)
    return response
  }

  async updateTask(publicId: string, data: Partial<TaskForm>): Promise<Task> {
    const response = await api.patch(`/projects/tasks/${publicId}/`, data)
    return response
  }

  async updateTaskStatus(publicId: string, status: string): Promise<Task> {
    const response = await api.patch(`/projects/tasks/${publicId}/update_status/`, { status })
    return response
  }

  async deleteTask(publicId: string): Promise<void> {
    await api.delete(`/projects/tasks/${publicId}/`)
  }

  // Comment operations
  async addComment(taskId: string, data: CommentForm): Promise<Comment> {
    const response = await api.post(`/projects/tasks/${taskId}/add_comment/`, data)
    return response
  }

  async updateComment(publicId: string, content: string): Promise<Comment> {
    const response = await api.patch(`/projects/comments/${publicId}/`, { content })
    return response
  }

  async deleteComment(publicId: string): Promise<void> {
    await api.delete(`/projects/comments/${publicId}/`)
  }

  // Helper methods for the Kanban board
  async getProjectTasks(projectId: string, filters?: TaskFilters): Promise<Task[]> {
    const taskFilters = { ...filters, project: projectId }
    const response = await this.listTasks(taskFilters)
    // Handle both paginated and non-paginated responses
    if (Array.isArray(response)) {
      return response
    }
    return response?.results || []
  }

  async moveTaskToSprint(taskId: string, sprintId: string | null): Promise<Task> {
    return this.updateTask(taskId, { sprint_id: sprintId || undefined })
  }

  async assignTask(taskId: string, userId: string | null): Promise<Task> {
    return this.updateTask(taskId, { assignee_id: userId || undefined })
  }
}

export default new ProjectService()

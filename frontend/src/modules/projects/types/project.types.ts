/**
 * Project Management Types
 * Ham Dog & TC's TypeScript definitions for the frontend crew!
 */

// User summary type (matches backend UserSummarySerializer)
export interface UserSummary {
  public_id: string
  email: string
  first_name: string
  last_name: string
  full_name?: string // Computed field from serializer
}

// Project types
export interface Project {
  public_id: string
  name: string
  slug: string
  description: string
  status: ProjectStatus
  owner: UserSummary
  member_count?: number
  task_count?: number
  start_date: string
  end_date?: string
  created_at: string
  updated_at?: string
  created_by?: UserSummary
  updated_by?: UserSummary
  memberships?: ProjectMembership[]
  active_sprint?: SprintSummary
  stats?: ProjectStats
}

export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'archived'

export interface ProjectStats {
  total_tasks: number
  completed_tasks: number
  in_progress_tasks: number
  blocked_tasks: number
}

// Project membership
export interface ProjectMembership {
  public_id: string
  user: UserSummary
  role: MemberRole
  joined_at: string
  created_at: string
  updated_at: string
}

export type MemberRole = 'owner' | 'manager' | 'developer' | 'designer' | 'viewer'

// Sprint types
export interface Sprint {
  public_id: string
  project?: Project
  name: string
  goal: string
  start_date: string
  end_date: string
  is_active: boolean
  task_count?: number
  stats?: SprintStats
  created_at: string
  updated_at: string
}

export interface SprintSummary {
  public_id: string
  name: string
  goal: string
  start_date: string
  end_date: string
  is_active: boolean
  task_count: number
}

export interface SprintStats {
  total_tasks: number
  completed_tasks: number
  total_story_points: number
  completed_story_points: number
  completion_percentage: number
}

// Task types
export interface Task {
  public_id: string
  project: Project | string
  sprint?: Sprint | string
  title: string
  description?: string
  assignee?: UserSummary
  status: TaskStatus
  priority: TaskPriority
  story_points: number
  due_date?: string
  comments?: Comment[]
  created_by?: UserSummary
  updated_by?: UserSummary
  created_at: string
  updated_at: string
}

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done' | 'blocked'
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical'

// Comment types
export interface Comment {
  public_id: string
  content: string
  author: UserSummary
  parent?: string
  replies?: Comment[]
  edited: boolean
  created_at: string
  updated_at: string
}

// Form types for creating/updating
export interface ProjectForm {
  name: string
  description: string
  status: ProjectStatus
  start_date: string
  end_date?: string
}

export interface TaskForm {
  title: string
  description: string
  assignee_id?: string
  sprint_id?: string
  status: TaskStatus
  priority: TaskPriority
  story_points: number
  due_date?: string
  project_id?: string
}

export interface SprintForm {
  project_id: string
  name: string
  goal: string
  start_date: string
  end_date: string
}

export interface CommentForm {
  content: string
  parent?: string
}

// API response types
export interface ProjectListResponse {
  results: Project[]
  count: number
  next?: string
  previous?: string
}

export interface TaskListResponse {
  results: Task[]
  count: number
  next?: string
  previous?: string
}

// Filter types
export interface ProjectFilters {
  status?: ProjectStatus
  owner?: string
  search?: string
}

export interface TaskFilters {
  status?: TaskStatus
  priority?: TaskPriority
  assignee?: string
  project?: string
  sprint?: string
  search?: string
}
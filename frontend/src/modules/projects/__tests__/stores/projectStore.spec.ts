/**
 * ProjectStore Tests
 * Ham Dog & TC's store testing suite
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProjectStore } from '../../stores/projectStore'
import { projectService } from '../../services/projectService'
import { mockProject, mockApiResponses, mockUser } from '../test-utils'

// Mock the service
vi.mock('../../services/projectService', () => ({
  projectService: {
    getProjects: vi.fn(),
    getProject: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
    addTeamMember: vi.fn(),
    removeTeamMember: vi.fn(),
    searchUsers: vi.fn()
  }
}))

describe('ProjectStore', () => {
  let store: ReturnType<typeof useProjectStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useProjectStore()
    vi.clearAllMocks()
  })

  describe('State Management', () => {
    it('initializes with default state', () => {
      expect(store.projects).toEqual([])
      expect(store.currentProject).toBeNull()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.currentPage).toBe(1)
      expect(store.totalPages).toBe(1)
      expect(store.totalCount).toBe(0)
    })

    it('sets projects correctly', () => {
      store.setProjects([mockProject])
      expect(store.projects).toEqual([mockProject])
    })

    it('sets current project correctly', () => {
      store.setCurrentProject(mockProject)
      expect(store.currentProject).toEqual(mockProject)
    })

    it('sets pagination info correctly', () => {
      store.setPagination({
        currentPage: 2,
        totalPages: 5,
        totalCount: 100
      })

      expect(store.currentPage).toBe(2)
      expect(store.totalPages).toBe(5)
      expect(store.totalCount).toBe(100)
    })
  })

  describe('Getters', () => {
    it('getUserProjects returns projects owned by user', () => {
      const ownedProject = { ...mockProject, owner: mockUser }
      const otherProject = { ...mockProject, public_id: 'other-123', owner: { ...mockUser, public_id: 'other-user' } }
      
      store.setProjects([ownedProject, otherProject])
      
      const userProjects = store.getUserProjects(mockUser.public_id)
      expect(userProjects).toHaveLength(1)
      expect(userProjects[0]).toEqual(ownedProject)
    })

    it('getProjectById returns correct project', () => {
      const project1 = { ...mockProject, public_id: 'proj-1' }
      const project2 = { ...mockProject, public_id: 'proj-2' }
      
      store.setProjects([project1, project2])
      
      expect(store.getProjectById('proj-1')).toEqual(project1)
      expect(store.getProjectById('proj-2')).toEqual(project2)
      expect(store.getProjectById('proj-3')).toBeUndefined()
    })

    it('getActiveProjects returns only active projects', () => {
      const activeProject = { ...mockProject, status: 'active' }
      const archivedProject = { ...mockProject, public_id: 'arch-123', status: 'archived' }
      const completedProject = { ...mockProject, public_id: 'comp-123', status: 'completed' }
      
      store.setProjects([activeProject, archivedProject, completedProject])
      
      const activeProjects = store.getActiveProjects
      expect(activeProjects).toHaveLength(1)
      expect(activeProjects[0].status).toBe('active')
    })

    it('hasProjects returns correct boolean', () => {
      expect(store.hasProjects).toBe(false)
      
      store.setProjects([mockProject])
      expect(store.hasProjects).toBe(true)
    })
  })

  describe('Actions - Fetching', () => {
    it('fetchProjects retrieves and sets projects', async () => {
      vi.mocked(projectService.getProjects).mockResolvedValue(mockApiResponses.projects.list)

      await store.fetchProjects()

      expect(projectService.getProjects).toHaveBeenCalledWith({ page: 1 })
      expect(store.projects).toEqual([mockProject])
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('fetchProjects handles pagination', async () => {
      const paginatedResponse = {
        results: [mockProject],
        count: 50,
        next: 'http://api/projects/?page=3',
        previous: 'http://api/projects/?page=1'
      }
      
      vi.mocked(projectService.getProjects).mockResolvedValue(paginatedResponse)

      await store.fetchProjects(2)

      expect(projectService.getProjects).toHaveBeenCalledWith({ page: 2 })
      expect(store.currentPage).toBe(2)
      expect(store.totalCount).toBe(50)
    })

    it('fetchProjects handles errors', async () => {
      const error = new Error('API Error')
      vi.mocked(projectService.getProjects).mockRejectedValue(error)

      await store.fetchProjects()

      expect(store.loading).toBe(false)
      expect(store.error).toBe('API Error')
      expect(store.projects).toEqual([])
    })

    it('fetchProject retrieves single project', async () => {
      vi.mocked(projectService.getProject).mockResolvedValue(mockProject)

      await store.fetchProject('proj-123')

      expect(projectService.getProject).toHaveBeenCalledWith('proj-123')
      expect(store.currentProject).toEqual(mockProject)
    })

    it('fetchProject handles errors', async () => {
      const error = new Error('Not found')
      vi.mocked(projectService.getProject).mockRejectedValue(error)

      await store.fetchProject('invalid-id')

      expect(store.error).toBe('Not found')
      expect(store.currentProject).toBeNull()
    })
  })

  describe('Actions - CRUD Operations', () => {
    it('createProject adds new project', async () => {
      const newProject = { ...mockProject, public_id: 'new-123' }
      vi.mocked(projectService.createProject).mockResolvedValue(newProject)

      const result = await store.createProject({
        name: 'New Project',
        description: 'Description'
      })

      expect(projectService.createProject).toHaveBeenCalledWith({
        name: 'New Project',
        description: 'Description'
      })
      expect(result).toEqual(newProject)
      expect(store.projects).toContainEqual(newProject)
    })

    it('updateProject modifies existing project', async () => {
      store.setProjects([mockProject])
      
      const updatedProject = { ...mockProject, name: 'Updated Name' }
      vi.mocked(projectService.updateProject).mockResolvedValue(updatedProject)

      const result = await store.updateProject('proj-123', { name: 'Updated Name' })

      expect(projectService.updateProject).toHaveBeenCalledWith('proj-123', { name: 'Updated Name' })
      expect(result).toEqual(updatedProject)
      expect(store.projects[0].name).toBe('Updated Name')
    })

    it('updateProject updates current project if matching', async () => {
      store.setCurrentProject(mockProject)
      
      const updatedProject = { ...mockProject, name: 'Updated Name' }
      vi.mocked(projectService.updateProject).mockResolvedValue(updatedProject)

      await store.updateProject('proj-123', { name: 'Updated Name' })

      expect(store.currentProject?.name).toBe('Updated Name')
    })

    it('deleteProject removes project from list', async () => {
      store.setProjects([mockProject])
      vi.mocked(projectService.deleteProject).mockResolvedValue(undefined)

      await store.deleteProject('proj-123')

      expect(projectService.deleteProject).toHaveBeenCalledWith('proj-123')
      expect(store.projects).toHaveLength(0)
    })

    it('deleteProject clears current project if matching', async () => {
      store.setProjects([mockProject])
      store.setCurrentProject(mockProject)
      vi.mocked(projectService.deleteProject).mockResolvedValue(undefined)

      await store.deleteProject('proj-123')

      expect(store.currentProject).toBeNull()
    })
  })

  describe('Actions - Team Management', () => {
    it('addTeamMember adds member to project', async () => {
      store.setCurrentProject(mockProject)
      
      const newMember = {
        user: mockUser,
        role: 'developer',
        joined_at: '2024-01-01T00:00:00Z'
      }
      
      const updatedProject = {
        ...mockProject,
        memberships: [...(mockProject.memberships || []), newMember]
      }
      
      vi.mocked(projectService.addTeamMember).mockResolvedValue(newMember)

      await store.addTeamMember('proj-123', 'user-123', 'developer')

      expect(projectService.addTeamMember).toHaveBeenCalledWith('proj-123', 'user-123', 'developer')
      expect(store.currentProject?.memberships).toContainEqual(newMember)
    })

    it('removeTeamMember removes member from project', async () => {
      const memberToRemove = {
        user: { ...mockUser, public_id: 'remove-user' },
        role: 'developer'
      }
      
      const projectWithMembers = {
        ...mockProject,
        memberships: [memberToRemove]
      }
      
      store.setCurrentProject(projectWithMembers)
      vi.mocked(projectService.removeTeamMember).mockResolvedValue(undefined)

      await store.removeTeamMember('proj-123', 'remove-user')

      expect(projectService.removeTeamMember).toHaveBeenCalledWith('proj-123', 'remove-user')
      expect(store.currentProject?.memberships).toHaveLength(0)
    })

    it('searchUsers returns user results', async () => {
      const users = [mockUser]
      vi.mocked(projectService.searchUsers).mockResolvedValue(users)

      const result = await store.searchUsers('test')

      expect(projectService.searchUsers).toHaveBeenCalledWith('test')
      expect(result).toEqual(users)
    })
  })

  describe('Actions - Filtering and Sorting', () => {
    it('filters projects by status', async () => {
      vi.mocked(projectService.getProjects).mockResolvedValue({
        results: [mockProject],
        count: 1
      })

      await store.fetchProjects(1, { status: 'active' })

      expect(projectService.getProjects).toHaveBeenCalledWith({
        page: 1,
        status: 'active'
      })
    })

    it('searches projects by name', async () => {
      vi.mocked(projectService.getProjects).mockResolvedValue({
        results: [mockProject],
        count: 1
      })

      await store.fetchProjects(1, { search: 'test' })

      expect(projectService.getProjects).toHaveBeenCalledWith({
        page: 1,
        search: 'test'
      })
    })

    it('sorts projects by field', async () => {
      vi.mocked(projectService.getProjects).mockResolvedValue({
        results: [mockProject],
        count: 1
      })

      await store.fetchProjects(1, { ordering: '-created_at' })

      expect(projectService.getProjects).toHaveBeenCalledWith({
        page: 1,
        ordering: '-created_at'
      })
    })
  })

  describe('Error Handling', () => {
    it('sets error state on failed operations', async () => {
      const error = new Error('Network error')
      vi.mocked(projectService.createProject).mockRejectedValue(error)

      try {
        await store.createProject({ name: 'Test' })
      } catch {
        // Expected to throw
      }

      expect(store.error).toBe('Network error')
    })

    it('clears error state on successful operations', async () => {
      store.setError('Previous error')
      vi.mocked(projectService.getProjects).mockResolvedValue(mockApiResponses.projects.list)

      await store.fetchProjects()

      expect(store.error).toBeNull()
    })
  })

  describe('Loading State', () => {
    it('sets loading state during fetch operations', async () => {
      vi.mocked(projectService.getProjects).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockApiResponses.projects.list), 100))
      )

      const promise = store.fetchProjects()
      expect(store.loading).toBe(true)

      await promise
      expect(store.loading).toBe(false)
    })

    it('sets loading state during create operations', async () => {
      vi.mocked(projectService.createProject).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockProject), 100))
      )

      const promise = store.createProject({ name: 'Test' })
      expect(store.loading).toBe(true)

      await promise
      expect(store.loading).toBe(false)
    })
  })

  describe('Reset and Cleanup', () => {
    it('resets store to initial state', () => {
      store.setProjects([mockProject])
      store.setCurrentProject(mockProject)
      store.setError('Some error')
      store.setPagination({ currentPage: 2, totalPages: 5, totalCount: 50 })

      store.resetStore()

      expect(store.projects).toEqual([])
      expect(store.currentProject).toBeNull()
      expect(store.error).toBeNull()
      expect(store.currentPage).toBe(1)
      expect(store.totalPages).toBe(1)
      expect(store.totalCount).toBe(0)
    })

    it('clears current project', () => {
      store.setCurrentProject(mockProject)
      store.clearCurrentProject()
      expect(store.currentProject).toBeNull()
    })
  })
})
/**
 * ProjectService Tests
 * Ham Dog & TC's API service testing
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { projectService } from '../../services/projectService'
import { mockProject, mockTask, mockSprint, mockComment, mockUser } from '../test-utils'

describe('ProjectService', () => {
  let fetchMock: any

  beforeEach(() => {
    fetchMock = vi.fn()
    global.fetch = fetchMock
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Project API Calls', () => {
    describe('getProjects', () => {
      it('fetches projects with default parameters', async () => {
        const mockResponse = {
          results: [mockProject],
          count: 1,
          next: null,
          previous: null
        }

        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })

        const result = await projectService.getProjects()

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/',
          expect.objectContaining({
            method: 'GET',
            headers: expect.objectContaining({
              'Content-Type': 'application/json'
            })
          })
        )
        expect(result).toEqual(mockResponse)
      })

      it('fetches projects with query parameters', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ results: [] })
        })

        await projectService.getProjects({
          page: 2,
          status: 'active',
          search: 'test',
          ordering: '-created_at'
        })

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/?page=2&status=active&search=test&ordering=-created_at',
          expect.any(Object)
        )
      })

      it('handles API errors', async () => {
        fetchMock.mockResolvedValue({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error'
        })

        await expect(projectService.getProjects()).rejects.toThrow('Internal Server Error')
      })
    })

    describe('getProject', () => {
      it('fetches single project by ID', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve(mockProject)
        })

        const result = await projectService.getProject('proj-123')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/proj-123/',
          expect.objectContaining({
            method: 'GET'
          })
        )
        expect(result).toEqual(mockProject)
      })

      it('handles 404 errors', async () => {
        fetchMock.mockResolvedValue({
          ok: false,
          status: 404,
          statusText: 'Not Found'
        })

        await expect(projectService.getProject('invalid-id')).rejects.toThrow('Not Found')
      })
    })

    describe('createProject', () => {
      it('creates new project', async () => {
        const projectData = {
          name: 'New Project',
          description: 'Description',
          status: 'planning',
          start_date: '2024-01-01',
          end_date: '2024-12-31'
        }

        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve(mockProject)
        })

        const result = await projectService.createProject(projectData)

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json'
            }),
            body: JSON.stringify(projectData)
          })
        )
        expect(result).toEqual(mockProject)
      })

      it('handles validation errors', async () => {
        const errorResponse = {
          name: ['This field is required'],
          start_date: ['Invalid date format']
        }

        fetchMock.mockResolvedValue({
          ok: false,
          status: 400,
          json: () => Promise.resolve(errorResponse)
        })

        await expect(projectService.createProject({})).rejects.toThrow()
      })
    })

    describe('updateProject', () => {
      it('updates existing project', async () => {
        const updates = { name: 'Updated Name' }

        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ ...mockProject, ...updates })
        })

        const result = await projectService.updateProject('proj-123', updates)

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/proj-123/',
          expect.objectContaining({
            method: 'PATCH',
            body: JSON.stringify(updates)
          })
        )
        expect(result.name).toBe('Updated Name')
      })

      it('handles concurrent update conflicts', async () => {
        fetchMock.mockResolvedValue({
          ok: false,
          status: 409,
          statusText: 'Conflict'
        })

        await expect(
          projectService.updateProject('proj-123', { name: 'Test' })
        ).rejects.toThrow('Conflict')
      })
    })

    describe('deleteProject', () => {
      it('deletes project', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          status: 204
        })

        await projectService.deleteProject('proj-123')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/proj-123/',
          expect.objectContaining({
            method: 'DELETE'
          })
        )
      })

      it('handles permission errors', async () => {
        fetchMock.mockResolvedValue({
          ok: false,
          status: 403,
          statusText: 'Forbidden'
        })

        await expect(projectService.deleteProject('proj-123')).rejects.toThrow('Forbidden')
      })
    })
  })

  describe('Team Management API Calls', () => {
    describe('addTeamMember', () => {
      it('adds team member to project', async () => {
        const memberData = {
          user: mockUser,
          role: 'developer'
        }

        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve(memberData)
        })

        const result = await projectService.addTeamMember('proj-123', 'user-456', 'developer')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/proj-123/add_member/',
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({
              user_id: 'user-456',
              role: 'developer'
            })
          })
        )
        expect(result).toEqual(memberData)
      })

      it('handles duplicate member errors', async () => {
        fetchMock.mockResolvedValue({
          ok: false,
          status: 400,
          json: () => Promise.resolve({
            error: 'User is already a member'
          })
        })

        await expect(
          projectService.addTeamMember('proj-123', 'user-456', 'developer')
        ).rejects.toThrow()
      })
    })

    describe('removeTeamMember', () => {
      it('removes team member from project', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          status: 204
        })

        await projectService.removeTeamMember('proj-123', 'user-456')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/projects/proj-123/remove_member/',
          expect.objectContaining({
            method: 'DELETE',
            body: JSON.stringify({ user_id: 'user-456' })
          })
        )
      })

      it('prevents removing project owner', async () => {
        fetchMock.mockResolvedValue({
          ok: false,
          status: 400,
          json: () => Promise.resolve({
            error: 'Cannot remove project owner'
          })
        })

        await expect(
          projectService.removeTeamMember('proj-123', 'owner-id')
        ).rejects.toThrow()
      })
    })

    describe('searchUsers', () => {
      it('searches for users by query', async () => {
        const users = [mockUser]

        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ results: users })
        })

        const result = await projectService.searchUsers('test@example')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/users/search/?q=test%40example',
          expect.objectContaining({
            method: 'GET'
          })
        )
        expect(result).toEqual(users)
      })

      it('handles empty search results', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ results: [] })
        })

        const result = await projectService.searchUsers('nonexistent')
        expect(result).toEqual([])
      })
    })
  })

  describe('Task API Calls', () => {
    describe('getTasks', () => {
      it('fetches tasks for project', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ results: [mockTask] })
        })

        const result = await projectService.getTasks('proj-123')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/tasks/?project=proj-123',
          expect.any(Object)
        )
        expect(result.results).toContain(mockTask)
      })

      it('filters tasks by status', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ results: [] })
        })

        await projectService.getTasks('proj-123', { status: 'done' })

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/tasks/?project=proj-123&status=done',
          expect.any(Object)
        )
      })
    })

    describe('createTask', () => {
      it('creates new task', async () => {
        const taskData = {
          title: 'New Task',
          description: 'Description',
          project_id: 'proj-123',
          status: 'todo'
        }

        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve(mockTask)
        })

        const result = await projectService.createTask(taskData)

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/tasks/',
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(taskData)
          })
        )
        expect(result).toEqual(mockTask)
      })
    })

    describe('updateTask', () => {
      it('updates task status', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ ...mockTask, status: 'done' })
        })

        const result = await projectService.updateTask('task-123', { status: 'done' })

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/tasks/task-123/',
          expect.objectContaining({
            method: 'PATCH',
            body: JSON.stringify({ status: 'done' })
          })
        )
        expect(result.status).toBe('done')
      })
    })
  })

  describe('Sprint API Calls', () => {
    describe('getSprints', () => {
      it('fetches sprints for project', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ results: [mockSprint] })
        })

        const result = await projectService.getSprints('proj-123')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/sprints/?project=proj-123',
          expect.any(Object)
        )
        expect(result.results).toContain(mockSprint)
      })
    })

    describe('activateSprint', () => {
      it('activates sprint', async () => {
        fetchMock.mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ ...mockSprint, is_active: true })
        })

        const result = await projectService.activateSprint('sprint-123')

        expect(fetchMock).toHaveBeenCalledWith(
          '/api/sprints/sprint-123/activate/',
          expect.objectContaining({
            method: 'POST'
          })
        )
        expect(result.is_active).toBe(true)
      })
    })
  })

  describe('Error Handling', () => {
    it('includes authentication headers when token exists', async () => {
      // Mock localStorage
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
      getItemSpy.mockReturnValue('test-token')

      fetchMock.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({})
      })

      await projectService.getProjects()

      expect(fetchMock).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      )

      getItemSpy.mockRestore()
    })

    it('handles network errors', async () => {
      fetchMock.mockRejectedValue(new Error('Network error'))

      await expect(projectService.getProjects()).rejects.toThrow('Network error')
    })

    it('handles timeout errors', async () => {
      fetchMock.mockImplementation(() => 
        new Promise((resolve) => {
          setTimeout(() => resolve({ ok: true }), 10000)
        })
      )

      const controller = new AbortController()
      setTimeout(() => controller.abort(), 100)

      await expect(
        projectService.getProjects({ signal: controller.signal })
      ).rejects.toThrow()
    })

    it('parses error messages from response body', async () => {
      fetchMock.mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          detail: 'Custom error message'
        })
      })

      await expect(projectService.getProjects()).rejects.toThrow('Custom error message')
    })
  })

  describe('Request Formatting', () => {
    it('handles special characters in URLs', async () => {
      fetchMock.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({})
      })

      await projectService.getProjects({
        search: 'test@example.com & special chars'
      })

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('test%40example.com%20%26%20special%20chars'),
        expect.any(Object)
      )
    })

    it('omits undefined values from request body', async () => {
      fetchMock.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({})
      })

      await projectService.createProject({
        name: 'Test',
        description: undefined,
        status: null
      })

      const callArgs = fetchMock.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      
      expect(body).toHaveProperty('name', 'Test')
      expect(body).not.toHaveProperty('description')
      expect(body).toHaveProperty('status', null)
    })
  })
})
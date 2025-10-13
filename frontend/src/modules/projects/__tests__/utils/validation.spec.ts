/**
 * Validation Utility Tests
 * Ham Dog & TC's validation testing
 */
import { describe, it, expect } from 'vitest'
import { 
  projectValidationSchema,
  taskValidationSchema,
  sprintValidationSchema,
  teamMemberValidationSchema
} from '../../utils/validation'

describe('Project Validation', () => {
  describe('projectValidationSchema', () => {
    it('validates valid project data', async () => {
      const validData = {
        name: 'Test Project',
        description: 'A test project description',
        status: 'active',
        start_date: '2024-01-01',
        end_date: '2024-12-31'
      }

      await expect(projectValidationSchema.validate(validData)).resolves.toEqual(validData)
    })

    it('requires project name', async () => {
      const invalidData = {
        description: 'Missing name',
        status: 'active'
      }

      await expect(projectValidationSchema.validate(invalidData))
        .rejects.toThrow('name is a required field')
    })

    it('validates name minimum length', async () => {
      const invalidData = {
        name: 'ab',
        description: 'Too short name'
      }

      await expect(projectValidationSchema.validate(invalidData))
        .rejects.toThrow('name must be at least 3 characters')
    })

    it('validates name maximum length', async () => {
      const invalidData = {
        name: 'a'.repeat(256),
        description: 'Too long name'
      }

      await expect(projectValidationSchema.validate(invalidData))
        .rejects.toThrow('name must be at most 255 characters')
    })

    it('validates status values', async () => {
      const invalidData = {
        name: 'Test Project',
        status: 'invalid_status'
      }

      await expect(projectValidationSchema.validate(invalidData))
        .rejects.toThrow('status must be one of the following values')
    })

    it('validates date format', async () => {
      const invalidData = {
        name: 'Test Project',
        start_date: 'invalid-date'
      }

      await expect(projectValidationSchema.validate(invalidData))
        .rejects.toThrow('start_date must be a valid date')
    })

    it('validates end date after start date', async () => {
      const invalidData = {
        name: 'Test Project',
        start_date: '2024-12-31',
        end_date: '2024-01-01'
      }

      await expect(projectValidationSchema.validate(invalidData))
        .rejects.toThrow('End date must be after start date')
    })

    it('allows null end date', async () => {
      const validData = {
        name: 'Test Project',
        description: 'Test',
        start_date: '2024-01-01',
        end_date: null
      }

      await expect(projectValidationSchema.validate(validData))
        .resolves.toEqual(validData)
    })
  })
})

describe('Task Validation', () => {
  describe('taskValidationSchema', () => {
    it('validates valid task data', async () => {
      const validData = {
        title: 'Test Task',
        description: 'Task description',
        status: 'todo',
        priority: 'medium',
        story_points: 5,
        assignee_id: 'user-123',
        due_date: '2024-12-31T23:59:59Z'
      }

      await expect(taskValidationSchema.validate(validData)).resolves.toEqual(validData)
    })

    it('requires task title', async () => {
      const invalidData = {
        description: 'Missing title',
        status: 'todo'
      }

      await expect(taskValidationSchema.validate(invalidData))
        .rejects.toThrow('title is a required field')
    })

    it('validates title minimum length', async () => {
      const invalidData = {
        title: 'ab',
        description: 'Too short title'
      }

      await expect(taskValidationSchema.validate(invalidData))
        .rejects.toThrow('title must be at least 3 characters')
    })

    it('validates status values', async () => {
      const validStatuses = ['todo', 'in_progress', 'review', 'done', 'blocked']
      
      for (const status of validStatuses) {
        const data = { title: 'Test Task', status }
        await expect(taskValidationSchema.validate(data)).resolves.toEqual(data)
      }

      const invalidData = { title: 'Test Task', status: 'invalid' }
      await expect(taskValidationSchema.validate(invalidData))
        .rejects.toThrow('status must be one of the following values')
    })

    it('validates priority values', async () => {
      const validPriorities = ['low', 'medium', 'high', 'critical']
      
      for (const priority of validPriorities) {
        const data = { title: 'Test Task', priority }
        await expect(taskValidationSchema.validate(data)).resolves.toEqual(data)
      }

      const invalidData = { title: 'Test Task', priority: 'urgent' }
      await expect(taskValidationSchema.validate(invalidData))
        .rejects.toThrow('priority must be one of the following values')
    })

    it('validates story points range', async () => {
      // Valid range: 1-21
      const validPoints = [1, 2, 3, 5, 8, 13, 21]
      for (const points of validPoints) {
        const data = { title: 'Test Task', story_points: points }
        await expect(taskValidationSchema.validate(data)).resolves.toEqual(data)
      }

      // Invalid: too low
      await expect(taskValidationSchema.validate({ title: 'Test', story_points: 0 }))
        .rejects.toThrow('story_points must be greater than or equal to 1')

      // Invalid: too high
      await expect(taskValidationSchema.validate({ title: 'Test', story_points: 22 }))
        .rejects.toThrow('story_points must be less than or equal to 21')
    })

    it('validates due date format', async () => {
      const validFormats = [
        '2024-12-31T23:59:59Z',
        '2024-12-31T23:59:59.999Z',
        '2024-12-31'
      ]

      for (const due_date of validFormats) {
        const data = { title: 'Test Task', due_date }
        await expect(taskValidationSchema.validate(data)).resolves.toBeDefined()
      }

      const invalidData = { title: 'Test Task', due_date: 'not-a-date' }
      await expect(taskValidationSchema.validate(invalidData))
        .rejects.toThrow('due_date must be a valid date')
    })

    it('allows optional fields to be null or undefined', async () => {
      const minimalData = {
        title: 'Minimal Task'
      }

      const result = await taskValidationSchema.validate(minimalData)
      expect(result.title).toBe('Minimal Task')
      expect(result.description).toBeUndefined()
      expect(result.assignee_id).toBeUndefined()
      expect(result.due_date).toBeUndefined()
    })
  })
})

describe('Sprint Validation', () => {
  describe('sprintValidationSchema', () => {
    it('validates valid sprint data', async () => {
      const validData = {
        name: 'Sprint 1',
        goal: 'Complete user authentication',
        start_date: '2024-01-01',
        end_date: '2024-01-14',
        is_active: true
      }

      await expect(sprintValidationSchema.validate(validData)).resolves.toEqual(validData)
    })

    it('requires sprint name', async () => {
      const invalidData = {
        goal: 'Missing name',
        start_date: '2024-01-01',
        end_date: '2024-01-14'
      }

      await expect(sprintValidationSchema.validate(invalidData))
        .rejects.toThrow('name is a required field')
    })

    it('requires sprint goal', async () => {
      const invalidData = {
        name: 'Sprint 1',
        start_date: '2024-01-01',
        end_date: '2024-01-14'
      }

      await expect(sprintValidationSchema.validate(invalidData))
        .rejects.toThrow('goal is a required field')
    })

    it('validates sprint dates are required', async () => {
      const missingStart = {
        name: 'Sprint 1',
        goal: 'Test',
        end_date: '2024-01-14'
      }

      await expect(sprintValidationSchema.validate(missingStart))
        .rejects.toThrow('start_date is a required field')

      const missingEnd = {
        name: 'Sprint 1',
        goal: 'Test',
        start_date: '2024-01-01'
      }

      await expect(sprintValidationSchema.validate(missingEnd))
        .rejects.toThrow('end_date is a required field')
    })

    it('validates end date after start date', async () => {
      const invalidData = {
        name: 'Sprint 1',
        goal: 'Test',
        start_date: '2024-01-14',
        end_date: '2024-01-01'
      }

      await expect(sprintValidationSchema.validate(invalidData))
        .rejects.toThrow('End date must be after start date')
    })

    it('validates sprint duration', async () => {
      // Too short (less than 1 week)
      const tooShort = {
        name: 'Sprint 1',
        goal: 'Test',
        start_date: '2024-01-01',
        end_date: '2024-01-03'
      }

      await expect(sprintValidationSchema.validate(tooShort))
        .rejects.toThrow('Sprint must be at least 7 days')

      // Too long (more than 4 weeks)
      const tooLong = {
        name: 'Sprint 1',
        goal: 'Test',
        start_date: '2024-01-01',
        end_date: '2024-02-15'
      }

      await expect(sprintValidationSchema.validate(tooLong))
        .rejects.toThrow('Sprint cannot be longer than 28 days')
    })

    it('validates is_active is boolean', async () => {
      const validData = {
        name: 'Sprint 1',
        goal: 'Test',
        start_date: '2024-01-01',
        end_date: '2024-01-14',
        is_active: 'yes'
      }

      await expect(sprintValidationSchema.validate(validData))
        .rejects.toThrow('is_active must be a boolean')
    })
  })
})

describe('Team Member Validation', () => {
  describe('teamMemberValidationSchema', () => {
    it('validates valid team member data', async () => {
      const validData = {
        user_id: 'user-123',
        role: 'developer'
      }

      await expect(teamMemberValidationSchema.validate(validData))
        .resolves.toEqual(validData)
    })

    it('requires user_id', async () => {
      const invalidData = {
        role: 'developer'
      }

      await expect(teamMemberValidationSchema.validate(invalidData))
        .rejects.toThrow('user_id is a required field')
    })

    it('requires role', async () => {
      const invalidData = {
        user_id: 'user-123'
      }

      await expect(teamMemberValidationSchema.validate(invalidData))
        .rejects.toThrow('role is a required field')
    })

    it('validates role values', async () => {
      const validRoles = ['owner', 'manager', 'developer', 'designer', 'viewer']
      
      for (const role of validRoles) {
        const data = { user_id: 'user-123', role }
        await expect(teamMemberValidationSchema.validate(data)).resolves.toEqual(data)
      }

      const invalidData = { user_id: 'user-123', role: 'admin' }
      await expect(teamMemberValidationSchema.validate(invalidData))
        .rejects.toThrow('role must be one of the following values')
    })

    it('validates user_id format', async () => {
      const invalidData = {
        user_id: '',
        role: 'developer'
      }

      await expect(teamMemberValidationSchema.validate(invalidData))
        .rejects.toThrow('user_id is a required field')
    })
  })
})

describe('Custom Validation Rules', () => {
  it('trims whitespace from string fields', async () => {
    const dataWithWhitespace = {
      name: '  Test Project  ',
      description: '  Description with spaces  ',
      status: 'active'
    }

    const result = await projectValidationSchema.validate(dataWithWhitespace)
    expect(result.name).toBe('Test Project')
    expect(result.description).toBe('Description with spaces')
  })

  it('handles null vs undefined correctly', async () => {
    const withNull = {
      title: 'Test Task',
      description: null,
      assignee_id: null
    }

    const withUndefined = {
      title: 'Test Task',
      description: undefined,
      assignee_id: undefined
    }

    const resultNull = await taskValidationSchema.validate(withNull)
    expect(resultNull.description).toBeNull()
    expect(resultNull.assignee_id).toBeNull()

    const resultUndefined = await taskValidationSchema.validate(withUndefined)
    expect(resultUndefined.description).toBeUndefined()
    expect(resultUndefined.assignee_id).toBeUndefined()
  })

  it('provides helpful error messages', async () => {
    const invalidProject = {
      name: 'Te',
      status: 'invalid',
      start_date: '2024-12-31',
      end_date: '2024-01-01'
    }

    try {
      await projectValidationSchema.validate(invalidProject, { abortEarly: false })
    } catch (error: any) {
      expect(error.errors).toContain('name must be at least 3 characters')
      expect(error.errors).toContain('status must be one of the following values: planning, active, on_hold, completed, archived')
      expect(error.errors).toContain('End date must be after start date')
    }
  })
})
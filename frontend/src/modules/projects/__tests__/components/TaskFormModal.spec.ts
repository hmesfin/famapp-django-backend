/**
 * TaskFormModal Component Tests
 * Ham Dog & TC's task form testing suite
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import TaskFormModal from '../../components/TaskFormModal.vue'
import { mountComponent, mockTask, mockProject, mockUser, flushPromises } from '../test-utils'
import { useTaskStore } from '../../stores/taskStore'
import { useToastStore } from '@/shared/stores/toastStore'

describe('TaskFormModal', () => {
  let wrapper: any
  let taskStore: any
  let toastStore: any

  beforeEach(() => {
    vi.clearAllMocks()
    taskStore = useTaskStore()
    toastStore = useToastStore()
    
    // Mock store methods
    vi.spyOn(taskStore, 'createTask').mockResolvedValue(mockTask)
    vi.spyOn(taskStore, 'updateTask').mockResolvedValue(mockTask)
    vi.spyOn(toastStore, 'success').mockImplementation(() => {})
    vi.spyOn(toastStore, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('Rendering', () => {
    it('renders in create mode with empty form', () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })

      expect(wrapper.find('[data-testid="modal-title"]').text()).toBe('Create New Task')
      expect(wrapper.find('[data-testid="title-input"]').element.value).toBe('')
      expect(wrapper.find('[data-testid="description-input"]').element.value).toBe('')
    })

    it('renders in edit mode with populated form', () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject,
          task: mockTask
        }
      })

      expect(wrapper.find('[data-testid="modal-title"]').text()).toBe('Edit Task')
      expect(wrapper.find('[data-testid="title-input"]').element.value).toBe(mockTask.title)
      expect(wrapper.find('[data-testid="description-input"]').element.value).toBe(mockTask.description)
    })

    it('shows all form fields', () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })

      expect(wrapper.find('[data-testid="title-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="description-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="status-select"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="priority-select"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="assignee-select"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="story-points-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="due-date-input"]').exists()).toBe(true)
    })

    it('populates sprint dropdown when sprints available', () => {
      const projectWithSprints = {
        ...mockProject,
        sprints: [
          { public_id: 'sprint-1', name: 'Sprint 1' },
          { public_id: 'sprint-2', name: 'Sprint 2' }
        ]
      }

      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: projectWithSprints
        }
      })

      const sprintSelect = wrapper.find('[data-testid="sprint-select"]')
      expect(sprintSelect.exists()).toBe(true)
      
      const options = sprintSelect.findAll('option')
      expect(options.length).toBe(3) // None + 2 sprints
      expect(options[1].text()).toBe('Sprint 1')
      expect(options[2].text()).toBe('Sprint 2')
    })
  })

  describe('Form Validation', () => {
    beforeEach(() => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })
    })

    it('validates required title field', async () => {
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      await submitButton.trigger('click')
      await flushPromises()

      expect(wrapper.find('[data-testid="title-error"]').text()).toContain('Title is required')
      expect(taskStore.createTask).not.toHaveBeenCalled()
    })

    it('validates title minimum length', async () => {
      const titleInput = wrapper.find('[data-testid="title-input"]')
      await titleInput.setValue('ab')
      
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      await submitButton.trigger('click')
      await flushPromises()

      expect(wrapper.find('[data-testid="title-error"]').text()).toContain('at least 3 characters')
      expect(taskStore.createTask).not.toHaveBeenCalled()
    })

    it('validates story points range', async () => {
      const storyPointsInput = wrapper.find('[data-testid="story-points-input"]')
      await storyPointsInput.setValue('25')
      
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      await submitButton.trigger('click')
      await flushPromises()

      expect(wrapper.find('[data-testid="story-points-error"]').text()).toContain('between 1 and 21')
      expect(taskStore.createTask).not.toHaveBeenCalled()
    })

    it('validates due date is in future', async () => {
      const pastDate = new Date('2020-01-01').toISOString().split('T')[0]
      const dueDateInput = wrapper.find('[data-testid="due-date-input"]')
      await dueDateInput.setValue(pastDate)
      
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      await submitButton.trigger('click')
      await flushPromises()

      expect(wrapper.find('[data-testid="due-date-error"]').text()).toContain('must be in the future')
      expect(taskStore.createTask).not.toHaveBeenCalled()
    })
  })

  describe('Form Submission', () => {
    it('creates task with valid data', async () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })

      // Fill form
      await wrapper.find('[data-testid="title-input"]').setValue('New Task')
      await wrapper.find('[data-testid="description-input"]').setValue('Task description')
      await wrapper.find('[data-testid="status-select"]').setValue('todo')
      await wrapper.find('[data-testid="priority-select"]').setValue('high')
      await wrapper.find('[data-testid="story-points-input"]').setValue('5')

      // Submit
      await wrapper.find('[data-testid="submit-button"]').trigger('click')
      await flushPromises()

      expect(taskStore.createTask).toHaveBeenCalledWith({
        title: 'New Task',
        description: 'Task description',
        status: 'todo',
        priority: 'high',
        story_points: 5,
        project_id: mockProject.public_id,
        assignee_id: null,
        sprint_id: null,
        due_date: null
      })

      expect(toastStore.success).toHaveBeenCalledWith('Task created successfully!')
      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('task-saved')).toBeTruthy()
    })

    it('updates task with valid data', async () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject,
          task: mockTask
        }
      })

      // Modify form
      await wrapper.find('[data-testid="title-input"]').setValue('Updated Task')
      await wrapper.find('[data-testid="status-select"]').setValue('in_progress')

      // Submit
      await wrapper.find('[data-testid="submit-button"]').trigger('click')
      await flushPromises()

      expect(taskStore.updateTask).toHaveBeenCalledWith(
        mockTask.public_id,
        expect.objectContaining({
          title: 'Updated Task',
          status: 'in_progress'
        })
      )

      expect(toastStore.success).toHaveBeenCalledWith('Task updated successfully!')
      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('task-saved')).toBeTruthy()
    })

    it('handles submission errors', async () => {
      taskStore.createTask.mockRejectedValue(new Error('API Error'))

      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })

      await wrapper.find('[data-testid="title-input"]').setValue('New Task')
      await wrapper.find('[data-testid="submit-button"]').trigger('click')
      await flushPromises()

      expect(toastStore.error).toHaveBeenCalledWith(
        'Failed to save task',
        'API Error'
      )
      expect(wrapper.emitted('close')).toBeFalsy()
    })
  })

  describe('User Interactions', () => {
    beforeEach(() => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })
    })

    it('closes modal on cancel button click', async () => {
      const cancelButton = wrapper.find('[data-testid="cancel-button"]')
      await cancelButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('closes modal on escape key', async () => {
      await wrapper.trigger('keydown.escape')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('disables submit button while submitting', async () => {
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      
      // Start submission
      taskStore.createTask.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      await wrapper.find('[data-testid="title-input"]').setValue('New Task')
      await submitButton.trigger('click')

      expect(submitButton.attributes('disabled')).toBeDefined()
      expect(submitButton.text()).toContain('Saving...')
    })

    it('resets form when modal reopens', async () => {
      // Fill form
      await wrapper.find('[data-testid="title-input"]').setValue('New Task')
      await wrapper.find('[data-testid="description-input"]').setValue('Description')

      // Close and reopen
      await wrapper.setProps({ isOpen: false })
      await wrapper.setProps({ isOpen: true, task: null })

      expect(wrapper.find('[data-testid="title-input"]').element.value).toBe('')
      expect(wrapper.find('[data-testid="description-input"]').element.value).toBe('')
    })
  })

  describe('Assignee Selection', () => {
    it('populates assignee dropdown with team members', () => {
      const projectWithMembers = {
        ...mockProject,
        memberships: [
          { user: { public_id: 'user-1', email: 'user1@example.com', first_name: 'User', last_name: 'One' } },
          { user: { public_id: 'user-2', email: 'user2@example.com', first_name: 'User', last_name: 'Two' } }
        ]
      }

      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: projectWithMembers
        }
      })

      const assigneeSelect = wrapper.find('[data-testid="assignee-select"]')
      const options = assigneeSelect.findAll('option')
      
      expect(options.length).toBe(3) // Unassigned + 2 members
      expect(options[1].text()).toContain('User One')
      expect(options[2].text()).toContain('User Two')
    })

    it('preselects current assignee in edit mode', () => {
      const taskWithAssignee = {
        ...mockTask,
        assignee: { public_id: 'user-1', email: 'user1@example.com' }
      }

      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject,
          task: taskWithAssignee
        }
      })

      const assigneeSelect = wrapper.find('[data-testid="assignee-select"]')
      expect(assigneeSelect.element.value).toBe('user-1')
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })

      const modal = wrapper.find('[role="dialog"]')
      expect(modal.exists()).toBe(true)
      expect(modal.attributes('aria-modal')).toBe('true')
      expect(modal.attributes('aria-labelledby')).toBeDefined()
    })

    it('traps focus within modal', async () => {
      wrapper = mountComponent(TaskFormModal, {
        props: {
          isOpen: true,
          project: mockProject
        }
      })

      const firstInput = wrapper.find('[data-testid="title-input"]')
      const lastButton = wrapper.find('[data-testid="cancel-button"]')

      // Focus should start on first input
      await nextTick()
      expect(document.activeElement).toBe(firstInput.element)

      // Tab from last element should cycle to first
      await lastButton.trigger('keydown.tab')
      await nextTick()
      expect(document.activeElement).toBe(firstInput.element)
    })
  })
})
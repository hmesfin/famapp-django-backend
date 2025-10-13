/**
 * ProjectCard Component Tests
 * Ham Dog & TC's comprehensive component testing
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import ProjectCard from '../../components/ProjectCard.vue'
import { mountComponent, mockProject, mockRouter } from '../test-utils'
import { useProjectStore } from '../../stores/projectStore'

describe('ProjectCard', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('Rendering', () => {
    it('renders project information correctly', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject
        }
      })

      expect(wrapper.text()).toContain(mockProject.name)
      expect(wrapper.text()).toContain(mockProject.description)
      expect(wrapper.text()).toContain('Active')
    })

    it('displays correct status badge color', () => {
      const statuses = [
        { status: 'active', class: 'bg-green-100' },
        { status: 'planning', class: 'bg-blue-100' },
        { status: 'on_hold', class: 'bg-yellow-100' },
        { status: 'completed', class: 'bg-gray-100' },
        { status: 'archived', class: 'bg-red-100' }
      ]

      statuses.forEach(({ status, class: expectedClass }) => {
        const project = { ...mockProject, status }
        wrapper = mountComponent(ProjectCard, {
          props: { project }
        })

        const badge = wrapper.find('[data-testid="status-badge"]')
        expect(badge.classes()).toContain(expectedClass)
        wrapper.unmount()
      })
    })

    it('shows member count and task count', () => {
      const project = {
        ...mockProject,
        member_count: 5,
        task_count: 10
      }

      wrapper = mountComponent(ProjectCard, {
        props: { project }
      })

      expect(wrapper.text()).toContain('5 members')
      expect(wrapper.text()).toContain('10 tasks')
    })

    it('displays formatted dates', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject
        }
      })

      expect(wrapper.text()).toContain('Jan 1, 2024')
      expect(wrapper.text()).toContain('Dec 31, 2024')
    })
  })

  describe('User Interactions', () => {
    it('navigates to project detail on view click', async () => {
      const push = vi.spyOn(mockRouter, 'push')
      
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject
        }
      })

      const viewButton = wrapper.find('[data-testid="view-button"]')
      await viewButton.trigger('click')

      expect(push).toHaveBeenCalledWith({
        name: 'project-detail',
        params: { id: mockProject.public_id }
      })
    })

    it('emits edit event when edit button clicked', async () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canEdit: true
        }
      })

      const editButton = wrapper.find('[data-testid="edit-button"]')
      await editButton.trigger('click')

      expect(wrapper.emitted('edit')).toBeTruthy()
      expect(wrapper.emitted('edit')[0]).toEqual([mockProject])
    })

    it('emits delete event when delete button clicked', async () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canDelete: true
        }
      })

      const deleteButton = wrapper.find('[data-testid="delete-button"]')
      await deleteButton.trigger('click')

      expect(wrapper.emitted('delete')).toBeTruthy()
      expect(wrapper.emitted('delete')[0]).toEqual([mockProject])
    })

    it('shows dropdown menu on menu button click', async () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canEdit: true,
          canDelete: true
        }
      })

      const menuButton = wrapper.find('[data-testid="menu-button"]')
      expect(wrapper.find('[data-testid="dropdown-menu"]').exists()).toBe(false)

      await menuButton.trigger('click')
      await nextTick()

      expect(wrapper.find('[data-testid="dropdown-menu"]').exists()).toBe(true)
    })
  })

  describe('Permissions', () => {
    it('hides edit button when canEdit is false', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canEdit: false
        }
      })

      expect(wrapper.find('[data-testid="edit-button"]').exists()).toBe(false)
    })

    it('hides delete button when canDelete is false', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canDelete: false
        }
      })

      expect(wrapper.find('[data-testid="delete-button"]').exists()).toBe(false)
    })

    it('hides menu button when no actions available', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canEdit: false,
          canDelete: false
        }
      })

      expect(wrapper.find('[data-testid="menu-button"]').exists()).toBe(false)
    })
  })

  describe('Loading State', () => {
    it('shows skeleton loader when loading', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: null,
          loading: true
        }
      })

      expect(wrapper.find('[data-testid="skeleton-loader"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="project-content"]').exists()).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('handles missing project data gracefully', () => {
      const incompleteProject = {
        public_id: 'test-123',
        name: 'Test Project'
        // Missing other fields
      }

      wrapper = mountComponent(ProjectCard, {
        props: {
          project: incompleteProject
        }
      })

      expect(wrapper.text()).toContain('Test Project')
      expect(wrapper.find('[data-testid="view-button"]').exists()).toBe(true)
    })

    it('handles null dates gracefully', () => {
      const projectWithNullDates = {
        ...mockProject,
        start_date: null,
        end_date: null
      }

      wrapper = mountComponent(ProjectCard, {
        props: {
          project: projectWithNullDates
        }
      })

      expect(wrapper.text()).toContain('No dates set')
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject,
          canEdit: true,
          canDelete: true
        }
      })

      const viewButton = wrapper.find('[data-testid="view-button"]')
      expect(viewButton.attributes('aria-label')).toBe(`View ${mockProject.name}`)

      const editButton = wrapper.find('[data-testid="edit-button"]')
      expect(editButton.attributes('aria-label')).toBe(`Edit ${mockProject.name}`)

      const deleteButton = wrapper.find('[data-testid="delete-button"]')
      expect(deleteButton.attributes('aria-label')).toBe(`Delete ${mockProject.name}`)
    })

    it('has keyboard navigation support', async () => {
      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject
        }
      })

      const viewButton = wrapper.find('[data-testid="view-button"]')
      await viewButton.trigger('keydown.enter')

      expect(mockRouter.push).toHaveBeenCalled()
    })
  })

  describe('Dark Mode', () => {
    it('applies dark mode classes correctly', () => {
      // Mock dark mode
      document.documentElement.classList.add('dark')

      wrapper = mountComponent(ProjectCard, {
        props: {
          project: mockProject
        }
      })

      const card = wrapper.find('[data-testid="project-card"]')
      expect(card.classes()).toContain('dark:bg-gray-800')
      expect(card.classes()).toContain('dark:border-gray-700')

      // Clean up
      document.documentElement.classList.remove('dark')
    })
  })
})
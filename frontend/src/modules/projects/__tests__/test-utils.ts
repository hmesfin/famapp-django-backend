/**
 * Test utilities for projects module
 * Ham Dog & TC's testing helpers
 */
import { mount, VueWrapper } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { vi } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import type { Component } from 'vue'

// Mock router
export const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/projects', name: 'projects', component: { template: '<div>Projects</div>' } },
    { path: '/projects/:id', name: 'project-detail', component: { template: '<div>Project Detail</div>' } }
  ]
})

// Mock user data
export const mockUser = {
  public_id: 'user-123',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User'
}

// Mock project data
export const mockProject = {
  public_id: 'proj-123',
  name: 'Test Project',
  slug: 'test-project',
  description: 'A test project',
  status: 'active',
  owner: mockUser,
  memberships: [],
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mock task data
export const mockTask = {
  public_id: 'task-123',
  title: 'Test Task',
  description: 'A test task',
  status: 'todo',
  priority: 'medium',
  assignee: mockUser,
  project: mockProject,
  story_points: 5,
  due_date: '2024-12-31T00:00:00Z',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mock sprint data
export const mockSprint = {
  public_id: 'sprint-123',
  name: 'Sprint 1',
  goal: 'Complete MVP',
  start_date: '2024-01-01',
  end_date: '2024-01-14',
  is_active: true,
  project: mockProject,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mock comment data
export const mockComment = {
  public_id: 'comment-123',
  content: 'This is a test comment',
  author: mockUser,
  task: mockTask,
  edited: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mount component with common test setup
export function mountComponent(
  component: Component,
  options: any = {}
): VueWrapper {
  const defaultOptions = {
    global: {
      plugins: [
        createTestingPinia({
          createSpy: vi.fn,
          stubActions: false
        }),
        mockRouter
      ],
      stubs: {
        teleport: true,
        TransitionRoot: false,
        Dialog: false,
        DialogPanel: false
      }
    }
  }

  return mount(component, {
    ...defaultOptions,
    ...options,
    global: {
      ...defaultOptions.global,
      ...options.global,
      plugins: [
        ...(defaultOptions.global.plugins || []),
        ...(options.global?.plugins || [])
      ]
    }
  })
}

// Wait for async updates
export async function flushPromises(): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, 0)
  })
}

// Mock API responses
export const mockApiResponses = {
  projects: {
    list: { results: [mockProject], count: 1, next: null, previous: null },
    detail: mockProject,
    create: mockProject,
    update: mockProject
  },
  tasks: {
    list: { results: [mockTask], count: 1, next: null, previous: null },
    detail: mockTask,
    create: mockTask,
    update: mockTask
  },
  sprints: {
    list: { results: [mockSprint], count: 1, next: null, previous: null },
    detail: mockSprint,
    create: mockSprint,
    update: mockSprint
  },
  comments: {
    list: [mockComment],
    create: mockComment,
    update: mockComment
  }
}

// Mock fetch for API calls
export function setupMockFetch() {
  global.fetch = vi.fn()
  
  const mockFetch = (url: string, options?: any) => {
    const method = options?.method || 'GET'
    
    // Mock responses based on URL patterns
    if (url.includes('/api/projects/')) {
      if (method === 'GET') {
        if (url.endsWith('/')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockApiResponses.projects.list)
          })
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockApiResponses.projects.detail)
        })
      }
      if (method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockApiResponses.projects.create)
        })
      }
    }
    
    // Default response
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({})
    })
  }
  
  ;(global.fetch as any).mockImplementation(mockFetch)
  
  return global.fetch
}
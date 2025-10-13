import type { RouteRecordRaw } from 'vue-router'

export const projectRoutes = {
  dashboard: [
    {
      path: 'projects',
      name: 'projects',
      component: () => import('./views/ProjectListView.vue'),
      meta: {
        title: 'Projects',
        requiresAuth: true
      }
    },
    {
      path: 'projects/:id',
      name: 'project-detail',
      component: () => import('./views/ProjectDetailView.vue'),
      meta: {
        title: 'Project Details',
        requiresAuth: true
      }
    },
    {
      path: 'projects/:id/edit',
      name: 'project-edit',
      component: () => import('./views/ProjectDetailView.vue'),
      meta: {
        title: 'Edit Project',
        requiresAuth: true
      }
    },
    {
      path: 'projects/:id/board',
      name: 'project-board',
      component: () => import('./views/ProjectDetailView.vue'),
      meta: {
        title: 'Task Board',
        requiresAuth: true
      }
    }
  ] as RouteRecordRaw[]
}
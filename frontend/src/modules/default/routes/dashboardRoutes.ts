import type { RouteRecordRaw } from 'vue-router'

export const dashboardRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'dashboard',
    component: () => import('../views/dashboard/DashboardOverviewView.vue'),
    meta: {
      title: 'Dashboard',
      requiresAuth: true,
    },
  },
]
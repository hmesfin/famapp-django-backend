import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import module routes
import { authRoutes } from '@/modules/auth/routes'
import { defaultRoutes } from '@/modules/default/routes'
import { projectRoutes } from '@/modules/projects/routes'
import { invitationRoutes } from '@/modules/invitations/routes'
import { profileRoutes } from '@/modules/profiles/routes'

const routes: RouteRecordRaw[] = [
  // Public routes with DefaultLayout
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      // Default module public routes
      ...defaultRoutes.public,
      // Invitation public routes (accept invitation)
      ...invitationRoutes.public,
    ],
  },

  // Auth routes with AuthLayout
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      // Auth module public routes
      ...authRoutes.public,
    ],
  },

  // Dashboard routes with DashboardLayout
  {
    path: '/dashboard',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      // Default dashboard route
      ...defaultRoutes.dashboard,
      // Auth dashboard routes
      ...authRoutes.dashboard,
      // Project management routes
      ...projectRoutes.dashboard,
      // Invitation management routes
      ...invitationRoutes.dashboard,
      // Profile and settings routes
      ...profileRoutes.dashboard,
    ],
  },

  // Catch-all 404 route
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: 'Page Not Found',
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const isAuthRoute = to.path.startsWith('/auth/')
  const authStore = useAuthStore()

  console.log(
    'Router guard - to:',
    to.path,
    'requiresAuth:',
    requiresAuth,
    'isAuthRoute:',
    isAuthRoute,
    'isAuthenticated:',
    authStore.isAuthenticated,
  )

  if (requiresAuth && !authStore.isAuthenticated) {
    console.log('Blocking access, redirecting to login')
    // Redirect to login if not authenticated
    next({
      name: 'auth-login',
      query: { redirect: to.fullPath },
    })
  } else if (isAuthRoute && authStore.isAuthenticated) {
    console.log('User already authenticated, redirecting away from auth pages')
    // Redirect authenticated users away from auth pages (login, register, etc.)
    next('/dashboard')
  } else {
    console.log('Allowing access to:', to.path)
    // Set page title
    if (to.meta.title) {
      document.title = `${to.meta.title} | Django Vue Starter`
    } else {
      document.title = 'Django Vue Starter'
    }
    next()
  }
})

export default router

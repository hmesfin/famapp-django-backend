/**
 * Profile Routes Configuration
 * Routes for profile and settings management
 */
import type { RouteRecordRaw } from 'vue-router'

// Dashboard routes (authenticated)
export const profileRoutes = {
  dashboard: [
    {
      path: 'profiles',
      name: 'profile-list',
      component: () => import('../views/ProfileList.vue'),
      meta: {
        title: 'Browse Profiles',
        requiresAuth: true,
      },
    },
    {
      path: 'profile/:id',
      name: 'profile-view',
      component: () => import('../views/ProfileView.vue'),
      meta: {
        title: 'Profile',
        requiresAuth: true,
      },
      props: true,
    },
    {
      path: 'profile',
      name: 'profile-current',
      component: () => import('../views/ProfileEdit.vue'),
      meta: {
        title: 'My Profile',
        requiresAuth: true,
      },
    },
    {
      path: 'profile/edit',
      name: 'profile-edit',
      component: () => import('../views/ProfileEdit.vue'),
      meta: {
        title: 'Edit Profile',
        requiresAuth: true,
      },
    },
    {
      path: 'settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: {
        title: 'Settings',
        requiresAuth: true,
      },
    },
  ] as RouteRecordRaw[],

  // Public routes (if needed in the future)
  public: [] as RouteRecordRaw[],
}

import type { RouteRecordRaw } from 'vue-router'

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'home',
    component: () => import('../views/public/HomePageView.vue'),
    meta: {
      title: 'Home',
      requiresAuth: false,
    },
  },
  {
    path: 'features',
    name: 'features',
    component: () => import('../views/public/FeaturesPageView.vue'),
    meta: {
      title: 'Features',
      requiresAuth: false,
    },
  },
  {
    path: 'contact',
    name: 'contact',
    component: () => import('../views/public/ContactPageView.vue'),
    meta: {
      title: 'Contact',
      requiresAuth: false,
    },
  },
  {
    path: 'about',
    name: 'about',
    component: () => import('../views/public/AboutPageView.vue'),
    meta: {
      title: 'About',
      requiresAuth: false,
    },
  },
  {
    path: 'privacy',
    name: 'privacy',
    component: () => import('../views/public/PrivacyPageView.vue'),
    meta: {
      title: 'Privacy Policy',
      requiresAuth: false,
    },
  },
  {
    path: 'terms',
    name: 'terms',
    component: () => import('../views/public/TermsPageView.vue'),
    meta: {
      title: 'Terms of Service',
      requiresAuth: false,
    },
  },
]
import type { RouteRecordRaw } from 'vue-router'

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: 'login',
    name: 'auth-login',
    component: () => import('../views/public/LoginView.vue'),
    meta: {
      title: 'Sign In',
      requiresAuth: false,
    },
  },
  {
    path: 'register',
    name: 'auth-register',
    component: () => import('../views/public/RegisterView.vue'),
    meta: {
      title: 'Sign Up',
      requiresAuth: false,
    },
  },
  {
    path: 'forgot-password',
    name: 'auth-forgot-password',
    component: () => import('../views/public/ForgotPasswordView.vue'),
    meta: {
      title: 'Forgot Password',
      requiresAuth: false,
    },
  },
  {
    path: 'reset-password',
    name: 'auth-reset-password',
    component: () => import('../views/public/ResetPasswordView.vue'),
    meta: {
      title: 'Reset Password',
      requiresAuth: false,
    },
  },
  {
    path: 'verify-email',
    name: 'auth-verify-email',
    component: () => import('../views/public/EmailVerificationView.vue'),
    meta: {
      title: 'Verify Email',
      requiresAuth: false,
    },
  },
]
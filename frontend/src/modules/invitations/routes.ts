import type { RouteRecordRaw } from 'vue-router'

export const invitationRoutes = {
  dashboard: [
    {
      path: 'invitations',
      name: 'invitations',
      component: () => import('./views/dashboard/InvitationListView.vue'),
      meta: {
        title: 'Invitations',
        requiresAuth: true,
        requiresPermission: 'canViewAll',
      },
    },
    {
      path: 'invitations/send',
      name: 'invitation-send',
      component: () => import('./views/dashboard/InvitationSendView.vue'),
      meta: {
        title: 'Send Invitation',
        requiresAuth: true,
        requiresPermission: 'canSend',
      },
    },
    {
      path: 'invitations/my',
      name: 'my-invitations',
      component: () => import('./views/dashboard/MyInvitationsView.vue'),
      meta: {
        title: 'My Invitations',
        requiresAuth: true,
      },
    },
    {
      path: 'invitations/:id',
      name: 'invitation-detail',
      component: () => import('./views/dashboard/InvitationDetailView.vue'),
      meta: {
        title: 'Invitation Details',
        requiresAuth: true,
      },
    },
  ] as RouteRecordRaw[],

  public: [
    {
      path: '/invitations/accept',
      name: 'invitation-accept',
      component: () => import('./views/public/InvitationAcceptView.vue'),
      meta: {
        title: 'Accept Invitation',
        requiresAuth: false,
        isPublic: true,
      },
    },
  ] as RouteRecordRaw[],
}

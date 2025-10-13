/**
 * Invitation Stats Store - Focused on statistics and analytics
 * Ham Dog & TC's specialized store for invitation metrics!
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import invitationService from '../services/invitationService'
import { useAuthStore } from '@/stores/auth'
import type { InvitationStats } from '../types/invitation.types'

export const useInvitationStatsStore = defineStore('invitationStats', () => {
  const authStore = useAuthStore()

  // State - statistics and metrics
  const stats = ref<InvitationStats | null>(null)
  const pendingCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdated = ref<Date | null>(null)

  // Cache duration in milliseconds (5 minutes)
  const CACHE_DURATION = 5 * 60 * 1000

  // Computed - derived statistics
  const isStatsAvailable = computed(() => stats.value !== null)

  const acceptanceRate = computed(() => {
    if (!stats.value) return 0
    return Math.round(stats.value.acceptance_rate)
  })

  const totalInvitations = computed(() => stats.value?.total || 0)

  const pendingInvitations = computed(() => stats.value?.pending || 0)

  const acceptedInvitations = computed(() => stats.value?.accepted || 0)

  const expiredInvitations = computed(() => stats.value?.expired || 0)

  const cancelledInvitations = computed(() => stats.value?.cancelled || 0)

  const averageAcceptanceHours = computed(() => {
    if (!stats.value) return 0
    return Math.round(stats.value.average_acceptance_time)
  })

  // Computed - permission to view stats
  const canViewStats = computed(() => {
    const user = authStore.user
    const userRoles = user?.roles || []
    return userRoles.includes('admin') || userRoles.includes('manager')
  })

  // Computed - cache validity
  const isCacheValid = computed(() => {
    if (!lastUpdated.value) return false
    const now = new Date()
    const cacheAge = now.getTime() - lastUpdated.value.getTime()
    return cacheAge < CACHE_DURATION
  })

  // Actions - Statistics fetching
  async function fetchStats(forceRefresh = false) {
    // Check cache first unless force refresh
    if (!forceRefresh && isCacheValid.value && stats.value) {
      return stats.value
    }

    if (!canViewStats.value) {
      console.warn('User does not have permission to view invitation stats')
      return null
    }

    loading.value = true
    error.value = null

    try {
      const response = await invitationService.getStats()
      stats.value = response
      lastUpdated.value = new Date()
      console.log('Invitation stats fetched:', response)
      return response
    } catch (err: any) {
      console.error('Failed to fetch invitation stats:', err)
      error.value = err.message || 'Failed to fetch invitation statistics'
      stats.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchPendingCount(forceRefresh = false) {
    // Simple cache check for pending count (shorter cache duration - 1 minute)
    const PENDING_CACHE_DURATION = 60 * 1000
    if (!forceRefresh && lastUpdated.value) {
      const now = new Date()
      const cacheAge = now.getTime() - lastUpdated.value.getTime()
      if (cacheAge < PENDING_CACHE_DURATION) {
        return pendingCount.value
      }
    }

    try {
      const count = await invitationService.getPendingCount()
      pendingCount.value = count
      return count
    } catch (err: any) {
      console.error('Failed to fetch pending count:', err)
      pendingCount.value = 0
      return 0
    }
  }

  // Actions - Statistics refresh
  async function refreshStats() {
    return await fetchStats(true)
  }

  async function refreshPendingCount() {
    return await fetchPendingCount(true)
  }

  async function refreshAll() {
    if (!canViewStats.value) return

    loading.value = true
    try {
      await Promise.all([refreshStats(), refreshPendingCount()])
    } finally {
      loading.value = false
    }
  }

  // Utility functions for dashboard metrics
  function getStatsByStatus() {
    if (!stats.value) return null

    return [
      {
        label: 'Total',
        value: stats.value.total,
        color: 'gray',
        icon: 'envelope',
      },
      {
        label: 'Pending',
        value: stats.value.pending,
        color: 'yellow',
        icon: 'clock',
        percentage: stats.value.total > 0 ? (stats.value.pending / stats.value.total) * 100 : 0,
      },
      {
        label: 'Accepted',
        value: stats.value.accepted,
        color: 'green',
        icon: 'check-circle',
        percentage: stats.value.total > 0 ? (stats.value.accepted / stats.value.total) * 100 : 0,
      },
      {
        label: 'Expired',
        value: stats.value.expired,
        color: 'red',
        icon: 'x-circle',
        percentage: stats.value.total > 0 ? (stats.value.expired / stats.value.total) * 100 : 0,
      },
      {
        label: 'Cancelled',
        value: stats.value.cancelled,
        color: 'gray',
        icon: 'ban',
        percentage: stats.value.total > 0 ? (stats.value.cancelled / stats.value.total) * 100 : 0,
      },
    ]
  }

  function getPerformanceMetrics() {
    if (!stats.value) return null

    return {
      acceptanceRate: {
        value: acceptanceRate.value,
        label: 'Acceptance Rate',
        unit: '%',
        trend: acceptanceRate.value >= 70 ? 'good' : acceptanceRate.value >= 50 ? 'okay' : 'poor',
      },
      averageAcceptanceTime: {
        value: averageAcceptanceHours.value,
        label: 'Avg. Acceptance Time',
        unit: 'hours',
        formatted:
          averageAcceptanceHours.value < 24
            ? `${averageAcceptanceHours.value}h`
            : `${Math.round(averageAcceptanceHours.value / 24)}d`,
      },
      pendingCount: {
        value: pendingCount.value,
        label: 'Pending Invitations',
        unit: 'invitations',
      },
    }
  }

  // Actions - Background refresh (for real-time updates)
  let refreshInterval: ReturnType<typeof setInterval> | null = null

  function startAutoRefresh(intervalMs = 60000) {
    // Default 1 minute
    if (refreshInterval) {
      clearInterval(refreshInterval)
    }

    refreshInterval = setInterval(() => {
      if (canViewStats.value) {
        fetchPendingCount() // Only refresh the lightweight pending count automatically
      }
    }, intervalMs)
  }

  function stopAutoRefresh() {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  // Reset store
  function resetStore() {
    stats.value = null
    pendingCount.value = 0
    loading.value = false
    error.value = null
    lastUpdated.value = null
    stopAutoRefresh()
  }

  return {
    // State
    stats,
    pendingCount,
    loading,
    error,
    lastUpdated,

    // Computed - Statistics
    isStatsAvailable,
    acceptanceRate,
    totalInvitations,
    pendingInvitations,
    acceptedInvitations,
    expiredInvitations,
    cancelledInvitations,
    averageAcceptanceHours,
    canViewStats,
    isCacheValid,

    // Actions - Fetching
    fetchStats,
    fetchPendingCount,
    refreshStats,
    refreshPendingCount,
    refreshAll,

    // Utilities - Dashboard
    getStatsByStatus,
    getPerformanceMetrics,

    // Auto-refresh
    startAutoRefresh,
    stopAutoRefresh,

    // Reset
    resetStore,
  }
})

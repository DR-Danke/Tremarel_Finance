import { useState, useEffect, useCallback } from 'react'
import { dashboardService } from '@/services/dashboardService'
import type { DashboardStats } from '@/types'

interface UseDashboardResult {
  stats: DashboardStats | null
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export const useDashboard = (entityId: string | undefined): UseDashboardResult => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useDashboard]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [useDashboard]: Fetching dashboard stats for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await dashboardService.getStats(entityId)
      setStats(data)
      console.log('INFO [useDashboard]: Stats loaded for entity:', entityId)
    } catch (err) {
      console.error('ERROR [useDashboard]: Failed to fetch dashboard stats:', err)
      setError('Failed to load dashboard statistics. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId])

  // Fetch stats when entityId changes
  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  return {
    stats,
    isLoading,
    error,
    refresh: fetchStats,
  }
}

export default useDashboard

import { useState, useEffect, useCallback } from 'react'
import { legaldeskService } from '@/services/legaldeskService'
import type { LdDashboardStats } from '@/types/legaldesk'

interface UseLegaldeskDashboardResult {
  stats: LdDashboardStats | null
  loading: boolean
  error: string | null
  refreshStats: () => Promise<void>
}

export const useLegaldeskDashboard = (): UseLegaldeskDashboardResult => {
  const [stats, setStats] = useState<LdDashboardStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshStats = useCallback(async () => {
    console.log('INFO [useLegaldeskDashboard]: Fetching dashboard stats')
    setLoading(true)
    setError(null)

    try {
      const data = await legaldeskService.getDashboardStats()
      setStats(data)
      console.log('INFO [useLegaldeskDashboard]: Dashboard stats fetched')
    } catch (err) {
      console.error('ERROR [useLegaldeskDashboard]: Failed to fetch stats:', err)
      setError('Failed to load dashboard stats. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshStats()
  }, [refreshStats])

  return {
    stats,
    loading,
    error,
    refreshStats,
  }
}

export default useLegaldeskDashboard

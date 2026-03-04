import { useState, useEffect, useCallback } from 'react'
import { restaurantDashboardService } from '@/services/restaurantDashboardService'
import type { DashboardOverview } from '@/types/dashboard'

interface UseDashboardOverviewResult {
  overview: DashboardOverview | null
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export const useDashboardOverview = (restaurantId: string | null | undefined): UseDashboardOverviewResult => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchOverview = useCallback(async () => {
    if (!restaurantId) {
      console.log('INFO [useDashboardOverview]: No restaurantId provided, skipping fetch')
      return
    }

    console.log('INFO [useDashboardOverview]: Fetching overview for restaurant:', restaurantId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await restaurantDashboardService.getOverview(restaurantId)
      setOverview(data)
      console.log('INFO [useDashboardOverview]: Overview fetched successfully')
    } catch (err) {
      console.error('ERROR [useDashboardOverview]: Failed to fetch overview:', err)
      setError('Error al cargar el dashboard. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [restaurantId])

  useEffect(() => {
    fetchOverview()
  }, [fetchOverview])

  return {
    overview,
    isLoading,
    error,
    refresh: fetchOverview,
  }
}

export default useDashboardOverview

import { apiClient } from '@/api/clients'
import type { DashboardStats } from '@/types'

/**
 * Dashboard service for fetching dashboard statistics.
 */
export const dashboardService = {
  /**
   * Get dashboard statistics for an entity.
   * @param entityId - Entity ID to get stats for
   * @returns Dashboard statistics including summary, trends, and expense breakdown
   */
  async getStats(entityId: string): Promise<DashboardStats> {
    console.log('INFO [DashboardService]: Fetching dashboard stats for entity:', entityId)
    try {
      const response = await apiClient.get<DashboardStats>(
        `/dashboard/stats?entity_id=${entityId}`
      )
      console.log('INFO [DashboardService]: Dashboard stats fetched successfully')
      return response.data
    } catch (error) {
      console.error('ERROR [DashboardService]: Failed to fetch dashboard stats:', error)
      throw error
    }
  },
}

export default dashboardService

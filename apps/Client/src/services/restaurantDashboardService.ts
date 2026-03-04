import { apiClient } from '@/api/clients'
import type { DashboardOverview } from '@/types/dashboard'

/**
 * Restaurant dashboard service for fetching aggregated operational overview.
 */
export const restaurantDashboardService = {
  /**
   * Get the operational dashboard overview for a restaurant.
   * @param restaurantId - Restaurant UUID
   * @returns Dashboard overview with stats, tasks, alerts, and movements
   */
  async getOverview(restaurantId: string): Promise<DashboardOverview> {
    console.log('INFO [RestaurantDashboardService]: Fetching overview for restaurant:', restaurantId)
    try {
      const response = await apiClient.get<DashboardOverview>(
        `/restaurant-dashboard/${restaurantId}/overview`
      )
      console.log('INFO [RestaurantDashboardService]: Overview fetched successfully')
      return response.data
    } catch (error) {
      console.error('ERROR [RestaurantDashboardService]: Failed to fetch overview:', error)
      throw error
    }
  },
}

export default restaurantDashboardService

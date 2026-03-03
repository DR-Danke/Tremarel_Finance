import { apiClient } from '@/api/clients'
import type { InventoryMovement, InventoryMovementCreate, MovementFilters } from '@/types/resource'

/**
 * Inventory movement service for recording and querying stock movements.
 */
export const inventoryMovementService = {
  /**
   * Create a new inventory movement (entry or exit).
   * @param data - Movement creation data
   * @returns Created movement
   */
  async create(data: InventoryMovementCreate): Promise<InventoryMovement> {
    console.log('INFO [InventoryMovementService]: Creating movement for resource:', data.resource_id)
    try {
      const response = await apiClient.post<InventoryMovement>('/inventory-movements', data)
      console.log('INFO [InventoryMovementService]: Movement created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [InventoryMovementService]: Failed to create movement:', error)
      throw error
    }
  },

  /**
   * Get movements for a specific resource, with optional date range.
   * @param resourceId - Resource UUID
   * @param dateFrom - Optional start date filter
   * @param dateTo - Optional end date filter
   * @returns List of movements
   */
  async getByResource(resourceId: string, dateFrom?: string, dateTo?: string): Promise<InventoryMovement[]> {
    console.log('INFO [InventoryMovementService]: Fetching movements for resource:', resourceId)
    try {
      const params: Record<string, string> = { resource_id: resourceId }
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      const response = await apiClient.get<InventoryMovement[]>('/inventory-movements', { params })
      console.log('INFO [InventoryMovementService]: Movements fetched:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [InventoryMovementService]: Failed to fetch movements:', error)
      throw error
    }
  },

  /**
   * Get all movements for a restaurant, with optional filters.
   * @param restaurantId - Restaurant UUID
   * @param filters - Optional date/reason filters
   * @returns List of movements
   */
  async getAll(restaurantId: string, filters?: MovementFilters): Promise<InventoryMovement[]> {
    console.log('INFO [InventoryMovementService]: Fetching movements for restaurant:', restaurantId)
    try {
      const params: Record<string, string> = { restaurant_id: restaurantId }
      if (filters?.date_from) params.date_from = filters.date_from
      if (filters?.date_to) params.date_to = filters.date_to
      if (filters?.reason) params.reason = filters.reason
      const response = await apiClient.get<InventoryMovement[]>('/inventory-movements', { params })
      console.log('INFO [InventoryMovementService]: Movements fetched:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [InventoryMovementService]: Failed to fetch movements:', error)
      throw error
    }
  },
}

export default inventoryMovementService

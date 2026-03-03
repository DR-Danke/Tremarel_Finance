import { apiClient } from '@/api/clients'
import type { Resource, ResourceType, ResourceCreate, ResourceUpdate } from '@/types/resource'

/**
 * Resource service for CRUD operations on restaurant resources.
 */
export const resourceService = {
  /**
   * Get all resources for a restaurant, with optional type filter.
   * @param restaurantId - Restaurant UUID
   * @param type - Optional resource type filter
   * @returns List of resources
   */
  async getAll(restaurantId: string, type?: ResourceType): Promise<Resource[]> {
    console.log('INFO [ResourceService]: Fetching resources for restaurant:', restaurantId)
    try {
      const params: Record<string, string> = { restaurant_id: restaurantId }
      if (type) {
        params.type = type
      }
      const response = await apiClient.get<Resource[]>('/resources', { params })
      console.log('INFO [ResourceService]: Resources fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [ResourceService]: Failed to fetch resources:', error)
      throw error
    }
  },

  /**
   * Get a specific resource by ID.
   * @param resourceId - Resource UUID
   * @returns Resource
   */
  async getById(resourceId: string): Promise<Resource> {
    console.log('INFO [ResourceService]: Fetching resource:', resourceId)
    try {
      const response = await apiClient.get<Resource>(`/resources/${resourceId}`)
      console.log('INFO [ResourceService]: Resource fetched:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [ResourceService]: Failed to fetch resource:', error)
      throw error
    }
  },

  /**
   * Get low-stock resources for a restaurant.
   * @param restaurantId - Restaurant UUID
   * @returns List of low-stock resources
   */
  async getLowStock(restaurantId: string): Promise<Resource[]> {
    console.log('INFO [ResourceService]: Fetching low-stock resources for restaurant:', restaurantId)
    try {
      const response = await apiClient.get<Resource[]>('/resources/low-stock', {
        params: { restaurant_id: restaurantId },
      })
      console.log('INFO [ResourceService]: Low-stock resources fetched:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [ResourceService]: Failed to fetch low-stock resources:', error)
      throw error
    }
  },

  /**
   * Create a new resource.
   * @param data - Resource creation data
   * @returns Created resource
   */
  async create(data: ResourceCreate): Promise<Resource> {
    console.log('INFO [ResourceService]: Creating resource:', data.name)
    try {
      const response = await apiClient.post<Resource>('/resources', data)
      console.log('INFO [ResourceService]: Resource created:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [ResourceService]: Failed to create resource:', error)
      throw error
    }
  },

  /**
   * Update an existing resource.
   * @param id - Resource UUID
   * @param data - Resource update data
   * @returns Updated resource
   */
  async update(id: string, data: ResourceUpdate): Promise<Resource> {
    console.log('INFO [ResourceService]: Updating resource:', id)
    try {
      const response = await apiClient.put<Resource>(`/resources/${id}`, data)
      console.log('INFO [ResourceService]: Resource updated:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [ResourceService]: Failed to update resource:', error)
      throw error
    }
  },

  /**
   * Delete a resource.
   * @param id - Resource UUID
   */
  async delete(id: string): Promise<void> {
    console.log('INFO [ResourceService]: Deleting resource:', id)
    try {
      await apiClient.delete(`/resources/${id}`)
      console.log('INFO [ResourceService]: Resource deleted:', id)
    } catch (error) {
      console.error('ERROR [ResourceService]: Failed to delete resource:', error)
      throw error
    }
  },
}

export default resourceService

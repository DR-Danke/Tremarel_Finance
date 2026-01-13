import { apiClient } from '@/api/clients'
import type { Entity, CreateEntityData, UpdateEntityData } from '@/types'

/**
 * Entity service for CRUD operations on entities.
 */
export const entityService = {
  /**
   * Get all entities the current user belongs to.
   * @returns List of entities
   */
  async getEntities(): Promise<Entity[]> {
    console.log('INFO [EntityService]: Fetching entities')
    try {
      const response = await apiClient.get<Entity[]>('/entities')
      console.log('INFO [EntityService]: Entities fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [EntityService]: Failed to fetch entities:', error)
      throw error
    }
  },

  /**
   * Get a specific entity by ID.
   * @param id - Entity ID
   * @returns Entity data
   */
  async getEntity(id: string): Promise<Entity> {
    console.log('INFO [EntityService]: Fetching entity:', id)
    try {
      const response = await apiClient.get<Entity>(`/entities/${id}`)
      console.log('INFO [EntityService]: Entity fetched:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [EntityService]: Failed to fetch entity:', error)
      throw error
    }
  },

  /**
   * Create a new entity.
   * @param data - Entity creation data
   * @returns Created entity
   */
  async createEntity(data: CreateEntityData): Promise<Entity> {
    console.log('INFO [EntityService]: Creating entity:', data.name)
    try {
      const response = await apiClient.post<Entity>('/entities', data)
      console.log('INFO [EntityService]: Entity created:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [EntityService]: Failed to create entity:', error)
      throw error
    }
  },

  /**
   * Update an existing entity.
   * @param id - Entity ID
   * @param data - Entity update data
   * @returns Updated entity
   */
  async updateEntity(id: string, data: UpdateEntityData): Promise<Entity> {
    console.log('INFO [EntityService]: Updating entity:', id)
    try {
      const response = await apiClient.put<Entity>(`/entities/${id}`, data)
      console.log('INFO [EntityService]: Entity updated:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [EntityService]: Failed to update entity:', error)
      throw error
    }
  },

  /**
   * Delete an entity.
   * @param id - Entity ID
   */
  async deleteEntity(id: string): Promise<void> {
    console.log('INFO [EntityService]: Deleting entity:', id)
    try {
      await apiClient.delete(`/entities/${id}`)
      console.log('INFO [EntityService]: Entity deleted:', id)
    } catch (error) {
      console.error('ERROR [EntityService]: Failed to delete entity:', error)
      throw error
    }
  },
}

export default entityService

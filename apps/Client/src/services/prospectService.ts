import { apiClient } from '@/api/clients'
import type {
  Prospect,
  ProspectCreate,
  ProspectUpdate,
  ProspectStageUpdate,
  ProspectFilters,
  ProspectListResponse,
} from '@/types'

/**
 * Prospect service for CRUD operations on CRM prospects.
 */
export const prospectService = {
  /**
   * Create a new prospect.
   * @param data - Prospect creation data
   * @returns Created prospect
   */
  async create(data: ProspectCreate): Promise<Prospect> {
    console.log('INFO [ProspectService]: Creating prospect for entity:', data.entity_id)
    try {
      const response = await apiClient.post<Prospect>('/prospects/', data)
      console.log('INFO [ProspectService]: Prospect created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [ProspectService]: Failed to create prospect:', error)
      throw error
    }
  },

  /**
   * List prospects for an entity with optional filters.
   * @param entityId - Entity ID to filter by
   * @param filters - Optional filter criteria
   * @param skip - Number of records to skip
   * @param limit - Maximum records to return
   * @returns List of prospects with total count
   */
  async list(
    entityId: string,
    filters?: ProspectFilters,
    skip = 0,
    limit = 100
  ): Promise<ProspectListResponse> {
    console.log('INFO [ProspectService]: Listing prospects for entity:', entityId)
    try {
      const params = new URLSearchParams()
      params.append('entity_id', entityId)
      params.append('skip', skip.toString())
      params.append('limit', limit.toString())

      if (filters?.stage) {
        params.append('stage', filters.stage)
      }
      if (filters?.is_active !== undefined) {
        params.append('is_active', filters.is_active.toString())
      }
      if (filters?.source) {
        params.append('source', filters.source)
      }

      const response = await apiClient.get<ProspectListResponse>(
        `/prospects/?${params.toString()}`
      )
      console.log(
        'INFO [ProspectService]: Fetched',
        response.data.prospects.length,
        'prospects (total:',
        response.data.total,
        ')'
      )
      return response.data
    } catch (error) {
      console.error('ERROR [ProspectService]: Failed to list prospects:', error)
      throw error
    }
  },

  /**
   * Get a single prospect by ID.
   * @param prospectId - Prospect ID
   * @param entityId - Entity ID for validation
   * @returns Prospect data
   */
  async get(prospectId: string, entityId: string): Promise<Prospect> {
    console.log('INFO [ProspectService]: Getting prospect:', prospectId)
    try {
      const response = await apiClient.get<Prospect>(
        `/prospects/${prospectId}?entity_id=${entityId}`
      )
      console.log('INFO [ProspectService]: Prospect fetched:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [ProspectService]: Failed to get prospect:', error)
      throw error
    }
  },

  /**
   * Update an existing prospect.
   * @param prospectId - Prospect ID to update
   * @param entityId - Entity ID for validation
   * @param data - Update data
   * @returns Updated prospect
   */
  async update(
    prospectId: string,
    entityId: string,
    data: ProspectUpdate
  ): Promise<Prospect> {
    console.log('INFO [ProspectService]: Updating prospect:', prospectId)
    try {
      const response = await apiClient.put<Prospect>(
        `/prospects/${prospectId}?entity_id=${entityId}`,
        data
      )
      console.log('INFO [ProspectService]: Prospect updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [ProspectService]: Failed to update prospect:', error)
      throw error
    }
  },

  /**
   * Update a prospect's pipeline stage.
   * @param prospectId - Prospect ID
   * @param entityId - Entity ID for validation
   * @param data - Stage update data
   * @returns Updated prospect
   */
  async updateStage(
    prospectId: string,
    entityId: string,
    data: ProspectStageUpdate
  ): Promise<Prospect> {
    console.log('INFO [ProspectService]: Updating stage for prospect:', prospectId, 'to', data.new_stage)
    try {
      const response = await apiClient.patch<Prospect>(
        `/prospects/${prospectId}/stage?entity_id=${entityId}`,
        data
      )
      console.log('INFO [ProspectService]: Prospect stage updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [ProspectService]: Failed to update prospect stage:', error)
      throw error
    }
  },

  /**
   * Delete a prospect.
   * @param prospectId - Prospect ID to delete
   * @param entityId - Entity ID for validation
   */
  async delete(prospectId: string, entityId: string): Promise<void> {
    console.log('INFO [ProspectService]: Deleting prospect:', prospectId)
    try {
      await apiClient.delete(`/prospects/${prospectId}?entity_id=${entityId}`)
      console.log('INFO [ProspectService]: Prospect deleted:', prospectId)
    } catch (error) {
      console.error('ERROR [ProspectService]: Failed to delete prospect:', error)
      throw error
    }
  },
}

export default prospectService

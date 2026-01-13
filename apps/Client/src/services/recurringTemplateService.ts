import { apiClient } from '@/api/clients'
import type {
  RecurringTemplate,
  RecurringTemplateCreate,
  RecurringTemplateUpdate,
  RecurringTemplateListResponse,
} from '@/types'

/**
 * Recurring template service for CRUD operations on recurring templates.
 */
export const recurringTemplateService = {
  /**
   * Create a new recurring template.
   * @param data - Template creation data
   * @returns Created template
   */
  async create(data: RecurringTemplateCreate): Promise<RecurringTemplate> {
    console.log('INFO [RecurringTemplateService]: Creating template for entity:', data.entity_id)
    try {
      const response = await apiClient.post<RecurringTemplate>('/recurring-templates/', data)
      console.log('INFO [RecurringTemplateService]: Template created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [RecurringTemplateService]: Failed to create template:', error)
      throw error
    }
  },

  /**
   * List recurring templates for an entity.
   * @param entityId - Entity ID to filter by
   * @param includeInactive - Whether to include inactive templates
   * @param skip - Number of records to skip
   * @param limit - Maximum records to return
   * @returns List of templates with total count
   */
  async list(
    entityId: string,
    includeInactive = false,
    skip = 0,
    limit = 100
  ): Promise<RecurringTemplateListResponse> {
    console.log('INFO [RecurringTemplateService]: Listing templates for entity:', entityId)
    try {
      const params = new URLSearchParams()
      params.append('entity_id', entityId)
      params.append('include_inactive', String(includeInactive))
      params.append('skip', skip.toString())
      params.append('limit', limit.toString())

      const response = await apiClient.get<RecurringTemplateListResponse>(
        `/recurring-templates/?${params.toString()}`
      )
      console.log(
        'INFO [RecurringTemplateService]: Fetched',
        response.data.templates.length,
        'templates (total:',
        response.data.total,
        ')'
      )
      return response.data
    } catch (error) {
      console.error('ERROR [RecurringTemplateService]: Failed to list templates:', error)
      throw error
    }
  },

  /**
   * Get a single recurring template by ID.
   * @param templateId - Template ID
   * @param entityId - Entity ID for validation
   * @returns Template data
   */
  async get(templateId: string, entityId: string): Promise<RecurringTemplate> {
    console.log('INFO [RecurringTemplateService]: Getting template:', templateId)
    try {
      const response = await apiClient.get<RecurringTemplate>(
        `/recurring-templates/${templateId}?entity_id=${entityId}`
      )
      console.log('INFO [RecurringTemplateService]: Template fetched:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [RecurringTemplateService]: Failed to get template:', error)
      throw error
    }
  },

  /**
   * Update an existing recurring template.
   * @param templateId - Template ID to update
   * @param entityId - Entity ID for validation
   * @param data - Update data
   * @returns Updated template
   */
  async update(
    templateId: string,
    entityId: string,
    data: RecurringTemplateUpdate
  ): Promise<RecurringTemplate> {
    console.log('INFO [RecurringTemplateService]: Updating template:', templateId)
    try {
      const response = await apiClient.put<RecurringTemplate>(
        `/recurring-templates/${templateId}?entity_id=${entityId}`,
        data
      )
      console.log('INFO [RecurringTemplateService]: Template updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [RecurringTemplateService]: Failed to update template:', error)
      throw error
    }
  },

  /**
   * Deactivate a recurring template (soft delete).
   * @param templateId - Template ID to deactivate
   * @param entityId - Entity ID for validation
   * @returns Deactivated template
   */
  async deactivate(templateId: string, entityId: string): Promise<RecurringTemplate> {
    console.log('INFO [RecurringTemplateService]: Deactivating template:', templateId)
    try {
      const response = await apiClient.post<RecurringTemplate>(
        `/recurring-templates/${templateId}/deactivate?entity_id=${entityId}`
      )
      console.log('INFO [RecurringTemplateService]: Template deactivated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [RecurringTemplateService]: Failed to deactivate template:', error)
      throw error
    }
  },

  /**
   * Delete a recurring template (hard delete).
   * @param templateId - Template ID to delete
   * @param entityId - Entity ID for validation
   */
  async delete(templateId: string, entityId: string): Promise<void> {
    console.log('INFO [RecurringTemplateService]: Deleting template:', templateId)
    try {
      await apiClient.delete(`/recurring-templates/${templateId}?entity_id=${entityId}`)
      console.log('INFO [RecurringTemplateService]: Template deleted:', templateId)
    } catch (error) {
      console.error('ERROR [RecurringTemplateService]: Failed to delete template:', error)
      throw error
    }
  },
}

export default recurringTemplateService

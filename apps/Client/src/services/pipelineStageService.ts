import { apiClient } from '@/api/clients'
import type { PipelineStage, PipelineStageListResponse } from '@/types'

export const pipelineStageService = {
  async list(
    entityId: string,
    activeOnly = true
  ): Promise<PipelineStageListResponse> {
    console.log('INFO [PipelineStageService]: Listing stages for entity:', entityId)
    try {
      const params = new URLSearchParams()
      params.append('entity_id', entityId)
      params.append('active_only', activeOnly.toString())

      const response = await apiClient.get<PipelineStageListResponse>(
        `/pipeline-stages/?${params.toString()}`
      )
      console.log(
        'INFO [PipelineStageService]: Fetched',
        response.data.stages.length,
        'stages (total:',
        response.data.total,
        ')'
      )
      return response.data
    } catch (error) {
      console.error('ERROR [PipelineStageService]: Failed to list stages:', error)
      throw error
    }
  },

  async seedDefaults(entityId: string): Promise<PipelineStage[]> {
    console.log('INFO [PipelineStageService]: Seeding default stages for entity:', entityId)
    try {
      const response = await apiClient.post<PipelineStage[]>(
        '/pipeline-stages/seed',
        { entity_id: entityId }
      )
      console.log('INFO [PipelineStageService]: Seeded', response.data.length, 'default stages')
      return response.data
    } catch (error) {
      console.error('ERROR [PipelineStageService]: Failed to seed default stages:', error)
      throw error
    }
  },
}

export default pipelineStageService

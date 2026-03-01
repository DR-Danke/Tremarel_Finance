import { useState, useEffect, useCallback } from 'react'
import { pipelineStageService } from '@/services/pipelineStageService'
import type { PipelineStage } from '@/types'

interface UsePipelineStagesResult {
  stages: PipelineStage[]
  isLoading: boolean
  error: string | null
  refetchStages: () => Promise<void>
}

export const usePipelineStages = (entityId: string | null): UsePipelineStagesResult => {
  const [stages, setStages] = useState<PipelineStage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStages = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [usePipelineStages]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [usePipelineStages]: Fetching stages for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const response = await pipelineStageService.list(entityId)
      let fetchedStages = response.stages

      if (fetchedStages.length === 0) {
        console.log('INFO [usePipelineStages]: No stages found, auto-seeding defaults')
        try {
          await pipelineStageService.seedDefaults(entityId)
          const seededResponse = await pipelineStageService.list(entityId)
          fetchedStages = seededResponse.stages
        } catch (seedError) {
          console.error('ERROR [usePipelineStages]: Failed to seed default stages:', seedError)
        }
      }

      const sorted = [...fetchedStages].sort((a, b) => a.order_index - b.order_index)
      setStages(sorted)
      console.log('INFO [usePipelineStages]: Loaded', sorted.length, 'stages')
    } catch (err) {
      console.error('ERROR [usePipelineStages]: Failed to fetch stages:', err)
      setError('Failed to load pipeline stages. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId])

  useEffect(() => {
    fetchStages()
  }, [fetchStages])

  return {
    stages,
    isLoading,
    error,
    refetchStages: fetchStages,
  }
}

export default usePipelineStages

import { useState, useEffect, useCallback } from 'react'
import { prospectService } from '@/services/prospectService'
import type {
  Prospect,
  ProspectCreate,
  ProspectUpdate,
  ProspectStageUpdate,
  ProspectFilters,
} from '@/types'

interface UseProspectsResult {
  prospects: Prospect[]
  total: number
  isLoading: boolean
  error: string | null
  filters: ProspectFilters
  fetchProspects: () => Promise<void>
  createProspect: (data: ProspectCreate) => Promise<void>
  updateProspect: (id: string, data: ProspectUpdate) => Promise<void>
  updateProspectStage: (id: string, data: ProspectStageUpdate) => Promise<void>
  deleteProspect: (id: string) => Promise<void>
  setFilters: (filters: ProspectFilters) => void
}

export const useProspects = (entityId: string | null): UseProspectsResult => {
  const [prospects, setProspects] = useState<Prospect[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<ProspectFilters>({})

  const fetchProspects = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useProspects]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [useProspects]: Fetching prospects for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const response = await prospectService.list(entityId, filters)
      setProspects(response.prospects)
      setTotal(response.total)
      console.log('INFO [useProspects]: Fetched', response.prospects.length, 'prospects')
    } catch (err) {
      console.error('ERROR [useProspects]: Failed to fetch prospects:', err)
      setError('Failed to load prospects. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId, filters])

  const createProspect = useCallback(
    async (data: ProspectCreate) => {
      console.log('INFO [useProspects]: Creating prospect')
      setError(null)

      try {
        await prospectService.create(data)
        console.log('INFO [useProspects]: Prospect created, refreshing list')
        await fetchProspects()
      } catch (err) {
        console.error('ERROR [useProspects]: Failed to create prospect:', err)
        setError('Failed to create prospect. Please try again.')
        throw err
      }
    },
    [fetchProspects]
  )

  const updateProspect = useCallback(
    async (id: string, data: ProspectUpdate) => {
      if (!entityId) return
      console.log('INFO [useProspects]: Updating prospect:', id)
      setError(null)

      try {
        await prospectService.update(id, entityId, data)
        console.log('INFO [useProspects]: Prospect updated, refreshing list')
        await fetchProspects()
      } catch (err) {
        console.error('ERROR [useProspects]: Failed to update prospect:', err)
        setError('Failed to update prospect. Please try again.')
        throw err
      }
    },
    [entityId, fetchProspects]
  )

  const updateProspectStage = useCallback(
    async (id: string, data: ProspectStageUpdate) => {
      if (!entityId) return
      console.log('INFO [useProspects]: Updating prospect stage:', id, 'to', data.new_stage)
      setError(null)

      try {
        await prospectService.updateStage(id, entityId, data)
        console.log('INFO [useProspects]: Prospect stage updated, refreshing list')
        await fetchProspects()
      } catch (err) {
        console.error('ERROR [useProspects]: Failed to update prospect stage:', err)
        setError('Failed to update prospect stage. Please try again.')
        throw err
      }
    },
    [entityId, fetchProspects]
  )

  const deleteProspect = useCallback(
    async (id: string) => {
      if (!entityId) return
      console.log('INFO [useProspects]: Deleting prospect:', id)
      setError(null)

      try {
        await prospectService.delete(id, entityId)
        console.log('INFO [useProspects]: Prospect deleted, refreshing list')
        await fetchProspects()
      } catch (err) {
        console.error('ERROR [useProspects]: Failed to delete prospect:', err)
        setError('Failed to delete prospect. Please try again.')
        throw err
      }
    },
    [entityId, fetchProspects]
  )

  // Fetch prospects when entityId or filters change
  useEffect(() => {
    fetchProspects()
  }, [fetchProspects])

  return {
    prospects,
    total,
    isLoading,
    error,
    filters,
    fetchProspects,
    createProspect,
    updateProspect,
    updateProspectStage,
    deleteProspect,
    setFilters,
  }
}

export default useProspects

import { useState, useEffect, useCallback } from 'react'
import { resourceService } from '@/services/resourceService'
import type { Resource, ResourceCreate, ResourceUpdate, ResourceFilters } from '@/types/resource'

interface UseResourcesResult {
  resources: Resource[]
  isLoading: boolean
  error: string | null
  filters: ResourceFilters
  fetchResources: () => Promise<void>
  createResource: (data: ResourceCreate) => Promise<void>
  updateResource: (id: string, data: ResourceUpdate) => Promise<void>
  deleteResource: (id: string) => Promise<void>
  setFilters: (filters: ResourceFilters) => void
}

export const useResources = (restaurantId: string | null): UseResourcesResult => {
  const [resources, setResources] = useState<Resource[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<ResourceFilters>({})

  const fetchResources = useCallback(async () => {
    if (!restaurantId) {
      console.log('INFO [useResources]: No restaurantId provided, skipping fetch')
      return
    }

    console.log('INFO [useResources]: Fetching resources for restaurant:', restaurantId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await resourceService.getAll(restaurantId, filters.type)
      setResources(data)
      console.log('INFO [useResources]: Fetched', data.length, 'resources')
    } catch (err) {
      console.error('ERROR [useResources]: Failed to fetch resources:', err)
      setError('Error al cargar recursos. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [restaurantId, filters])

  const createResource = useCallback(
    async (data: ResourceCreate) => {
      console.log('INFO [useResources]: Creating resource')
      setError(null)

      try {
        await resourceService.create(data)
        console.log('INFO [useResources]: Resource created, refreshing list')
        await fetchResources()
      } catch (err) {
        console.error('ERROR [useResources]: Failed to create resource:', err)
        setError('Error al crear recurso. Intente de nuevo.')
        throw err
      }
    },
    [fetchResources]
  )

  const updateResource = useCallback(
    async (id: string, data: ResourceUpdate) => {
      if (!restaurantId) return
      console.log('INFO [useResources]: Updating resource:', id)
      setError(null)

      try {
        await resourceService.update(id, data)
        console.log('INFO [useResources]: Resource updated, refreshing list')
        await fetchResources()
      } catch (err) {
        console.error('ERROR [useResources]: Failed to update resource:', err)
        setError('Error al actualizar recurso. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchResources]
  )

  const deleteResource = useCallback(
    async (id: string) => {
      if (!restaurantId) return
      console.log('INFO [useResources]: Deleting resource:', id)
      setError(null)

      try {
        await resourceService.delete(id)
        console.log('INFO [useResources]: Resource deleted, refreshing list')
        await fetchResources()
      } catch (err) {
        console.error('ERROR [useResources]: Failed to delete resource:', err)
        setError('Error al eliminar recurso. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchResources]
  )

  useEffect(() => {
    fetchResources()
  }, [fetchResources])

  return {
    resources,
    isLoading,
    error,
    filters,
    fetchResources,
    createResource,
    updateResource,
    deleteResource,
    setFilters,
  }
}

export default useResources

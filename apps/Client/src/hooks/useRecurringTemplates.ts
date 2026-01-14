import { useState, useEffect, useCallback } from 'react'
import { recurringTemplateService } from '@/services/recurringTemplateService'
import type {
  RecurringTemplate,
  RecurringTemplateCreate,
  RecurringTemplateUpdate,
} from '@/types'

interface UseRecurringTemplatesResult {
  templates: RecurringTemplate[]
  total: number
  isLoading: boolean
  error: string | null
  includeInactive: boolean
  fetchTemplates: () => Promise<void>
  createTemplate: (data: RecurringTemplateCreate) => Promise<void>
  updateTemplate: (id: string, data: RecurringTemplateUpdate) => Promise<void>
  deactivateTemplate: (id: string) => Promise<void>
  deleteTemplate: (id: string) => Promise<void>
  setIncludeInactive: (include: boolean) => void
}

export const useRecurringTemplates = (entityId: string | null): UseRecurringTemplatesResult => {
  const [templates, setTemplates] = useState<RecurringTemplate[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [includeInactive, setIncludeInactive] = useState(false)

  const fetchTemplates = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useRecurringTemplates]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [useRecurringTemplates]: Fetching templates for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const response = await recurringTemplateService.list(entityId, includeInactive)
      setTemplates(response.templates)
      setTotal(response.total)
      console.log('INFO [useRecurringTemplates]: Fetched', response.templates.length, 'templates')
    } catch (err) {
      console.error('ERROR [useRecurringTemplates]: Failed to fetch templates:', err)
      setError('Failed to load recurring templates. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId, includeInactive])

  const createTemplate = useCallback(
    async (data: RecurringTemplateCreate) => {
      console.log('INFO [useRecurringTemplates]: Creating template')
      setError(null)

      try {
        await recurringTemplateService.create(data)
        console.log('INFO [useRecurringTemplates]: Template created, refreshing list')
        await fetchTemplates()
      } catch (err) {
        console.error('ERROR [useRecurringTemplates]: Failed to create template:', err)
        setError('Failed to create template. Please try again.')
        throw err
      }
    },
    [fetchTemplates]
  )

  const updateTemplate = useCallback(
    async (id: string, data: RecurringTemplateUpdate) => {
      if (!entityId) return
      console.log('INFO [useRecurringTemplates]: Updating template:', id)
      setError(null)

      try {
        await recurringTemplateService.update(id, entityId, data)
        console.log('INFO [useRecurringTemplates]: Template updated, refreshing list')
        await fetchTemplates()
      } catch (err) {
        console.error('ERROR [useRecurringTemplates]: Failed to update template:', err)
        setError('Failed to update template. Please try again.')
        throw err
      }
    },
    [entityId, fetchTemplates]
  )

  const deactivateTemplate = useCallback(
    async (id: string) => {
      if (!entityId) return
      console.log('INFO [useRecurringTemplates]: Deactivating template:', id)
      setError(null)

      try {
        await recurringTemplateService.deactivate(id, entityId)
        console.log('INFO [useRecurringTemplates]: Template deactivated, refreshing list')
        await fetchTemplates()
      } catch (err) {
        console.error('ERROR [useRecurringTemplates]: Failed to deactivate template:', err)
        setError('Failed to deactivate template. Please try again.')
        throw err
      }
    },
    [entityId, fetchTemplates]
  )

  const deleteTemplate = useCallback(
    async (id: string) => {
      if (!entityId) return
      console.log('INFO [useRecurringTemplates]: Deleting template:', id)
      setError(null)

      try {
        await recurringTemplateService.delete(id, entityId)
        console.log('INFO [useRecurringTemplates]: Template deleted, refreshing list')
        await fetchTemplates()
      } catch (err) {
        console.error('ERROR [useRecurringTemplates]: Failed to delete template:', err)
        setError('Failed to delete template. Please try again.')
        throw err
      }
    },
    [entityId, fetchTemplates]
  )

  // Fetch templates when entityId or includeInactive changes
  useEffect(() => {
    fetchTemplates()
  }, [fetchTemplates])

  return {
    templates,
    total,
    isLoading,
    error,
    includeInactive,
    fetchTemplates,
    createTemplate,
    updateTemplate,
    deactivateTemplate,
    deleteTemplate,
    setIncludeInactive,
  }
}

export default useRecurringTemplates

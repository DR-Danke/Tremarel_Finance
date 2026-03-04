import { useState, useEffect, useCallback } from 'react'
import { legaldeskService } from '@/services/legaldeskService'
import type { LdCase, LdCaseCreate, LdCaseFilters } from '@/types/legaldesk'

interface UseLegaldeskCasesResult {
  cases: LdCase[]
  loading: boolean
  error: string | null
  filters: LdCaseFilters
  setFilters: (filters: LdCaseFilters) => void
  createCase: (data: LdCaseCreate) => Promise<LdCase>
  refreshCases: () => Promise<void>
}

export const useLegaldeskCases = (): UseLegaldeskCasesResult => {
  const [cases, setCases] = useState<LdCase[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<LdCaseFilters>({})

  const refreshCases = useCallback(async () => {
    console.log('INFO [useLegaldeskCases]: Fetching cases with filters:', filters)
    setLoading(true)
    setError(null)

    try {
      const data = await legaldeskService.listCases(filters)
      setCases(data)
      console.log('INFO [useLegaldeskCases]: Fetched', data.length, 'cases')
    } catch (err) {
      console.error('ERROR [useLegaldeskCases]: Failed to fetch cases:', err)
      setError('Failed to load cases. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  const createCase = useCallback(
    async (data: LdCaseCreate): Promise<LdCase> => {
      console.log('INFO [useLegaldeskCases]: Creating case')
      setError(null)

      try {
        const created = await legaldeskService.createCase(data)
        console.log('INFO [useLegaldeskCases]: Case created, refreshing list')
        await refreshCases()
        return created
      } catch (err) {
        console.error('ERROR [useLegaldeskCases]: Failed to create case:', err)
        setError('Failed to create case. Please try again.')
        throw err
      }
    },
    [refreshCases]
  )

  useEffect(() => {
    refreshCases()
  }, [refreshCases])

  return {
    cases,
    loading,
    error,
    filters,
    setFilters,
    createCase,
    refreshCases,
  }
}

export default useLegaldeskCases

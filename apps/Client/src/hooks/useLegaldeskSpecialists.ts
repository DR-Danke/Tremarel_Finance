import { useState, useEffect, useCallback } from 'react'
import { legaldeskService } from '@/services/legaldeskService'
import type {
  LdSpecialist,
  LdSpecialistCreate,
  LdSpecialistUpdate,
  LdSpecialistExpertiseCreate,
  LdSpecialistJurisdictionCreate,
  LdSpecialistScoreCreate,
} from '@/types/legaldesk'

interface UseLegaldeskSpecialistsResult {
  specialists: LdSpecialist[]
  loading: boolean
  error: string | null
  createSpecialist: (data: LdSpecialistCreate) => Promise<LdSpecialist>
  updateSpecialist: (id: number, data: LdSpecialistUpdate) => Promise<void>
  addExpertise: (id: number, data: LdSpecialistExpertiseCreate) => Promise<void>
  addJurisdiction: (id: number, data: LdSpecialistJurisdictionCreate) => Promise<void>
  submitScore: (id: number, data: LdSpecialistScoreCreate) => Promise<void>
  refreshSpecialists: () => Promise<void>
}

export const useLegaldeskSpecialists = (): UseLegaldeskSpecialistsResult => {
  const [specialists, setSpecialists] = useState<LdSpecialist[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshSpecialists = useCallback(async () => {
    console.log('INFO [useLegaldeskSpecialists]: Fetching specialists')
    setLoading(true)
    setError(null)

    try {
      const data = await legaldeskService.listSpecialists()
      setSpecialists(data)
      console.log('INFO [useLegaldeskSpecialists]: Fetched', data.length, 'specialists')
    } catch (err) {
      console.error('ERROR [useLegaldeskSpecialists]: Failed to fetch specialists:', err)
      setError('Failed to load specialists. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  const createSpecialist = useCallback(
    async (data: LdSpecialistCreate): Promise<LdSpecialist> => {
      console.log('INFO [useLegaldeskSpecialists]: Creating specialist')
      setError(null)

      try {
        const created = await legaldeskService.createSpecialist(data)
        console.log('INFO [useLegaldeskSpecialists]: Specialist created, refreshing list')
        await refreshSpecialists()
        return created
      } catch (err) {
        console.error('ERROR [useLegaldeskSpecialists]: Failed to create specialist:', err)
        setError('Failed to create specialist. Please try again.')
        throw err
      }
    },
    [refreshSpecialists]
  )

  const updateSpecialist = useCallback(
    async (id: number, data: LdSpecialistUpdate) => {
      console.log('INFO [useLegaldeskSpecialists]: Updating specialist:', id)
      setError(null)

      try {
        await legaldeskService.updateSpecialist(id, data)
        console.log('INFO [useLegaldeskSpecialists]: Specialist updated, refreshing list')
        await refreshSpecialists()
      } catch (err) {
        console.error('ERROR [useLegaldeskSpecialists]: Failed to update specialist:', err)
        setError('Failed to update specialist. Please try again.')
        throw err
      }
    },
    [refreshSpecialists]
  )

  const addExpertise = useCallback(
    async (id: number, data: LdSpecialistExpertiseCreate) => {
      console.log('INFO [useLegaldeskSpecialists]: Adding expertise for specialist:', id)
      setError(null)

      try {
        await legaldeskService.addExpertise(id, data)
        console.log('INFO [useLegaldeskSpecialists]: Expertise added, refreshing list')
        await refreshSpecialists()
      } catch (err) {
        console.error('ERROR [useLegaldeskSpecialists]: Failed to add expertise:', err)
        setError('Failed to add expertise. Please try again.')
        throw err
      }
    },
    [refreshSpecialists]
  )

  const addJurisdiction = useCallback(
    async (id: number, data: LdSpecialistJurisdictionCreate) => {
      console.log('INFO [useLegaldeskSpecialists]: Adding jurisdiction for specialist:', id)
      setError(null)

      try {
        await legaldeskService.addJurisdiction(id, data)
        console.log('INFO [useLegaldeskSpecialists]: Jurisdiction added, refreshing list')
        await refreshSpecialists()
      } catch (err) {
        console.error('ERROR [useLegaldeskSpecialists]: Failed to add jurisdiction:', err)
        setError('Failed to add jurisdiction. Please try again.')
        throw err
      }
    },
    [refreshSpecialists]
  )

  const submitScore = useCallback(
    async (id: number, data: LdSpecialistScoreCreate) => {
      console.log('INFO [useLegaldeskSpecialists]: Submitting score for specialist:', id)
      setError(null)

      try {
        await legaldeskService.submitScore(id, data)
        console.log('INFO [useLegaldeskSpecialists]: Score submitted, refreshing list')
        await refreshSpecialists()
      } catch (err) {
        console.error('ERROR [useLegaldeskSpecialists]: Failed to submit score:', err)
        setError('Failed to submit score. Please try again.')
        throw err
      }
    },
    [refreshSpecialists]
  )

  useEffect(() => {
    refreshSpecialists()
  }, [refreshSpecialists])

  return {
    specialists,
    loading,
    error,
    createSpecialist,
    updateSpecialist,
    addExpertise,
    addJurisdiction,
    submitScore,
    refreshSpecialists,
  }
}

export default useLegaldeskSpecialists

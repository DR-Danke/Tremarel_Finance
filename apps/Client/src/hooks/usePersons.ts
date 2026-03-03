import { useState, useEffect, useCallback } from 'react'
import { personService } from '@/services/personService'
import type { Person, PersonCreate, PersonUpdate, PersonFilters } from '@/types/person'

interface UsePersonsResult {
  persons: Person[]
  isLoading: boolean
  error: string | null
  filters: PersonFilters
  fetchPersons: () => Promise<void>
  createPerson: (data: PersonCreate) => Promise<void>
  updatePerson: (id: string, data: PersonUpdate) => Promise<void>
  deletePerson: (id: string) => Promise<void>
  setFilters: (filters: PersonFilters) => void
}

export const usePersons = (restaurantId: string | null): UsePersonsResult => {
  const [persons, setPersons] = useState<Person[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<PersonFilters>({})

  const fetchPersons = useCallback(async () => {
    if (!restaurantId) {
      console.log('INFO [usePersons]: No restaurantId provided, skipping fetch')
      return
    }

    console.log('INFO [usePersons]: Fetching persons for restaurant:', restaurantId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await personService.getAll(restaurantId, filters.type)
      setPersons(data)
      console.log('INFO [usePersons]: Fetched', data.length, 'persons')
    } catch (err) {
      console.error('ERROR [usePersons]: Failed to fetch persons:', err)
      setError('Error al cargar personas. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [restaurantId, filters])

  const createPerson = useCallback(
    async (data: PersonCreate) => {
      console.log('INFO [usePersons]: Creating person')
      setError(null)

      try {
        await personService.create(data)
        console.log('INFO [usePersons]: Person created, refreshing list')
        await fetchPersons()
      } catch (err) {
        console.error('ERROR [usePersons]: Failed to create person:', err)
        setError('Error al crear persona. Intente de nuevo.')
        throw err
      }
    },
    [fetchPersons]
  )

  const updatePerson = useCallback(
    async (id: string, data: PersonUpdate) => {
      if (!restaurantId) return
      console.log('INFO [usePersons]: Updating person:', id)
      setError(null)

      try {
        await personService.update(id, data)
        console.log('INFO [usePersons]: Person updated, refreshing list')
        await fetchPersons()
      } catch (err) {
        console.error('ERROR [usePersons]: Failed to update person:', err)
        setError('Error al actualizar persona. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchPersons]
  )

  const deletePerson = useCallback(
    async (id: string) => {
      if (!restaurantId) return
      console.log('INFO [usePersons]: Deleting person:', id)
      setError(null)

      try {
        await personService.delete(id)
        console.log('INFO [usePersons]: Person deleted, refreshing list')
        await fetchPersons()
      } catch (err) {
        console.error('ERROR [usePersons]: Failed to delete person:', err)
        setError('Error al eliminar persona. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchPersons]
  )

  useEffect(() => {
    fetchPersons()
  }, [fetchPersons])

  return {
    persons,
    isLoading,
    error,
    filters,
    fetchPersons,
    createPerson,
    updatePerson,
    deletePerson,
    setFilters,
  }
}

export default usePersons

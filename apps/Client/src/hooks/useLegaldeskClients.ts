import { useState, useEffect, useCallback } from 'react'
import { legaldeskService } from '@/services/legaldeskService'
import type { LdClient, LdClientCreate, LdClientUpdate } from '@/types/legaldesk'

interface UseLegaldeskClientsResult {
  clients: LdClient[]
  loading: boolean
  error: string | null
  createClient: (data: LdClientCreate) => Promise<LdClient>
  updateClient: (id: number, data: LdClientUpdate) => Promise<void>
  refreshClients: () => Promise<void>
}

export const useLegaldeskClients = (): UseLegaldeskClientsResult => {
  const [clients, setClients] = useState<LdClient[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshClients = useCallback(async () => {
    console.log('INFO [useLegaldeskClients]: Fetching clients')
    setLoading(true)
    setError(null)

    try {
      const data = await legaldeskService.listClients()
      setClients(data)
      console.log('INFO [useLegaldeskClients]: Fetched', data.length, 'clients')
    } catch (err) {
      console.error('ERROR [useLegaldeskClients]: Failed to fetch clients:', err)
      setError('Failed to load clients. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  const createClient = useCallback(
    async (data: LdClientCreate): Promise<LdClient> => {
      console.log('INFO [useLegaldeskClients]: Creating client')
      setError(null)

      try {
        const created = await legaldeskService.createClient(data)
        console.log('INFO [useLegaldeskClients]: Client created, refreshing list')
        await refreshClients()
        return created
      } catch (err) {
        console.error('ERROR [useLegaldeskClients]: Failed to create client:', err)
        setError('Failed to create client. Please try again.')
        throw err
      }
    },
    [refreshClients]
  )

  const updateClient = useCallback(
    async (id: number, data: LdClientUpdate) => {
      console.log('INFO [useLegaldeskClients]: Updating client:', id)
      setError(null)

      try {
        await legaldeskService.updateClient(id, data)
        console.log('INFO [useLegaldeskClients]: Client updated, refreshing list')
        await refreshClients()
      } catch (err) {
        console.error('ERROR [useLegaldeskClients]: Failed to update client:', err)
        setError('Failed to update client. Please try again.')
        throw err
      }
    },
    [refreshClients]
  )

  useEffect(() => {
    refreshClients()
  }, [refreshClients])

  return {
    clients,
    loading,
    error,
    createClient,
    updateClient,
    refreshClients,
  }
}

export default useLegaldeskClients

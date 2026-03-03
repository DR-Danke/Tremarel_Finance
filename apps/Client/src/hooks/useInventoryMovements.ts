import { useState, useCallback } from 'react'
import { inventoryMovementService } from '@/services/inventoryMovementService'
import type { InventoryMovement, InventoryMovementCreate } from '@/types/resource'

interface UseInventoryMovementsResult {
  movements: InventoryMovement[]
  isLoading: boolean
  error: string | null
  fetchMovementsByResource: (resourceId: string) => Promise<void>
  createMovement: (data: InventoryMovementCreate) => Promise<void>
  clearMovements: () => void
}

export const useInventoryMovements = (): UseInventoryMovementsResult => {
  const [movements, setMovements] = useState<InventoryMovement[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMovementsByResource = useCallback(async (resourceId: string) => {
    console.log('INFO [useInventoryMovements]: Fetching movements for resource:', resourceId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await inventoryMovementService.getByResource(resourceId)
      setMovements(data)
      console.log('INFO [useInventoryMovements]: Fetched', data.length, 'movements')
    } catch (err) {
      console.error('ERROR [useInventoryMovements]: Failed to fetch movements:', err)
      setError('Error al cargar movimientos. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createMovement = useCallback(async (data: InventoryMovementCreate) => {
    console.log('INFO [useInventoryMovements]: Creating movement')
    setError(null)

    try {
      await inventoryMovementService.create(data)
      console.log('INFO [useInventoryMovements]: Movement created successfully')
    } catch (err) {
      console.error('ERROR [useInventoryMovements]: Failed to create movement:', err)
      setError('Error al registrar movimiento. Intente de nuevo.')
      throw err
    }
  }, [])

  const clearMovements = useCallback(() => {
    console.log('INFO [useInventoryMovements]: Clearing movements')
    setMovements([])
    setError(null)
  }, [])

  return {
    movements,
    isLoading,
    error,
    fetchMovementsByResource,
    createMovement,
    clearMovements,
  }
}

export default useInventoryMovements

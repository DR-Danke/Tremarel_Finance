import { useState, useEffect, useCallback } from 'react'
import { budgetService } from '@/services/budgetService'
import type {
  BudgetWithSpending,
  BudgetCreate,
  BudgetUpdate,
} from '@/types'

interface UseBudgetsResult {
  budgets: BudgetWithSpending[]
  total: number
  isLoading: boolean
  error: string | null
  fetchBudgets: () => Promise<void>
  createBudget: (data: BudgetCreate) => Promise<void>
  updateBudget: (id: string, data: BudgetUpdate) => Promise<void>
  deleteBudget: (id: string) => Promise<void>
}

export const useBudgets = (entityId: string | null): UseBudgetsResult => {
  const [budgets, setBudgets] = useState<BudgetWithSpending[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchBudgets = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useBudgets]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [useBudgets]: Fetching budgets for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const response = await budgetService.list(entityId)
      setBudgets(response.budgets)
      setTotal(response.total)
      console.log('INFO [useBudgets]: Fetched', response.budgets.length, 'budgets')
    } catch (err) {
      console.error('ERROR [useBudgets]: Failed to fetch budgets:', err)
      setError('Failed to load budgets. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId])

  const createBudget = useCallback(
    async (data: BudgetCreate) => {
      console.log('INFO [useBudgets]: Creating budget')
      setError(null)

      try {
        await budgetService.create(data)
        console.log('INFO [useBudgets]: Budget created, refreshing list')
        await fetchBudgets()
      } catch (err) {
        console.error('ERROR [useBudgets]: Failed to create budget:', err)
        setError('Failed to create budget. Please try again.')
        throw err
      }
    },
    [fetchBudgets]
  )

  const updateBudget = useCallback(
    async (id: string, data: BudgetUpdate) => {
      if (!entityId) {
        console.log('INFO [useBudgets]: No entityId provided, skipping update')
        return
      }
      console.log('INFO [useBudgets]: Updating budget:', id)
      setError(null)

      try {
        await budgetService.update(id, entityId, data)
        console.log('INFO [useBudgets]: Budget updated, refreshing list')
        await fetchBudgets()
      } catch (err) {
        console.error('ERROR [useBudgets]: Failed to update budget:', err)
        setError('Failed to update budget. Please try again.')
        throw err
      }
    },
    [entityId, fetchBudgets]
  )

  const deleteBudget = useCallback(
    async (id: string) => {
      if (!entityId) {
        console.log('INFO [useBudgets]: No entityId provided, skipping delete')
        return
      }
      console.log('INFO [useBudgets]: Deleting budget:', id)
      setError(null)

      try {
        await budgetService.delete(id, entityId)
        console.log('INFO [useBudgets]: Budget deleted, refreshing list')
        await fetchBudgets()
      } catch (err) {
        console.error('ERROR [useBudgets]: Failed to delete budget:', err)
        setError('Failed to delete budget. Please try again.')
        throw err
      }
    },
    [entityId, fetchBudgets]
  )

  // Fetch budgets when entityId changes
  useEffect(() => {
    fetchBudgets()
  }, [fetchBudgets])

  return {
    budgets,
    total,
    isLoading,
    error,
    fetchBudgets,
    createBudget,
    updateBudget,
    deleteBudget,
  }
}

export default useBudgets

import { apiClient } from '@/api/clients'
import type {
  Budget,
  BudgetCreate,
  BudgetUpdate,
  BudgetWithSpending,
  BudgetListResponse,
} from '@/types'

/**
 * Budget service for CRUD operations on budgets.
 */
export const budgetService = {
  /**
   * Create a new budget.
   * @param data - Budget creation data
   * @returns Created budget
   */
  async create(data: BudgetCreate): Promise<Budget> {
    console.log('INFO [BudgetService]: Creating budget for entity:', data.entity_id)
    try {
      const response = await apiClient.post<Budget>('/budgets/', data)
      console.log('INFO [BudgetService]: Budget created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [BudgetService]: Failed to create budget:', error)
      throw error
    }
  },

  /**
   * List budgets for an entity with spending information.
   * @param entityId - Entity ID to filter by
   * @param skip - Number of records to skip
   * @param limit - Maximum records to return
   * @returns List of budgets with spending and total count
   */
  async list(
    entityId: string,
    skip = 0,
    limit = 100
  ): Promise<BudgetListResponse> {
    console.log('INFO [BudgetService]: Listing budgets for entity:', entityId)
    try {
      const params = new URLSearchParams()
      params.append('entity_id', entityId)
      params.append('skip', skip.toString())
      params.append('limit', limit.toString())

      const response = await apiClient.get<BudgetListResponse>(
        `/budgets/?${params.toString()}`
      )
      console.log(
        'INFO [BudgetService]: Fetched',
        response.data.budgets.length,
        'budgets (total:',
        response.data.total,
        ')'
      )
      return response.data
    } catch (error) {
      console.error('ERROR [BudgetService]: Failed to list budgets:', error)
      throw error
    }
  },

  /**
   * Get a single budget by ID with spending information.
   * @param budgetId - Budget ID
   * @param entityId - Entity ID for validation
   * @returns Budget data with spending
   */
  async get(budgetId: string, entityId: string): Promise<BudgetWithSpending> {
    console.log('INFO [BudgetService]: Getting budget:', budgetId)
    try {
      const response = await apiClient.get<BudgetWithSpending>(
        `/budgets/${budgetId}?entity_id=${entityId}`
      )
      console.log('INFO [BudgetService]: Budget fetched:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [BudgetService]: Failed to get budget:', error)
      throw error
    }
  },

  /**
   * Update an existing budget.
   * @param budgetId - Budget ID to update
   * @param entityId - Entity ID for validation
   * @param data - Update data
   * @returns Updated budget
   */
  async update(
    budgetId: string,
    entityId: string,
    data: BudgetUpdate
  ): Promise<Budget> {
    console.log('INFO [BudgetService]: Updating budget:', budgetId)
    try {
      const response = await apiClient.put<Budget>(
        `/budgets/${budgetId}?entity_id=${entityId}`,
        data
      )
      console.log('INFO [BudgetService]: Budget updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [BudgetService]: Failed to update budget:', error)
      throw error
    }
  },

  /**
   * Delete a budget.
   * @param budgetId - Budget ID to delete
   * @param entityId - Entity ID for validation
   */
  async delete(budgetId: string, entityId: string): Promise<void> {
    console.log('INFO [BudgetService]: Deleting budget:', budgetId)
    try {
      await apiClient.delete(`/budgets/${budgetId}?entity_id=${entityId}`)
      console.log('INFO [BudgetService]: Budget deleted:', budgetId)
    } catch (error) {
      console.error('ERROR [BudgetService]: Failed to delete budget:', error)
      throw error
    }
  },
}

export default budgetService

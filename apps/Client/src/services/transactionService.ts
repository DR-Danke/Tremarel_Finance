import { apiClient } from '@/api/clients'
import type {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  TransactionFilters,
  TransactionListResponse,
} from '@/types'

/**
 * Transaction service for CRUD operations on transactions.
 */
export const transactionService = {
  /**
   * Create a new transaction.
   * @param data - Transaction creation data
   * @returns Created transaction
   */
  async create(data: TransactionCreate): Promise<Transaction> {
    console.log('INFO [TransactionService]: Creating transaction for entity:', data.entity_id)
    try {
      const response = await apiClient.post<Transaction>('/transactions/', data)
      console.log('INFO [TransactionService]: Transaction created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [TransactionService]: Failed to create transaction:', error)
      throw error
    }
  },

  /**
   * List transactions for an entity with optional filters.
   * @param entityId - Entity ID to filter by
   * @param filters - Optional filter criteria
   * @param skip - Number of records to skip
   * @param limit - Maximum records to return
   * @returns List of transactions with total count
   */
  async list(
    entityId: string,
    filters?: TransactionFilters,
    skip = 0,
    limit = 100
  ): Promise<TransactionListResponse> {
    console.log('INFO [TransactionService]: Listing transactions for entity:', entityId)
    try {
      const params = new URLSearchParams()
      params.append('entity_id', entityId)
      params.append('skip', skip.toString())
      params.append('limit', limit.toString())

      if (filters?.start_date) {
        params.append('start_date', filters.start_date)
      }
      if (filters?.end_date) {
        params.append('end_date', filters.end_date)
      }
      if (filters?.category_id) {
        params.append('category_id', filters.category_id)
      }
      if (filters?.type) {
        params.append('type', filters.type)
      }

      const response = await apiClient.get<TransactionListResponse>(
        `/transactions/?${params.toString()}`
      )
      console.log(
        'INFO [TransactionService]: Fetched',
        response.data.transactions.length,
        'transactions (total:',
        response.data.total,
        ')'
      )
      return response.data
    } catch (error) {
      console.error('ERROR [TransactionService]: Failed to list transactions:', error)
      throw error
    }
  },

  /**
   * Get a single transaction by ID.
   * @param transactionId - Transaction ID
   * @param entityId - Entity ID for validation
   * @returns Transaction data
   */
  async get(transactionId: string, entityId: string): Promise<Transaction> {
    console.log('INFO [TransactionService]: Getting transaction:', transactionId)
    try {
      const response = await apiClient.get<Transaction>(
        `/transactions/${transactionId}?entity_id=${entityId}`
      )
      console.log('INFO [TransactionService]: Transaction fetched:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [TransactionService]: Failed to get transaction:', error)
      throw error
    }
  },

  /**
   * Update an existing transaction.
   * @param transactionId - Transaction ID to update
   * @param entityId - Entity ID for validation
   * @param data - Update data
   * @returns Updated transaction
   */
  async update(
    transactionId: string,
    entityId: string,
    data: TransactionUpdate
  ): Promise<Transaction> {
    console.log('INFO [TransactionService]: Updating transaction:', transactionId)
    try {
      const response = await apiClient.put<Transaction>(
        `/transactions/${transactionId}?entity_id=${entityId}`,
        data
      )
      console.log('INFO [TransactionService]: Transaction updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [TransactionService]: Failed to update transaction:', error)
      throw error
    }
  },

  /**
   * Delete a transaction.
   * @param transactionId - Transaction ID to delete
   * @param entityId - Entity ID for validation
   */
  async delete(transactionId: string, entityId: string): Promise<void> {
    console.log('INFO [TransactionService]: Deleting transaction:', transactionId)
    try {
      await apiClient.delete(`/transactions/${transactionId}?entity_id=${entityId}`)
      console.log('INFO [TransactionService]: Transaction deleted:', transactionId)
    } catch (error) {
      console.error('ERROR [TransactionService]: Failed to delete transaction:', error)
      throw error
    }
  },
}

export default transactionService

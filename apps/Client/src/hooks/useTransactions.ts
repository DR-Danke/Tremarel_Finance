import { useState, useEffect, useCallback } from 'react'
import { transactionService } from '@/services/transactionService'
import type {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  TransactionFilters,
} from '@/types'

interface UseTransactionsResult {
  transactions: Transaction[]
  total: number
  isLoading: boolean
  error: string | null
  filters: TransactionFilters
  fetchTransactions: () => Promise<void>
  createTransaction: (data: TransactionCreate) => Promise<void>
  updateTransaction: (id: string, data: TransactionUpdate) => Promise<void>
  deleteTransaction: (id: string) => Promise<void>
  setFilters: (filters: TransactionFilters) => void
}

export const useTransactions = (entityId: string | null): UseTransactionsResult => {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<TransactionFilters>({})

  const fetchTransactions = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useTransactions]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [useTransactions]: Fetching transactions for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const response = await transactionService.list(entityId, filters)
      setTransactions(response.transactions)
      setTotal(response.total)
      console.log('INFO [useTransactions]: Fetched', response.transactions.length, 'transactions')
    } catch (err) {
      console.error('ERROR [useTransactions]: Failed to fetch transactions:', err)
      setError('Failed to load transactions. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId, filters])

  const createTransaction = useCallback(
    async (data: TransactionCreate) => {
      console.log('INFO [useTransactions]: Creating transaction')
      setError(null)

      try {
        await transactionService.create(data)
        console.log('INFO [useTransactions]: Transaction created, refreshing list')
        await fetchTransactions()
      } catch (err) {
        console.error('ERROR [useTransactions]: Failed to create transaction:', err)
        setError('Failed to create transaction. Please try again.')
        throw err
      }
    },
    [fetchTransactions]
  )

  const updateTransaction = useCallback(
    async (id: string, data: TransactionUpdate) => {
      if (!entityId) {
        console.log('INFO [useTransactions]: No entityId provided, skipping update')
        return
      }
      console.log('INFO [useTransactions]: Updating transaction:', id)
      setError(null)

      try {
        await transactionService.update(id, entityId, data)
        console.log('INFO [useTransactions]: Transaction updated, refreshing list')
        await fetchTransactions()
      } catch (err) {
        console.error('ERROR [useTransactions]: Failed to update transaction:', err)
        setError('Failed to update transaction. Please try again.')
        throw err
      }
    },
    [entityId, fetchTransactions]
  )

  const deleteTransaction = useCallback(
    async (id: string) => {
      if (!entityId) {
        console.log('INFO [useTransactions]: No entityId provided, skipping delete')
        return
      }
      console.log('INFO [useTransactions]: Deleting transaction:', id)
      setError(null)

      try {
        await transactionService.delete(id, entityId)
        console.log('INFO [useTransactions]: Transaction deleted, refreshing list')
        await fetchTransactions()
      } catch (err) {
        console.error('ERROR [useTransactions]: Failed to delete transaction:', err)
        setError('Failed to delete transaction. Please try again.')
        throw err
      }
    },
    [entityId, fetchTransactions]
  )

  // Fetch transactions when entityId or filters change
  useEffect(() => {
    fetchTransactions()
  }, [fetchTransactions])

  return {
    transactions,
    total,
    isLoading,
    error,
    filters,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    setFilters,
  }
}

export default useTransactions

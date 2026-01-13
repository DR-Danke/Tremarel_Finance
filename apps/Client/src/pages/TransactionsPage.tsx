import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  DialogActions,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import { useAuth } from '@/hooks/useAuth'
import { useTransactions } from '@/hooks/useTransactions'
import { TRTransactionForm } from '@/components/forms/TRTransactionForm'
import { TRTransactionTable } from '@/components/ui/TRTransactionTable'
import type { Transaction, TransactionCreate, TransactionUpdate, Category } from '@/types'
import { apiClient } from '@/api/clients'

// Mock categories for testing - will be replaced with actual category service
const MOCK_CATEGORIES: Category[] = [
  { id: '1', entity_id: '', name: 'Salary', type: 'income', is_active: true, created_at: '' },
  { id: '2', entity_id: '', name: 'Freelance', type: 'income', is_active: true, created_at: '' },
  { id: '3', entity_id: '', name: 'Food & Dining', type: 'expense', is_active: true, created_at: '' },
  { id: '4', entity_id: '', name: 'Transportation', type: 'expense', is_active: true, created_at: '' },
  { id: '5', entity_id: '', name: 'Utilities', type: 'expense', is_active: true, created_at: '' },
]

// Placeholder entity ID - will be replaced with EntityContext
const PLACEHOLDER_ENTITY_ID = 'b4e8f9a0-1234-5678-9abc-def012345678'

export const TransactionsPage: React.FC = () => {
  const { user } = useAuth()
  const [searchParams] = useSearchParams()

  // Use entity_id from URL params if available, otherwise use placeholder
  const entityId = searchParams.get('entity_id') || PLACEHOLDER_ENTITY_ID

  const {
    transactions,
    total,
    isLoading,
    error,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    setFilters,
  } = useTransactions(entityId)

  // Dialog state
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [operationError, setOperationError] = useState<string | null>(null)

  // Categories state
  const [categories, setCategories] = useState<Category[]>(MOCK_CATEGORIES)

  // Filter state
  const [filterStartDate, setFilterStartDate] = useState('')
  const [filterEndDate, setFilterEndDate] = useState('')
  const [filterType, setFilterType] = useState<string>('')

  // Check if user can delete (admin or manager)
  const canDelete = user?.role === 'admin' || user?.role === 'manager'

  // Create category lookup map
  const categoryMap = useMemo(() => {
    const map: Record<string, Category> = {}
    categories.forEach((cat) => {
      map[cat.id] = cat
    })
    return map
  }, [categories])

  // Attempt to load real categories (will fail gracefully if categories endpoint doesn't exist yet)
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await apiClient.get<{ categories: Category[] }>(
          `/categories?entity_id=${entityId}`
        )
        if (response.data.categories && response.data.categories.length > 0) {
          setCategories(response.data.categories)
          console.log('INFO [TransactionsPage]: Loaded', response.data.categories.length, 'categories')
        }
      } catch (err) {
        console.log('INFO [TransactionsPage]: Using mock categories (category API not available)')
      }
    }
    loadCategories()
  }, [entityId])

  const handleOpenAddDialog = () => {
    console.log('INFO [TransactionsPage]: Opening add transaction dialog')
    setOperationError(null)
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [TransactionsPage]: Closing add transaction dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (transaction: Transaction) => {
    console.log('INFO [TransactionsPage]: Opening edit dialog for transaction:', transaction.id)
    setOperationError(null)
    setSelectedTransaction(transaction)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [TransactionsPage]: Closing edit transaction dialog')
    setIsEditDialogOpen(false)
    setSelectedTransaction(null)
  }

  const handleOpenDeleteDialog = (transactionId: string) => {
    console.log('INFO [TransactionsPage]: Opening delete dialog for transaction:', transactionId)
    setOperationError(null)
    const transaction = transactions.find((t) => t.id === transactionId)
    if (transaction) {
      setSelectedTransaction(transaction)
      setIsDeleteDialogOpen(true)
    }
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [TransactionsPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedTransaction(null)
  }

  const handleCreateTransaction = async (data: TransactionCreate) => {
    console.log('INFO [TransactionsPage]: Creating transaction')
    try {
      await createTransaction(data)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [TransactionsPage]: Failed to create transaction:', err)
      setOperationError('Failed to create transaction. Please try again.')
    }
  }

  const handleUpdateTransaction = async (data: TransactionCreate) => {
    if (!selectedTransaction) return

    console.log('INFO [TransactionsPage]: Updating transaction:', selectedTransaction.id)
    try {
      const updateData: TransactionUpdate = {
        category_id: data.category_id,
        amount: data.amount,
        type: data.type,
        description: data.description,
        date: data.date,
        notes: data.notes,
      }
      await updateTransaction(selectedTransaction.id, updateData)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [TransactionsPage]: Failed to update transaction:', err)
      setOperationError('Failed to update transaction. Please try again.')
    }
  }

  const handleDeleteTransaction = async () => {
    if (!selectedTransaction) return

    console.log('INFO [TransactionsPage]: Deleting transaction:', selectedTransaction.id)
    try {
      await deleteTransaction(selectedTransaction.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [TransactionsPage]: Failed to delete transaction:', err)
      setOperationError('Failed to delete transaction. Please try again.')
    }
  }

  const handleApplyFilters = () => {
    console.log('INFO [TransactionsPage]: Applying filters')
    setFilters({
      start_date: filterStartDate || undefined,
      end_date: filterEndDate || undefined,
      type: filterType as 'income' | 'expense' | undefined,
    })
  }

  const handleClearFilters = () => {
    console.log('INFO [TransactionsPage]: Clearing filters')
    setFilterStartDate('')
    setFilterEndDate('')
    setFilterType('')
    setFilters({})
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Typography variant="h4" component="h1">
            Transactions
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenAddDialog}
          >
            Add Transaction
          </Button>
        </Box>

        {/* Global error display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <TextField
                label="Start Date"
                type="date"
                value={filterStartDate}
                onChange={(e) => setFilterStartDate(e.target.value)}
                fullWidth
                size="small"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                label="End Date"
                type="date"
                value={filterEndDate}
                onChange={(e) => setFilterEndDate(e.target.value)}
                fullWidth
                size="small"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Type</InputLabel>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="income">Income</MenuItem>
                  <MenuItem value="expense">Expense</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button variant="contained" size="small" onClick={handleApplyFilters}>
                  Apply
                </Button>
                <Button variant="outlined" size="small" onClick={handleClearFilters}>
                  Clear
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Transaction count */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Showing {transactions.length} of {total} transactions
        </Typography>

        {/* Transactions table */}
        <TRTransactionTable
          transactions={transactions}
          categories={categoryMap}
          onEdit={handleOpenEditDialog}
          onDelete={handleOpenDeleteDialog}
          isLoading={isLoading}
          canDelete={canDelete}
        />

        {/* Add Transaction Dialog */}
        <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Add Transaction</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              <TRTransactionForm
                onSubmit={handleCreateTransaction}
                categories={categories}
                entityId={entityId}
                onCancel={handleCloseAddDialog}
              />
            </Box>
          </DialogContent>
        </Dialog>

        {/* Edit Transaction Dialog */}
        <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Edit Transaction</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              {selectedTransaction && (
                <TRTransactionForm
                  onSubmit={handleUpdateTransaction}
                  initialData={selectedTransaction}
                  categories={categories}
                  entityId={entityId}
                  onCancel={handleCloseEditDialog}
                />
              )}
            </Box>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
          <DialogTitle>Delete Transaction</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Typography>
              Are you sure you want to delete this transaction?
            </Typography>
            {selectedTransaction && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2">
                  <strong>Type:</strong> {selectedTransaction.type}
                </Typography>
                <Typography variant="body2">
                  <strong>Amount:</strong> ${selectedTransaction.amount}
                </Typography>
                <Typography variant="body2">
                  <strong>Date:</strong> {selectedTransaction.date}
                </Typography>
                {selectedTransaction.description && (
                  <Typography variant="body2">
                    <strong>Description:</strong> {selectedTransaction.description}
                  </Typography>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
            <Button onClick={handleDeleteTransaction} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  )
}

export default TransactionsPage

import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
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
  CircularProgress,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import { useAuth } from '@/hooks/useAuth'
import { useTransactions } from '@/hooks/useTransactions'
import { useEntity } from '@/hooks/useEntity'
import { TRTransactionForm } from '@/components/forms/TRTransactionForm'
import { TRTransactionTable } from '@/components/ui/TRTransactionTable'
import { categoryService } from '@/services/categoryService'
import type { Transaction, TransactionCreate, TransactionUpdate, Category } from '@/types'

export const TransactionsPage: React.FC = () => {
  const { user } = useAuth()

  // Get current entity from EntityContext
  const { currentEntity, entities, isLoading: entityLoading } = useEntity()
  const entityId = currentEntity?.id || null

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
  const [categories, setCategories] = useState<Category[]>([])

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

  // Load categories using categoryService
  useEffect(() => {
    const loadCategories = async () => {
      if (!entityId) {
        console.log('INFO [TransactionsPage]: No entityId, skipping category load')
        return
      }
      try {
        const fetchedCategories = await categoryService.getCategories(entityId)
        if (fetchedCategories && fetchedCategories.length > 0) {
          setCategories(fetchedCategories)
          console.log('INFO [TransactionsPage]: Loaded', fetchedCategories.length, 'categories from API')
        } else {
          console.log('INFO [TransactionsPage]: No categories found for entity')
        }
      } catch (err) {
        console.error('ERROR [TransactionsPage]: Failed to load categories:', err)
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

  // Show loading state while entity context is loading
  if (entityLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  // Show message if no entity is selected
  if (!currentEntity) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Transactions
          </Typography>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Entity Selected
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {entities.length === 0
                ? 'Create your first entity to start tracking transactions.'
                : 'Select an entity to view and manage its transactions.'}
            </Typography>
            <Button
              variant="contained"
              component={Link}
              to="/entities"
              sx={{ mt: 2 }}
            >
              {entities.length === 0 ? 'Create Entity' : 'Manage Entities'}
            </Button>
          </Paper>
        </Box>
      </Container>
    )
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

        {/* Current Entity Info */}
        <Paper elevation={1} sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
          <Typography variant="body2" color="text.secondary">
            Managing transactions for: <strong>{currentEntity.name}</strong>
          </Typography>
        </Paper>

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
                entityId={currentEntity.id}
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
                  entityId={currentEntity.id}
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

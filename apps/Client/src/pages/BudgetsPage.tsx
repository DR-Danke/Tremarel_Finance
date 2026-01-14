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
  DialogActions,
  Alert,
  Grid,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import { useAuth } from '@/hooks/useAuth'
import { useBudgets } from '@/hooks/useBudgets'
import { useEntity } from '@/hooks/useEntity'
import { TRBudgetForm } from '@/components/forms/TRBudgetForm'
import { TRBudgetCard } from '@/components/ui/TRBudgetCard'
import type { BudgetWithSpending, BudgetCreate, BudgetUpdate, Category } from '@/types'
import { categoryService } from '@/services/categoryService'

export const BudgetsPage: React.FC = () => {
  const { user } = useAuth()

  // Get current entity from EntityContext
  const { currentEntity, entities, isLoading: entityLoading } = useEntity()
  const entityId = currentEntity?.id || null

  const {
    budgets,
    total,
    isLoading,
    error,
    createBudget,
    updateBudget,
    deleteBudget,
  } = useBudgets(entityId)

  // Dialog state
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedBudget, setSelectedBudget] = useState<BudgetWithSpending | null>(null)
  const [operationError, setOperationError] = useState<string | null>(null)

  // Categories state
  const [categories, setCategories] = useState<Category[]>([])
  const [categoriesLoading, setCategoriesLoading] = useState(false)

  // Check if user can delete (admin or manager)
  const canDelete = user?.role === 'admin' || user?.role === 'manager'

  // Load categories
  useEffect(() => {
    const loadCategories = async () => {
      if (!entityId) {
        console.log('INFO [BudgetsPage]: No entityId, skipping category load')
        return
      }
      setCategoriesLoading(true)
      try {
        const fetchedCategories = await categoryService.getCategories(entityId)
        if (fetchedCategories && fetchedCategories.length > 0) {
          setCategories(fetchedCategories)
          console.log('INFO [BudgetsPage]: Loaded', fetchedCategories.length, 'categories from API')
        }
      } catch (err) {
        console.error('ERROR [BudgetsPage]: Failed to load categories:', err)
      } finally {
        setCategoriesLoading(false)
      }
    }
    loadCategories()
  }, [entityId])

  // Calculate summary stats
  const summaryStats = useMemo(() => {
    const totalBudgeted = budgets.reduce((sum, b) => sum + b.amount, 0)
    const totalSpent = budgets.reduce((sum, b) => sum + b.spent_amount, 0)
    const overBudgetCount = budgets.filter((b) => b.spent_percentage > 100).length
    const underBudgetCount = budgets.filter((b) => b.spent_percentage <= 100).length

    return {
      totalBudgeted,
      totalSpent,
      overBudgetCount,
      underBudgetCount,
    }
  }, [budgets])

  const handleOpenAddDialog = () => {
    console.log('INFO [BudgetsPage]: Opening add budget dialog')
    setOperationError(null)
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [BudgetsPage]: Closing add budget dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (budget: BudgetWithSpending) => {
    console.log('INFO [BudgetsPage]: Opening edit dialog for budget:', budget.id)
    setOperationError(null)
    setSelectedBudget(budget)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [BudgetsPage]: Closing edit budget dialog')
    setIsEditDialogOpen(false)
    setSelectedBudget(null)
  }

  const handleOpenDeleteDialog = (budgetId: string) => {
    console.log('INFO [BudgetsPage]: Opening delete dialog for budget:', budgetId)
    setOperationError(null)
    const budget = budgets.find((b) => b.id === budgetId)
    if (budget) {
      setSelectedBudget(budget)
      setIsDeleteDialogOpen(true)
    }
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [BudgetsPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedBudget(null)
  }

  const handleCreateBudget = async (data: BudgetCreate) => {
    console.log('INFO [BudgetsPage]: Creating budget')
    try {
      await createBudget(data)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [BudgetsPage]: Failed to create budget:', err)
      setOperationError('Failed to create budget. Please try again.')
    }
  }

  const handleUpdateBudget = async (data: BudgetCreate) => {
    if (!selectedBudget) return

    console.log('INFO [BudgetsPage]: Updating budget:', selectedBudget.id)
    try {
      const updateData: BudgetUpdate = {
        amount: data.amount,
        period_type: data.period_type,
        start_date: data.start_date,
      }
      await updateBudget(selectedBudget.id, updateData)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [BudgetsPage]: Failed to update budget:', err)
      setOperationError('Failed to update budget. Please try again.')
    }
  }

  const handleDeleteBudget = async () => {
    if (!selectedBudget) return

    console.log('INFO [BudgetsPage]: Deleting budget:', selectedBudget.id)
    try {
      await deleteBudget(selectedBudget.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [BudgetsPage]: Failed to delete budget:', err)
      setOperationError('Failed to delete budget. Please try again.')
    }
  }

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount)
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
            Budgets
          </Typography>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Entity Selected
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {entities.length === 0
                ? 'Create your first entity to start managing budgets.'
                : 'Select an entity to view and manage its budgets.'}
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
            Budgets
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenAddDialog}
            disabled={categoriesLoading}
          >
            Add Budget
          </Button>
        </Box>

        {/* Current Entity Info */}
        <Paper elevation={1} sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
          <Typography variant="body2" color="text.secondary">
            Managing budgets for: <strong>{currentEntity.name}</strong>
          </Typography>
        </Paper>

        {/* Global error display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Summary Stats */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Budgeted
                </Typography>
                <Typography variant="h5" component="div">
                  {formatCurrency(summaryStats.totalBudgeted)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Spent
                </Typography>
                <Typography variant="h5" component="div">
                  {formatCurrency(summaryStats.totalSpent)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Under Budget
                </Typography>
                <Typography variant="h5" component="div" color="success.main">
                  {summaryStats.underBudgetCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Over Budget
                </Typography>
                <Typography variant="h5" component="div" color="error.main">
                  {summaryStats.overBudgetCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Budget count */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Showing {budgets.length} of {total} budgets
        </Typography>

        {/* Loading state */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Empty state */}
        {!isLoading && budgets.length === 0 && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No budgets yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Create a budget to start tracking your spending against your goals.
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleOpenAddDialog}
              disabled={categoriesLoading}
            >
              Create Your First Budget
            </Button>
          </Paper>
        )}

        {/* Budget cards grid */}
        {!isLoading && budgets.length > 0 && (
          <Grid container spacing={3}>
            {budgets.map((budget) => (
              <Grid item xs={12} sm={6} md={4} key={budget.id}>
                <TRBudgetCard
                  budget={budget}
                  onEdit={handleOpenEditDialog}
                  onDelete={handleOpenDeleteDialog}
                  canDelete={canDelete}
                />
              </Grid>
            ))}
          </Grid>
        )}

        {/* Add Budget Dialog */}
        <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Add Budget</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              <TRBudgetForm
                onSubmit={handleCreateBudget}
                categories={categories}
                entityId={currentEntity.id}
                onCancel={handleCloseAddDialog}
              />
            </Box>
          </DialogContent>
        </Dialog>

        {/* Edit Budget Dialog */}
        <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Edit Budget</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              {selectedBudget && (
                <TRBudgetForm
                  onSubmit={handleUpdateBudget}
                  initialData={selectedBudget}
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
          <DialogTitle>Delete Budget</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Typography>
              Are you sure you want to delete this budget?
            </Typography>
            {selectedBudget && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2">
                  <strong>Category:</strong> {selectedBudget.category_name || 'Unknown'}
                </Typography>
                <Typography variant="body2">
                  <strong>Amount:</strong> {formatCurrency(selectedBudget.amount)}
                </Typography>
                <Typography variant="body2">
                  <strong>Period:</strong> {selectedBudget.period_type}
                </Typography>
                <Typography variant="body2">
                  <strong>Spent:</strong> {formatCurrency(selectedBudget.spent_amount)} ({selectedBudget.spent_percentage.toFixed(1)}%)
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
            <Button onClick={handleDeleteBudget} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  )
}

export default BudgetsPage

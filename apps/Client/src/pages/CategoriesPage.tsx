import { useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
  Box,
  CircularProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { TRCategoryForm } from '@/components/forms/TRCategoryForm'
import { TRCategoryTree } from '@/components/ui/TRCategoryTree'
import { useCategories } from '@/hooks/useCategories'
import type { Category, CategoryTree, CategoryCreateInput, CategoryUpdateInput } from '@/types'
import { AxiosError } from 'axios'

// Default entity ID for development/testing
// In production, this would come from EntityContext
const DEFAULT_ENTITY_ID = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'

/**
 * Categories management page.
 * Displays category tree and provides CRUD operations.
 */
export const CategoriesPage: React.FC = () => {
  // Get entityId from URL params or use default
  const { entityId: urlEntityId } = useParams<{ entityId?: string }>()
  const entityId = urlEntityId || DEFAULT_ENTITY_ID

  // Category state and operations
  const {
    categories,
    categoryTree,
    loading,
    error: categoriesError,
    createCategory,
    updateCategory,
    deleteCategory,
    clearError,
  } = useCategories(entityId)

  // Dialog and form state
  const [isFormDialogOpen, setIsFormDialogOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | undefined>(undefined)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [categoryToDelete, setCategoryToDelete] = useState<CategoryTree | null>(null)

  // Notification state
  const [notification, setNotification] = useState<{
    open: boolean
    message: string
    severity: 'success' | 'error'
  }>({
    open: false,
    message: '',
    severity: 'success',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  const showNotification = (message: string, severity: 'success' | 'error') => {
    setNotification({ open: true, message, severity })
  }

  const handleCloseNotification = () => {
    setNotification((prev) => ({ ...prev, open: false }))
  }

  // Form dialog handlers
  const handleOpenCreateForm = () => {
    console.log('INFO [CategoriesPage]: Opening create form')
    setEditingCategory(undefined)
    setIsFormDialogOpen(true)
  }

  const handleOpenEditForm = (category: CategoryTree) => {
    console.log(`INFO [CategoriesPage]: Opening edit form for ${category.name}`)
    setEditingCategory(category as Category)
    setIsFormDialogOpen(true)
  }

  const handleCloseForm = () => {
    console.log('INFO [CategoriesPage]: Closing form dialog')
    setIsFormDialogOpen(false)
    setEditingCategory(undefined)
  }

  const handleFormSubmit = async (data: CategoryCreateInput | CategoryUpdateInput) => {
    setIsSubmitting(true)
    try {
      if (editingCategory) {
        await updateCategory(editingCategory.id, data as CategoryUpdateInput)
        showNotification('Category updated successfully', 'success')
      } else {
        await createCategory(data as CategoryCreateInput)
        showNotification('Category created successfully', 'success')
      }
      handleCloseForm()
    } catch (err) {
      console.error('ERROR [CategoriesPage]: Form submission failed:', err)
      let errorMessage = 'An error occurred'
      if (err instanceof AxiosError) {
        errorMessage = err.response?.data?.detail || err.message
      }
      showNotification(errorMessage, 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Delete dialog handlers
  const handleOpenDeleteDialog = (category: CategoryTree) => {
    console.log(`INFO [CategoriesPage]: Opening delete dialog for ${category.name}`)
    setCategoryToDelete(category)
    setIsDeleteDialogOpen(true)
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [CategoriesPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setCategoryToDelete(null)
  }

  const handleConfirmDelete = async () => {
    if (!categoryToDelete) return

    setIsSubmitting(true)
    try {
      await deleteCategory(categoryToDelete.id)
      showNotification('Category deleted successfully', 'success')
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [CategoriesPage]: Delete failed:', err)
      let errorMessage = 'Failed to delete category'
      if (err instanceof AxiosError) {
        errorMessage = err.response?.data?.detail || err.message
      }
      showNotification(errorMessage, 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Clear error when component unmounts
  if (categoriesError) {
    console.error('ERROR [CategoriesPage]: Categories error:', categoriesError)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Categories
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateForm}
          disabled={loading}
        >
          Add Category
        </Button>
      </Box>

      {/* Error Alert */}
      {categoriesError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
          {categoriesError}
        </Alert>
      )}

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, minHeight: 400 }}>
            <Typography variant="h6" gutterBottom>
              Category Tree
            </Typography>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TRCategoryTree
                categories={categoryTree}
                onEdit={handleOpenEditForm}
                onDelete={handleOpenDeleteDialog}
              />
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Create/Edit Dialog */}
      <Dialog open={isFormDialogOpen} onClose={handleCloseForm} maxWidth="sm" fullWidth>
        <DialogTitle>{editingCategory ? 'Edit Category' : 'Create Category'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TRCategoryForm
              onSubmit={handleFormSubmit}
              category={editingCategory}
              parentCategories={categories}
              entityId={entityId}
              onCancel={handleCloseForm}
              isLoading={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Delete Category</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the category "{categoryToDelete?.name}"?
          </Typography>
          {categoryToDelete?.children && categoryToDelete.children.length > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This category has subcategories. Please delete or reassign them first.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseNotification} severity={notification.severity}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  )
}

export default CategoriesPage

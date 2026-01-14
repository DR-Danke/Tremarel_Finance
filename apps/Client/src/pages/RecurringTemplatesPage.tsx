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
  FormControlLabel,
  Switch,
  DialogActions,
  CircularProgress,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import { useAuth } from '@/hooks/useAuth'
import { useRecurringTemplates } from '@/hooks/useRecurringTemplates'
import { useEntity } from '@/hooks/useEntity'
import { TRRecurringTemplateForm } from '@/components/forms/TRRecurringTemplateForm'
import { TRRecurringTemplateTable } from '@/components/ui/TRRecurringTemplateTable'
import type { RecurringTemplate, RecurringTemplateCreate, RecurringTemplateUpdate, Category } from '@/types'
import { categoryService } from '@/services/categoryService'

export const RecurringTemplatesPage: React.FC = () => {
  const { user } = useAuth()

  // Get current entity from EntityContext
  const { currentEntity, entities, isLoading: entityLoading } = useEntity()
  const entityId = currentEntity?.id || null

  const {
    templates,
    total,
    isLoading,
    error,
    includeInactive,
    createTemplate,
    updateTemplate,
    deactivateTemplate,
    deleteTemplate,
    setIncludeInactive,
  } = useRecurringTemplates(entityId)

  // Dialog state
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeactivateDialogOpen, setIsDeactivateDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<RecurringTemplate | null>(null)
  const [operationError, setOperationError] = useState<string | null>(null)

  // Categories state
  const [categories, setCategories] = useState<Category[]>([])

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

  // Load categories
  useEffect(() => {
    const loadCategories = async () => {
      if (!entityId) {
        console.log('INFO [RecurringTemplatesPage]: No entityId, skipping category load')
        return
      }
      try {
        const fetchedCategories = await categoryService.getCategories(entityId)
        if (fetchedCategories && fetchedCategories.length > 0) {
          setCategories(fetchedCategories)
          console.log('INFO [RecurringTemplatesPage]: Loaded', fetchedCategories.length, 'categories from API')
        }
      } catch (err) {
        console.error('ERROR [RecurringTemplatesPage]: Failed to load categories:', err)
      }
    }
    loadCategories()
  }, [entityId])

  const handleOpenAddDialog = () => {
    console.log('INFO [RecurringTemplatesPage]: Opening add template dialog')
    setOperationError(null)
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [RecurringTemplatesPage]: Closing add template dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (template: RecurringTemplate) => {
    console.log('INFO [RecurringTemplatesPage]: Opening edit dialog for template:', template.id)
    setOperationError(null)
    setSelectedTemplate(template)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [RecurringTemplatesPage]: Closing edit template dialog')
    setIsEditDialogOpen(false)
    setSelectedTemplate(null)
  }

  const handleOpenDeactivateDialog = (templateId: string) => {
    console.log('INFO [RecurringTemplatesPage]: Opening deactivate dialog for template:', templateId)
    setOperationError(null)
    const template = templates.find((t) => t.id === templateId)
    if (template) {
      setSelectedTemplate(template)
      setIsDeactivateDialogOpen(true)
    }
  }

  const handleCloseDeactivateDialog = () => {
    console.log('INFO [RecurringTemplatesPage]: Closing deactivate dialog')
    setIsDeactivateDialogOpen(false)
    setSelectedTemplate(null)
  }

  const handleOpenDeleteDialog = (templateId: string) => {
    console.log('INFO [RecurringTemplatesPage]: Opening delete dialog for template:', templateId)
    setOperationError(null)
    const template = templates.find((t) => t.id === templateId)
    if (template) {
      setSelectedTemplate(template)
      setIsDeleteDialogOpen(true)
    }
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [RecurringTemplatesPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedTemplate(null)
  }

  const handleCreateTemplate = async (data: RecurringTemplateCreate) => {
    console.log('INFO [RecurringTemplatesPage]: Creating template')
    try {
      await createTemplate(data)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [RecurringTemplatesPage]: Failed to create template:', err)
      setOperationError('Failed to create template. Please try again.')
    }
  }

  const handleUpdateTemplate = async (data: RecurringTemplateCreate) => {
    if (!selectedTemplate) return

    console.log('INFO [RecurringTemplatesPage]: Updating template:', selectedTemplate.id)
    try {
      const updateData: RecurringTemplateUpdate = {
        category_id: data.category_id,
        name: data.name,
        amount: data.amount,
        type: data.type,
        frequency: data.frequency,
        start_date: data.start_date,
        end_date: data.end_date,
        description: data.description,
        notes: data.notes,
      }
      await updateTemplate(selectedTemplate.id, updateData)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [RecurringTemplatesPage]: Failed to update template:', err)
      setOperationError('Failed to update template. Please try again.')
    }
  }

  const handleDeactivateTemplate = async () => {
    if (!selectedTemplate) return

    console.log('INFO [RecurringTemplatesPage]: Deactivating template:', selectedTemplate.id)
    try {
      await deactivateTemplate(selectedTemplate.id)
      handleCloseDeactivateDialog()
    } catch (err) {
      console.error('ERROR [RecurringTemplatesPage]: Failed to deactivate template:', err)
      setOperationError('Failed to deactivate template. Please try again.')
    }
  }

  const handleDeleteTemplate = async () => {
    if (!selectedTemplate) return

    console.log('INFO [RecurringTemplatesPage]: Deleting template:', selectedTemplate.id)
    try {
      await deleteTemplate(selectedTemplate.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [RecurringTemplatesPage]: Failed to delete template:', err)
      setOperationError('Failed to delete template. Please try again.')
    }
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
            Recurring Transactions
          </Typography>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Entity Selected
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {entities.length === 0
                ? 'Create your first entity to start managing recurring transactions.'
                : 'Select an entity to view and manage its recurring transactions.'}
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
            Recurring Transactions
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenAddDialog}
          >
            Add Recurring Template
          </Button>
        </Box>

        {/* Current Entity Info */}
        <Paper elevation={1} sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
          <Typography variant="body2" color="text.secondary">
            Managing recurring transactions for: <strong>{currentEntity.name}</strong>
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
          <FormControlLabel
            control={
              <Switch
                checked={includeInactive}
                onChange={(e) => setIncludeInactive(e.target.checked)}
              />
            }
            label="Show inactive templates"
          />
        </Paper>

        {/* Template count */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Showing {templates.length} of {total} recurring templates
        </Typography>

        {/* Templates table */}
        <TRRecurringTemplateTable
          templates={templates}
          categories={categoryMap}
          onEdit={handleOpenEditDialog}
          onDeactivate={handleOpenDeactivateDialog}
          onDelete={handleOpenDeleteDialog}
          isLoading={isLoading}
          canDelete={canDelete}
        />

        {/* Add Template Dialog */}
        <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Add Recurring Template</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              <TRRecurringTemplateForm
                onSubmit={handleCreateTemplate}
                categories={categories}
                entityId={currentEntity.id}
                onCancel={handleCloseAddDialog}
              />
            </Box>
          </DialogContent>
        </Dialog>

        {/* Edit Template Dialog */}
        <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Edit Recurring Template</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              {selectedTemplate && (
                <TRRecurringTemplateForm
                  onSubmit={handleUpdateTemplate}
                  initialData={selectedTemplate}
                  categories={categories}
                  entityId={currentEntity.id}
                  onCancel={handleCloseEditDialog}
                />
              )}
            </Box>
          </DialogContent>
        </Dialog>

        {/* Deactivate Confirmation Dialog */}
        <Dialog open={isDeactivateDialogOpen} onClose={handleCloseDeactivateDialog}>
          <DialogTitle>Deactivate Recurring Template</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Typography>
              Are you sure you want to deactivate this recurring template?
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              The template will remain in your records but will be marked as inactive.
            </Typography>
            {selectedTemplate && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2">
                  <strong>Name:</strong> {selectedTemplate.name}
                </Typography>
                <Typography variant="body2">
                  <strong>Type:</strong> {selectedTemplate.type}
                </Typography>
                <Typography variant="body2">
                  <strong>Amount:</strong> ${selectedTemplate.amount}
                </Typography>
                <Typography variant="body2">
                  <strong>Frequency:</strong> {selectedTemplate.frequency}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeactivateDialog}>Cancel</Button>
            <Button onClick={handleDeactivateTemplate} color="warning" variant="contained">
              Deactivate
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
          <DialogTitle>Delete Recurring Template</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Typography color="error">
              Are you sure you want to permanently delete this recurring template?
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              This action cannot be undone. Consider deactivating instead to preserve history.
            </Typography>
            {selectedTemplate && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2">
                  <strong>Name:</strong> {selectedTemplate.name}
                </Typography>
                <Typography variant="body2">
                  <strong>Type:</strong> {selectedTemplate.type}
                </Typography>
                <Typography variant="body2">
                  <strong>Amount:</strong> ${selectedTemplate.amount}
                </Typography>
                <Typography variant="body2">
                  <strong>Frequency:</strong> {selectedTemplate.frequency}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
            <Button onClick={handleDeleteTemplate} color="error" variant="contained">
              Delete Permanently
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  )
}

export default RecurringTemplatesPage

import React, { useState } from 'react'
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import BusinessIcon from '@mui/icons-material/Business'
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom'
import { useForm, Controller } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useEntity } from '@/hooks/useEntity'
import { useAuth } from '@/hooks/useAuth'
import type { CreateEntityData, UpdateEntityData, Entity } from '@/types'

interface EntityFormData {
  name: string
  type: 'family' | 'startup'
  description: string
}

/**
 * Entities page for managing user entities.
 * Allows creating, editing, deleting, and viewing entities.
 */
export const EntitiesPage: React.FC = () => {
  const { entities, currentEntity, isLoading, createEntity, updateEntity, deleteEntity, switchEntity } = useEntity()
  const { logout } = useAuth()
  const navigate = useNavigate()

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EntityFormData>({
    defaultValues: {
      name: '',
      type: 'family',
      description: '',
    },
  })

  const handleLogout = () => {
    console.log('INFO [EntitiesPage]: User initiated logout')
    logout()
    navigate('/login')
  }

  const handleOpenCreateDialog = () => {
    reset({ name: '', type: 'family', description: '' })
    setError(null)
    setIsCreateDialogOpen(true)
  }

  const handleOpenEditDialog = (entity: Entity) => {
    setSelectedEntity(entity)
    reset({
      name: entity.name,
      type: entity.type,
      description: entity.description || '',
    })
    setError(null)
    setIsEditDialogOpen(true)
  }

  const handleOpenDeleteDialog = (entity: Entity) => {
    setSelectedEntity(entity)
    setError(null)
    setIsDeleteDialogOpen(true)
  }

  const handleCreateSubmit = async (data: EntityFormData) => {
    console.log('INFO [EntitiesPage]: Creating entity:', data.name)
    setIsSubmitting(true)
    setError(null)
    try {
      const entityData: CreateEntityData = {
        name: data.name,
        type: data.type,
        description: data.description || undefined,
      }
      await createEntity(entityData)
      setIsCreateDialogOpen(false)
      reset()
      console.log('INFO [EntitiesPage]: Entity created successfully')
    } catch (err) {
      console.error('ERROR [EntitiesPage]: Failed to create entity:', err)
      setError('Failed to create entity. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEditSubmit = async (data: EntityFormData) => {
    if (!selectedEntity) return
    console.log('INFO [EntitiesPage]: Updating entity:', selectedEntity.id)
    setIsSubmitting(true)
    setError(null)
    try {
      const updateData: UpdateEntityData = {
        name: data.name,
        description: data.description || undefined,
      }
      await updateEntity(selectedEntity.id, updateData)
      setIsEditDialogOpen(false)
      setSelectedEntity(null)
      reset()
      console.log('INFO [EntitiesPage]: Entity updated successfully')
    } catch (err) {
      console.error('ERROR [EntitiesPage]: Failed to update entity:', err)
      setError('Failed to update entity. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!selectedEntity) return
    console.log('INFO [EntitiesPage]: Deleting entity:', selectedEntity.id)
    setIsSubmitting(true)
    setError(null)
    try {
      await deleteEntity(selectedEntity.id)
      setIsDeleteDialogOpen(false)
      setSelectedEntity(null)
      console.log('INFO [EntitiesPage]: Entity deleted successfully')
    } catch (err) {
      console.error('ERROR [EntitiesPage]: Failed to delete entity:', err)
      setError('Failed to delete entity. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSelectEntity = (entity: Entity) => {
    switchEntity(entity.id)
    navigate('/dashboard')
  }

  const getEntityIcon = (type: 'family' | 'startup') => {
    return type === 'family' ? (
      <FamilyRestroomIcon fontSize="large" color="primary" />
    ) : (
      <BusinessIcon fontSize="large" color="secondary" />
    )
  }

  if (isLoading) {
    return (
      <Container maxWidth="md">
        <Box
          sx={{
            py: 4,
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4, minHeight: '100vh' }}>
        {/* Header */}
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Grid container justifyContent="space-between" alignItems="center">
            <Grid>
              <Typography variant="h4" component="h1" gutterBottom>
                Entity Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage your financial tracking entities
              </Typography>
            </Grid>
            <Grid>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button variant="outlined" onClick={() => navigate('/dashboard')}>
                  Dashboard
                </Button>
                <Button variant="outlined" color="secondary" onClick={handleLogout}>
                  Logout
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Create Button */}
        <Box sx={{ mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreateDialog}
          >
            Create Entity
          </Button>
        </Box>

        {/* Entity List */}
        {entities.length === 0 ? (
          <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No entities yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Create your first entity to start tracking finances.
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {entities.map((entity) => (
              <Grid item key={entity.id} xs={12} sm={6} md={4}>
                <Card
                  elevation={currentEntity?.id === entity.id ? 6 : 2}
                  sx={{
                    border: currentEntity?.id === entity.id ? '2px solid' : 'none',
                    borderColor: 'primary.main',
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      {getEntityIcon(entity.type)}
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" component="h2">
                          {entity.name}
                        </Typography>
                        <Chip
                          label={entity.type}
                          size="small"
                          color={entity.type === 'family' ? 'primary' : 'secondary'}
                        />
                      </Box>
                    </Box>
                    {entity.description && (
                      <Typography variant="body2" color="text.secondary">
                        {entity.description}
                      </Typography>
                    )}
                    {currentEntity?.id === entity.id && (
                      <Chip
                        label="Current"
                        size="small"
                        color="success"
                        sx={{ mt: 1 }}
                      />
                    )}
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'space-between' }}>
                    <Button
                      size="small"
                      variant={currentEntity?.id === entity.id ? 'contained' : 'outlined'}
                      onClick={() => handleSelectEntity(entity)}
                    >
                      {currentEntity?.id === entity.id ? 'Selected' : 'Select'}
                    </Button>
                    <Box>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenEditDialog(entity)}
                        aria-label="Edit entity"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleOpenDeleteDialog(entity)}
                        aria-label="Delete entity"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Create Dialog */}
        <Dialog open={isCreateDialogOpen} onClose={() => setIsCreateDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handleSubmit(handleCreateSubmit)}>
            <DialogTitle>Create New Entity</DialogTitle>
            <DialogContent>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Name is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    autoFocus
                    margin="dense"
                    label="Entity Name"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                  />
                )}
              />
              <Controller
                name="type"
                control={control}
                rules={{ required: 'Type is required' }}
                render={({ field }) => (
                  <FormControl fullWidth margin="dense">
                    <InputLabel>Type</InputLabel>
                    <Select {...field} label="Type">
                      <MenuItem value="family">Family</MenuItem>
                      <MenuItem value="startup">Startup</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    margin="dense"
                    label="Description"
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsCreateDialogOpen(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" disabled={isSubmitting}>
                {isSubmitting ? <CircularProgress size={24} /> : 'Create'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Edit Dialog */}
        <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handleSubmit(handleEditSubmit)}>
            <DialogTitle>Edit Entity</DialogTitle>
            <DialogContent>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Name is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    autoFocus
                    margin="dense"
                    label="Entity Name"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                  />
                )}
              />
              <Controller
                name="type"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth margin="dense" disabled>
                    <InputLabel>Type</InputLabel>
                    <Select {...field} label="Type">
                      <MenuItem value="family">Family</MenuItem>
                      <MenuItem value="startup">Startup</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    margin="dense"
                    label="Description"
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsEditDialogOpen(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" disabled={isSubmitting}>
                {isSubmitting ? <CircularProgress size={24} /> : 'Save'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
          <DialogTitle>Delete Entity</DialogTitle>
          <DialogContent>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            <Typography>
              Are you sure you want to delete &quot;{selectedEntity?.name}&quot;? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDeleteDialogOpen(false)} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              color="error"
              variant="contained"
              disabled={isSubmitting}
            >
              {isSubmitting ? <CircularProgress size={24} /> : 'Delete'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  )
}

export default EntitiesPage

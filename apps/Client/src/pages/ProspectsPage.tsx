import { useState } from 'react'
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
  CircularProgress,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import { useEntity } from '@/hooks/useEntity'
import { useProspects } from '@/hooks/useProspects'
import { usePipelineStages } from '@/hooks/usePipelineStages'
import { TRKanbanBoard } from '@/components/ui/TRKanbanBoard'
import { TRProspectForm } from '@/components/forms/TRProspectForm'
import type { Prospect, ProspectCreate, ProspectUpdate } from '@/types'

export const ProspectsPage: React.FC = () => {
  const { currentEntity, entities, isLoading: entityLoading } = useEntity()
  const entityId = currentEntity?.id || null

  const { stages, isLoading: stagesLoading, error: stagesError } = usePipelineStages(entityId)
  const {
    prospects,
    isLoading: prospectsLoading,
    error: prospectsError,
    createProspect,
    updateProspect,
  } = useProspects(entityId)

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedProspect, setSelectedProspect] = useState<Prospect | null>(null)
  const [operationError, setOperationError] = useState<string | null>(null)

  const handleOpenAddDialog = () => {
    console.log('INFO [ProspectsPage]: Opening add prospect dialog')
    setOperationError(null)
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [ProspectsPage]: Closing add prospect dialog')
    setIsAddDialogOpen(false)
  }

  const handleProspectClick = (prospect: Prospect) => {
    console.log('INFO [ProspectsPage]: Opening edit dialog for prospect:', prospect.id)
    setOperationError(null)
    setSelectedProspect(prospect)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [ProspectsPage]: Closing edit prospect dialog')
    setIsEditDialogOpen(false)
    setSelectedProspect(null)
  }

  const handleCreateProspect = async (data: ProspectCreate | ProspectUpdate) => {
    console.log('INFO [ProspectsPage]: Creating prospect')
    try {
      await createProspect(data as ProspectCreate)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [ProspectsPage]: Failed to create prospect:', err)
      setOperationError('Failed to create prospect. Please try again.')
    }
  }

  const handleUpdateProspect = async (data: ProspectCreate | ProspectUpdate) => {
    if (!selectedProspect) return

    console.log('INFO [ProspectsPage]: Updating prospect:', selectedProspect.id)
    try {
      await updateProspect(selectedProspect.id, data as ProspectUpdate)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [ProspectsPage]: Failed to update prospect:', err)
      setOperationError('Failed to update prospect. Please try again.')
    }
  }

  if (entityLoading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (!currentEntity) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Prospects
          </Typography>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Entity Selected
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {entities.length === 0
                ? 'Create your first entity to start managing prospects.'
                : 'Select an entity to view and manage its prospects.'}
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

  const error = stagesError || prospectsError

  return (
    <Container maxWidth="xl">
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
            Prospects
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenAddDialog}
          >
            Add Prospect
          </Button>
        </Box>

        {/* Current Entity Info */}
        <Paper elevation={1} sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
          <Typography variant="body2" color="text.secondary">
            Managing prospects for: <strong>{currentEntity.name}</strong>
          </Typography>
        </Paper>

        {/* Error display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Kanban Board */}
        <TRKanbanBoard
          stages={stages}
          prospects={prospects}
          isLoading={stagesLoading || prospectsLoading}
          onProspectClick={handleProspectClick}
          onProspectEdit={handleProspectClick}
        />

        {/* Add Prospect Dialog */}
        <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Add Prospect</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              <TRProspectForm
                onSubmit={handleCreateProspect}
                entityId={currentEntity.id}
                stages={stages}
                onCancel={handleCloseAddDialog}
              />
            </Box>
          </DialogContent>
        </Dialog>

        {/* Edit Prospect Dialog */}
        <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
          <DialogTitle>Edit Prospect</DialogTitle>
          <DialogContent>
            {operationError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operationError}
              </Alert>
            )}
            <Box sx={{ pt: 1 }}>
              {selectedProspect && (
                <TRProspectForm
                  onSubmit={handleUpdateProspect}
                  initialData={selectedProspect}
                  entityId={currentEntity.id}
                  stages={stages}
                  onCancel={handleCloseEditDialog}
                />
              )}
            </Box>
          </DialogContent>
        </Dialog>
      </Box>
    </Container>
  )
}

export default ProspectsPage

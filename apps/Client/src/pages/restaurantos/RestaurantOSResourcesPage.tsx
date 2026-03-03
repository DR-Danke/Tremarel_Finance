import React, { useState, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  CircularProgress,
  Chip,
  Drawer,
} from '@mui/material'
import { Add, Edit, Delete, Visibility } from '@mui/icons-material'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useResources } from '@/hooks/useResources'
import { useInventoryMovements } from '@/hooks/useInventoryMovements'
import { usePersons } from '@/hooks/usePersons'
import { TRResourceForm } from '@/components/forms/TRResourceForm'
import { TRInventoryMovementForm } from '@/components/forms/TRInventoryMovementForm'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Resource, ResourceCreate, ResourceUpdate, InventoryMovementCreate } from '@/types/resource'
import {
  RESOURCE_TYPE_LABELS,
  MOVEMENT_TYPE_LABELS,
  MOVEMENT_REASON_LABELS,
} from '@/types/resource'

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('es-CO', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return '—'
  }
}

export const RestaurantOSResourcesPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading } = useRestaurant()
  const {
    resources,
    isLoading: resourcesLoading,
    error,
    setFilters,
    fetchResources,
    createResource,
    updateResource,
    deleteResource,
  } = useResources(currentRestaurant?.id ?? null)
  const {
    movements,
    isLoading: movementsLoading,
    error: movementsError,
    fetchMovementsByResource,
    createMovement,
    clearMovements,
  } = useInventoryMovements()
  const { persons } = usePersons(currentRestaurant?.id ?? null)

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isMovementDialogOpen, setIsMovementDialogOpen] = useState(false)
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null)
  const [drawerResource, setDrawerResource] = useState<Resource | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const filteredResources = useMemo(() => {
    if (!searchQuery) return resources
    return resources.filter((r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [resources, searchQuery])

  const personsMap = useMemo(() => {
    const map: Record<string, string> = {}
    for (const person of persons) {
      map[person.id] = person.name
    }
    return map
  }, [persons])

  // Loading state
  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <CircularProgress size={24} />
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  // No restaurants
  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  // --- Dialog handlers ---

  const handleOpenAddDialog = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Opening add resource dialog')
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Closing add resource dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (resource: Resource) => {
    console.log('INFO [RestaurantOSResourcesPage]: Opening edit dialog for resource:', resource.id)
    setSelectedResource(resource)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Closing edit resource dialog')
    setIsEditDialogOpen(false)
    setSelectedResource(null)
  }

  const handleOpenDeleteDialog = (resource: Resource) => {
    console.log('INFO [RestaurantOSResourcesPage]: Opening delete dialog for resource:', resource.id)
    setSelectedResource(resource)
    setIsDeleteDialogOpen(true)
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedResource(null)
  }

  const handleOpenMovementDialog = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Opening movement dialog')
    setIsMovementDialogOpen(true)
  }

  const handleCloseMovementDialog = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Closing movement dialog')
    setIsMovementDialogOpen(false)
  }

  // --- Detail drawer handlers ---

  const handleOpenDrawer = (resource: Resource) => {
    console.log('INFO [RestaurantOSResourcesPage]: Opening detail drawer for resource:', resource.id)
    setDrawerResource(resource)
    fetchMovementsByResource(resource.id)
  }

  const handleCloseDrawer = () => {
    console.log('INFO [RestaurantOSResourcesPage]: Closing detail drawer')
    setDrawerResource(null)
    clearMovements()
  }

  // --- CRUD handlers ---

  const handleCreateResource = async (data: ResourceCreate | ResourceUpdate) => {
    console.log('INFO [RestaurantOSResourcesPage]: Creating resource')
    setIsSubmitting(true)
    try {
      await createResource(data as ResourceCreate)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to create resource:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdateResource = async (data: ResourceCreate | ResourceUpdate) => {
    if (!selectedResource) return
    console.log('INFO [RestaurantOSResourcesPage]: Updating resource:', selectedResource.id)
    setIsSubmitting(true)
    try {
      await updateResource(selectedResource.id, data as ResourceUpdate)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to update resource:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteResource = async () => {
    if (!selectedResource) return
    console.log('INFO [RestaurantOSResourcesPage]: Deleting resource:', selectedResource.id)
    setIsSubmitting(true)
    try {
      await deleteResource(selectedResource.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to delete resource:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCreateMovement = async (data: InventoryMovementCreate) => {
    console.log('INFO [RestaurantOSResourcesPage]: Creating movement')
    setIsSubmitting(true)
    try {
      await createMovement(data)
      handleCloseMovementDialog()
      // Refresh resources since stock changed
      await fetchResources()
      // Refresh drawer movements if open for same resource
      if (drawerResource && data.resource_id === drawerResource.id) {
        await fetchMovementsByResource(drawerResource.id)
      }
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to create movement:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTypeFilterChange = (value: string) => {
    setTypeFilter(value)
    setFilters({ type: value ? (value as ResourceCreate['type']) : undefined })
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Recursos / Inventario
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {currentRestaurant?.name}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenAddDialog}
          >
            Agregar Recurso
          </Button>
          <Button
            variant="outlined"
            onClick={handleOpenMovementDialog}
          >
            Registrar Movimiento
          </Button>
        </Box>
      </Box>

      {/* Error display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters row */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          label="Buscar por nombre"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{ minWidth: 250 }}
        />
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="resource-type-filter-label">Filtrar por tipo</InputLabel>
          <Select
            labelId="resource-type-filter-label"
            value={typeFilter}
            onChange={(e) => handleTypeFilterChange(e.target.value)}
            label="Filtrar por tipo"
          >
            <MenuItem value="">Todos</MenuItem>
            <MenuItem value="producto">Producto</MenuItem>
            <MenuItem value="activo">Activo</MenuItem>
            <MenuItem value="servicio">Servicio</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Data table */}
      {resourcesLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredResources.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No se encontraron recursos
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Unidad</TableCell>
                <TableCell>Stock Actual</TableCell>
                <TableCell>Stock Mínimo</TableCell>
                <TableCell>Último Costo</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredResources.map((resource) => (
                <TableRow
                  key={resource.id}
                  hover
                  sx={{ cursor: 'pointer' }}
                  onClick={() => handleOpenDrawer(resource)}
                >
                  <TableCell>{resource.name}</TableCell>
                  <TableCell>{RESOURCE_TYPE_LABELS[resource.type] || resource.type}</TableCell>
                  <TableCell>{resource.unit}</TableCell>
                  <TableCell>{resource.current_stock}</TableCell>
                  <TableCell>{resource.minimum_stock}</TableCell>
                  <TableCell>{formatCurrency(resource.last_unit_cost)}</TableCell>
                  <TableCell>
                    {resource.is_low_stock ? (
                      <Chip label="Stock Bajo" color="error" size="small" />
                    ) : (
                      <Chip label="OK" color="success" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenDrawer(resource)
                      }}
                      aria-label="view"
                    >
                      <Visibility fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenEditDialog(resource)
                      }}
                      aria-label="edit"
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenDeleteDialog(resource)
                      }}
                      aria-label="delete"
                      color="error"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add Resource Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Recurso</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRResourceForm
              onSubmit={handleCreateResource}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={handleCloseAddDialog}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Resource Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Recurso</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedResource && (
              <TRResourceForm
                onSubmit={handleUpdateResource}
                initialData={selectedResource}
                restaurantId={currentRestaurant?.id || ''}
                onCancel={handleCloseEditDialog}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Register Movement Dialog */}
      <Dialog open={isMovementDialogOpen} onClose={handleCloseMovementDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Registrar Movimiento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRInventoryMovementForm
              onSubmit={handleCreateMovement}
              resources={resources}
              persons={persons}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={handleCloseMovementDialog}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Eliminar Recurso</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro que desea eliminar este recurso?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            onClick={handleDeleteResource}
            color="error"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detail Drawer */}
      <Drawer
        anchor="right"
        open={!!drawerResource}
        onClose={handleCloseDrawer}
        PaperProps={{ sx: { width: { xs: '100%', sm: 500 } } }}
      >
        {drawerResource && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              {drawerResource.name}
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary">
                Tipo: {RESOURCE_TYPE_LABELS[drawerResource.type] || drawerResource.type}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Unidad: {drawerResource.unit}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Stock Actual: {drawerResource.current_stock}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Stock Mínimo: {drawerResource.minimum_stock}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Último Costo: {formatCurrency(drawerResource.last_unit_cost)}
              </Typography>
              <Box sx={{ mt: 1 }}>
                {drawerResource.is_low_stock ? (
                  <Chip label="Stock Bajo" color="error" size="small" />
                ) : (
                  <Chip label="OK" color="success" size="small" />
                )}
              </Box>
            </Box>

            <Typography variant="h6" gutterBottom>
              Historial de Movimientos
            </Typography>

            {movementsError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {movementsError}
              </Alert>
            )}

            {movementsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : movements.length === 0 ? (
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography color="text.secondary">
                  No hay movimientos registrados
                </Typography>
              </Paper>
            ) : (
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Fecha</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Cantidad</TableCell>
                      <TableCell>Razón</TableCell>
                      <TableCell>Persona</TableCell>
                      <TableCell>Notas</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {movements.map((movement) => (
                      <TableRow key={movement.id}>
                        <TableCell>{formatDate(movement.date)}</TableCell>
                        <TableCell>
                          {MOVEMENT_TYPE_LABELS[movement.type] || movement.type}
                        </TableCell>
                        <TableCell>{movement.quantity}</TableCell>
                        <TableCell>
                          {MOVEMENT_REASON_LABELS[movement.reason] || movement.reason}
                        </TableCell>
                        <TableCell>
                          {movement.person_id ? personsMap[movement.person_id] || '—' : '—'}
                        </TableCell>
                        <TableCell>{movement.notes || '—'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </Drawer>
    </Box>
  )
}

export default RestaurantOSResourcesPage

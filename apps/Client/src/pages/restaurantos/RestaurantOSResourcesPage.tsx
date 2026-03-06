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
  LinearProgress,
  TableSortLabel,
  TablePagination,
} from '@mui/material'
import { Add, Edit, Delete, Visibility } from '@mui/icons-material'
import InventoryIcon from '@mui/icons-material/Inventory'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useResources } from '@/hooks/useResources'
import { useInventoryMovements } from '@/hooks/useInventoryMovements'
import { usePersons } from '@/hooks/usePersons'
import { useSnackbar } from '@/hooks/useSnackbar'
import { useTableSort } from '@/hooks/useTableSort'
import { useTablePagination } from '@/hooks/useTablePagination'
import { TRResourceForm } from '@/components/forms/TRResourceForm'
import { TRInventoryMovementForm } from '@/components/forms/TRInventoryMovementForm'
import { TRBreadcrumbs } from '@/components/ui/TRBreadcrumbs'
import { TRTableSkeleton } from '@/components/ui/TRTableSkeleton'
import { TREmptyState } from '@/components/ui/TREmptyState'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Resource, ResourceCreate, ResourceUpdate, InventoryMovementCreate } from '@/types/resource'
import {
  RESOURCE_TYPE_LABELS,
  MOVEMENT_TYPE_LABELS,
  MOVEMENT_REASON_LABELS,
} from '@/types/resource'

const formatCurrency = (value: number): string =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return '—'
  try {
    return new Date(dateStr).toLocaleDateString('es-CO', {
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

const getStockRatio = (current: number, minimum: number): number => {
  if (minimum <= 0) return 100
  return Math.min((current / minimum) * 100, 200)
}

const getStockColor = (ratio: number): 'error' | 'warning' | 'success' => {
  if (ratio < 100) return 'error'
  if (ratio < 150) return 'warning'
  return 'success'
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
  const { showSnackbar } = useSnackbar()

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isMovementDialogOpen, setIsMovementDialogOpen] = useState(false)
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null)
  const [drawerResource, setDrawerResource] = useState<Resource | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [moveDateFrom, setMoveDateFrom] = useState('')
  const [moveDateTo, setMoveDateTo] = useState('')

  const filteredResources = useMemo(() => {
    if (!searchQuery) return resources
    return resources.filter((r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [resources, searchQuery])

  const { sorted, orderBy, order, onSort } = useTableSort<Resource>(filteredResources)
  const { paginated, page, rowsPerPage, totalCount, onPageChange, onRowsPerPageChange } = useTablePagination(sorted)

  const personsMap = useMemo(() => {
    const map: Record<string, string> = {}
    for (const person of persons) {
      map[person.id] = person.name
    }
    return map
  }, [persons])

  // Summary stats
  const lowStockCount = resources.filter((r) => r.is_low_stock).length
  const totalInventoryValue = resources.reduce((sum, r) => sum + r.current_stock * r.last_unit_cost, 0)

  // Filtered movements for drawer
  const filteredMovements = useMemo(() => {
    let filtered = movements
    if (moveDateFrom) {
      filtered = filtered.filter((m) => m.date && m.date >= moveDateFrom)
    }
    if (moveDateTo) {
      filtered = filtered.filter((m) => m.date && m.date <= moveDateTo + 'T23:59:59')
    }
    return filtered
  }, [movements, moveDateFrom, moveDateTo])

  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <CircularProgress size={24} />
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  const handleOpenDrawer = (resource: Resource) => {
    console.log('INFO [RestaurantOSResourcesPage]: Opening detail drawer for resource:', resource.id)
    setDrawerResource(resource)
    setMoveDateFrom('')
    setMoveDateTo('')
    fetchMovementsByResource(resource.id)
  }

  const handleCloseDrawer = () => {
    setDrawerResource(null)
    clearMovements()
  }

  const handleCreateResource = async (data: ResourceCreate | ResourceUpdate) => {
    console.log('INFO [RestaurantOSResourcesPage]: Creating resource')
    setIsSubmitting(true)
    try {
      await createResource(data as ResourceCreate)
      setIsAddDialogOpen(false)
      showSnackbar('Recurso creado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to create resource:', err)
      showSnackbar('Error al crear recurso', 'error')
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
      setIsEditDialogOpen(false)
      setSelectedResource(null)
      showSnackbar('Recurso actualizado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to update resource:', err)
      showSnackbar('Error al actualizar recurso', 'error')
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
      setIsDeleteDialogOpen(false)
      setSelectedResource(null)
      showSnackbar('Recurso eliminado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to delete resource:', err)
      showSnackbar('Error al eliminar recurso', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCreateMovement = async (data: InventoryMovementCreate) => {
    console.log('INFO [RestaurantOSResourcesPage]: Creating movement')
    setIsSubmitting(true)
    try {
      await createMovement(data)
      setIsMovementDialogOpen(false)
      await fetchResources()
      if (drawerResource && data.resource_id === drawerResource.id) {
        await fetchMovementsByResource(drawerResource.id)
      }
      showSnackbar('Movimiento registrado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSResourcesPage]: Failed to create movement:', err)
      showSnackbar('Error al registrar movimiento', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTypeFilterChange = (value: string) => {
    setTypeFilter(value)
    setFilters({ type: value ? (value as ResourceCreate['type']) : undefined })
  }

  const sortableHeader = (label: string, column: keyof Resource) => (
    <TableSortLabel
      active={orderBy === column}
      direction={orderBy === column ? order : 'asc'}
      onClick={() => onSort(column)}
    >
      {label}
    </TableSortLabel>
  )

  return (
    <Box sx={{ p: 3 }}>
      <TRBreadcrumbs
        module="RestaurantOS"
        moduleHref="/poc/restaurant-os"
        restaurantName={currentRestaurant?.name}
        currentPage="Recursos / Inventario"
      />

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Recursos / Inventario
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="contained" startIcon={<Add />} onClick={() => setIsAddDialogOpen(true)}>
            Agregar Recurso
          </Button>
          <Button variant="outlined" onClick={() => setIsMovementDialogOpen(true)}>
            Registrar Movimiento
          </Button>
        </Box>
      </Box>

      {/* Summary Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Chip label={`${resources.length} total`} variant="outlined" />
        <Chip
          label={`${lowStockCount} stock bajo`}
          color={lowStockCount > 0 ? 'error' : 'success'}
          variant="outlined"
        />
        <Chip label={`Valor inventario: ${formatCurrency(totalInventoryValue)}`} variant="outlined" />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
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

      {/* Table */}
      {resourcesLoading ? (
        <TRTableSkeleton columns={8} />
      ) : filteredResources.length === 0 ? (
        <TREmptyState
          icon={<InventoryIcon sx={{ fontSize: 64 }} />}
          title="No se encontraron recursos"
          description="Agrega productos, activos y servicios para tu inventario"
          actionLabel="Agregar Recurso"
          onAction={() => setIsAddDialogOpen(true)}
        />
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{sortableHeader('Nombre', 'name')}</TableCell>
                  <TableCell>{sortableHeader('Tipo', 'type')}</TableCell>
                  <TableCell>Unidad</TableCell>
                  <TableCell>{sortableHeader('Stock Actual', 'current_stock')}</TableCell>
                  <TableCell>Stock Minimo</TableCell>
                  <TableCell>{sortableHeader('Ultimo Costo', 'last_unit_cost')}</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginated.map((resource) => (
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
                        onClick={(e) => { e.stopPropagation(); handleOpenDrawer(resource) }}
                        aria-label="view"
                      >
                        <Visibility fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => { e.stopPropagation(); setSelectedResource(resource); setIsEditDialogOpen(true) }}
                        aria-label="edit"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => { e.stopPropagation(); setSelectedResource(resource); setIsDeleteDialogOpen(true) }}
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
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={(_, p) => onPageChange(p)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => onRowsPerPageChange(parseInt(e.target.value, 10))}
            rowsPerPageOptions={[10, 25, 50]}
            labelRowsPerPage="Filas por pagina"
          />
        </>
      )}

      {/* Add Resource Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Recurso</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRResourceForm
              onSubmit={handleCreateResource}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={() => setIsAddDialogOpen(false)}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Resource Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => { setIsEditDialogOpen(false); setSelectedResource(null) }} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Recurso</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedResource && (
              <TRResourceForm
                onSubmit={handleUpdateResource}
                initialData={selectedResource}
                restaurantId={currentRestaurant?.id || ''}
                onCancel={() => { setIsEditDialogOpen(false); setSelectedResource(null) }}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Movement Dialog */}
      <Dialog open={isMovementDialogOpen} onClose={() => setIsMovementDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Registrar Movimiento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRInventoryMovementForm
              onSubmit={handleCreateMovement}
              resources={resources}
              persons={persons}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={() => setIsMovementDialogOpen(false)}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => { setIsDeleteDialogOpen(false); setSelectedResource(null) }}>
        <DialogTitle>Eliminar Recurso</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Esta seguro que desea eliminar este recurso?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setIsDeleteDialogOpen(false); setSelectedResource(null) }} disabled={isSubmitting}>
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
                Stock Minimo: {drawerResource.minimum_stock}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ultimo Costo: {formatCurrency(drawerResource.last_unit_cost)}
              </Typography>

              {/* Stock Level Visualization */}
              <Box sx={{ mt: 2, mb: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Nivel de Stock
                </Typography>
                {(() => {
                  const ratio = getStockRatio(drawerResource.current_stock, drawerResource.minimum_stock)
                  const color = getStockColor(ratio)
                  return (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(ratio, 100)}
                        color={color}
                        sx={{ flex: 1, height: 10, borderRadius: 5 }}
                      />
                      <Typography variant="caption" fontWeight={600}>
                        {Math.round(ratio)}%
                      </Typography>
                    </Box>
                  )
                })()}
              </Box>

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

            {/* Movement Date Filters */}
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                label="Desde"
                type="date"
                size="small"
                value={moveDateFrom}
                onChange={(e) => setMoveDateFrom(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
              <TextField
                label="Hasta"
                type="date"
                size="small"
                value={moveDateTo}
                onChange={(e) => setMoveDateTo(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Box>

            {movementsError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {movementsError}
              </Alert>
            )}

            {movementsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : filteredMovements.length === 0 ? (
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
                      <TableCell>Razon</TableCell>
                      <TableCell>Persona</TableCell>
                      <TableCell>Notas</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredMovements.map((movement) => (
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

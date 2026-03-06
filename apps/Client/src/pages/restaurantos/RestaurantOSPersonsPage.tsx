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
  TableSortLabel,
  TablePagination,
} from '@mui/material'
import { Add, Edit, Delete, Check } from '@mui/icons-material'
import PeopleIcon from '@mui/icons-material/People'
import { useRestaurant } from '@/hooks/useRestaurant'
import { usePersons } from '@/hooks/usePersons'
import { useSnackbar } from '@/hooks/useSnackbar'
import { useTableSort } from '@/hooks/useTableSort'
import { useTablePagination } from '@/hooks/useTablePagination'
import { TRPersonForm } from '@/components/forms/TRPersonForm'
import { TRBreadcrumbs } from '@/components/ui/TRBreadcrumbs'
import { TRTableSkeleton } from '@/components/ui/TRTableSkeleton'
import { TREmptyState } from '@/components/ui/TREmptyState'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Person, PersonCreate, PersonUpdate } from '@/types/person'

const PERSON_TYPE_LABELS: Record<string, string> = {
  employee: 'Empleado',
  supplier: 'Proveedor',
  owner: 'Dueno',
}

export const RestaurantOSPersonsPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading } = useRestaurant()
  const {
    persons,
    isLoading: personsLoading,
    error,
    setFilters,
    createPerson,
    updatePerson,
    deletePerson,
  } = usePersons(currentRestaurant?.id ?? null)
  const { showSnackbar } = useSnackbar()

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const filteredPersons = useMemo(() => {
    if (!searchQuery) return persons
    return persons.filter((p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [persons, searchQuery])

  const { sorted, orderBy, order, onSort } = useTableSort<Person>(filteredPersons)
  const { paginated, page, rowsPerPage, totalCount, onPageChange, onRowsPerPageChange } = useTablePagination(sorted)

  // Summary stats
  const employeeCount = persons.filter((p) => p.type === 'employee').length
  const supplierCount = persons.filter((p) => p.type === 'supplier').length

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

  const handleCreatePerson = async (data: PersonCreate | PersonUpdate) => {
    console.log('INFO [RestaurantOSPersonsPage]: Creating person')
    setIsSubmitting(true)
    try {
      await createPerson(data as PersonCreate)
      setIsAddDialogOpen(false)
      showSnackbar('Persona creada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSPersonsPage]: Failed to create person:', err)
      showSnackbar('Error al crear persona', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdatePerson = async (data: PersonCreate | PersonUpdate) => {
    if (!selectedPerson) return
    console.log('INFO [RestaurantOSPersonsPage]: Updating person:', selectedPerson.id)
    setIsSubmitting(true)
    try {
      await updatePerson(selectedPerson.id, data as PersonUpdate)
      setIsEditDialogOpen(false)
      setSelectedPerson(null)
      showSnackbar('Persona actualizada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSPersonsPage]: Failed to update person:', err)
      showSnackbar('Error al actualizar persona', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeletePerson = async () => {
    if (!selectedPerson) return
    console.log('INFO [RestaurantOSPersonsPage]: Deleting person:', selectedPerson.id)
    setIsSubmitting(true)
    try {
      await deletePerson(selectedPerson.id)
      setIsDeleteDialogOpen(false)
      setSelectedPerson(null)
      showSnackbar('Persona eliminada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSPersonsPage]: Failed to delete person:', err)
      showSnackbar('Error al eliminar persona', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTypeFilterChange = (value: string) => {
    setTypeFilter(value)
    setFilters({ type: value ? (value as PersonCreate['type']) : undefined })
  }

  const sortableHeader = (label: string, column: keyof Person) => (
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
        currentPage="Personas"
      />

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Personas
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setIsAddDialogOpen(true)}
        >
          Agregar Persona
        </Button>
      </Box>

      {/* Summary Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Chip label={`${persons.length} total`} variant="outlined" />
        <Chip label={`${employeeCount} empleados`} color="primary" variant="outlined" />
        <Chip label={`${supplierCount} proveedores`} color="secondary" variant="outlined" />
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
          <InputLabel id="type-filter-label">Filtrar por tipo</InputLabel>
          <Select
            labelId="type-filter-label"
            value={typeFilter}
            onChange={(e) => handleTypeFilterChange(e.target.value)}
            label="Filtrar por tipo"
          >
            <MenuItem value="">Todos</MenuItem>
            <MenuItem value="employee">Empleado</MenuItem>
            <MenuItem value="supplier">Proveedor</MenuItem>
            <MenuItem value="owner">Dueno</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Table */}
      {personsLoading ? (
        <TRTableSkeleton columns={7} />
      ) : filteredPersons.length === 0 ? (
        <TREmptyState
          icon={<PeopleIcon sx={{ fontSize: 64 }} />}
          title="No se encontraron personas"
          description="Agrega empleados y proveedores para tu restaurante"
          actionLabel="Agregar Persona"
          onAction={() => setIsAddDialogOpen(true)}
        />
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{sortableHeader('Nombre', 'name')}</TableCell>
                  <TableCell>{sortableHeader('Rol', 'role')}</TableCell>
                  <TableCell>{sortableHeader('Tipo', 'type')}</TableCell>
                  <TableCell>Correo Electronico</TableCell>
                  <TableCell>WhatsApp</TableCell>
                  <TableCell>Push</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginated.map((person) => (
                  <TableRow key={person.id}>
                    <TableCell>{person.name}</TableCell>
                    <TableCell>{person.role}</TableCell>
                    <TableCell>{PERSON_TYPE_LABELS[person.type] || person.type}</TableCell>
                    <TableCell>{person.email || '—'}</TableCell>
                    <TableCell>{person.whatsapp || '—'}</TableCell>
                    <TableCell>{person.push_token ? <Check fontSize="small" color="success" /> : '—'}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedPerson(person)
                          setIsEditDialogOpen(true)
                        }}
                        aria-label="edit"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedPerson(person)
                          setIsDeleteDialogOpen(true)
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

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Persona</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRPersonForm
              onSubmit={handleCreatePerson}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={() => setIsAddDialogOpen(false)}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => { setIsEditDialogOpen(false); setSelectedPerson(null) }} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Persona</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedPerson && (
              <TRPersonForm
                onSubmit={handleUpdatePerson}
                initialData={selectedPerson}
                restaurantId={currentRestaurant?.id || ''}
                onCancel={() => { setIsEditDialogOpen(false); setSelectedPerson(null) }}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => { setIsDeleteDialogOpen(false); setSelectedPerson(null) }}>
        <DialogTitle>Eliminar Persona</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Esta seguro que desea eliminar esta persona?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setIsDeleteDialogOpen(false); setSelectedPerson(null) }} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            onClick={handleDeletePerson}
            color="error"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default RestaurantOSPersonsPage

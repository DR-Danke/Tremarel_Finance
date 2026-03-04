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
} from '@mui/material'
import { Add, Edit, Delete, Check } from '@mui/icons-material'
import { useRestaurant } from '@/hooks/useRestaurant'
import { usePersons } from '@/hooks/usePersons'
import { TRPersonForm } from '@/components/forms/TRPersonForm'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Person, PersonCreate, PersonUpdate } from '@/types/person'

const PERSON_TYPE_LABELS: Record<string, string> = {
  employee: 'Empleado',
  supplier: 'Proveedor',
  owner: 'Dueño',
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

  const handleOpenAddDialog = () => {
    console.log('INFO [RestaurantOSPersonsPage]: Opening add person dialog')
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [RestaurantOSPersonsPage]: Closing add person dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (person: Person) => {
    console.log('INFO [RestaurantOSPersonsPage]: Opening edit dialog for person:', person.id)
    setSelectedPerson(person)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [RestaurantOSPersonsPage]: Closing edit person dialog')
    setIsEditDialogOpen(false)
    setSelectedPerson(null)
  }

  const handleOpenDeleteDialog = (person: Person) => {
    console.log('INFO [RestaurantOSPersonsPage]: Opening delete dialog for person:', person.id)
    setSelectedPerson(person)
    setIsDeleteDialogOpen(true)
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [RestaurantOSPersonsPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedPerson(null)
  }

  const handleCreatePerson = async (data: PersonCreate | PersonUpdate) => {
    console.log('INFO [RestaurantOSPersonsPage]: Creating person')
    setIsSubmitting(true)
    try {
      await createPerson(data as PersonCreate)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSPersonsPage]: Failed to create person:', err)
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
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSPersonsPage]: Failed to update person:', err)
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
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSPersonsPage]: Failed to delete person:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTypeFilterChange = (value: string) => {
    setTypeFilter(value)
    setFilters({ type: value ? (value as PersonCreate['type']) : undefined })
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Personas
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {currentRestaurant?.name}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenAddDialog}
        >
          Agregar Persona
        </Button>
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
            <MenuItem value="owner">Dueño</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Data table */}
      {personsLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredPersons.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No se encontraron personas
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Rol</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Correo Electrónico</TableCell>
                <TableCell>WhatsApp</TableCell>
                <TableCell>Push</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredPersons.map((person) => (
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
                      onClick={() => handleOpenEditDialog(person)}
                      aria-label="edit"
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDeleteDialog(person)}
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

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Persona</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRPersonForm
              onSubmit={handleCreatePerson}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={handleCloseAddDialog}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Persona</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedPerson && (
              <TRPersonForm
                onSubmit={handleUpdatePerson}
                initialData={selectedPerson}
                restaurantId={currentRestaurant?.id || ''}
                onCancel={handleCloseEditDialog}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Eliminar Persona</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro que desea eliminar esta persona?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
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

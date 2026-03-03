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
import { Add, Edit, Delete, CheckCircle } from '@mui/icons-material'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useEvents } from '@/hooks/useEvents'
import { usePersons } from '@/hooks/usePersons'
import { TREventForm } from '@/components/forms/TREventForm'
import { TREventStatusBadge } from '@/components/ui/TREventStatusBadge'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Event, EventCreate, EventUpdate, EventType, EventStatus } from '@/types/event'
import { EVENT_TYPE_OPTIONS, EVENT_STATUS_OPTIONS } from '@/types/event'

const EVENT_TYPE_LABELS: Record<string, string> = {
  tarea: 'Tarea',
  vencimiento: 'Vencimiento',
  pago: 'Pago',
  turno: 'Turno',
  checklist: 'Checklist',
  alerta_stock: 'Alerta Stock',
  alerta_rentabilidad: 'Alerta Rentabilidad',
}

interface DateGroup {
  date: string
  events: Event[]
}

export const RestaurantOSEventsPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading } = useRestaurant()
  const {
    events,
    isLoading: eventsLoading,
    error,
    setFilters,
    createEvent,
    updateEvent,
    updateEventStatus,
    deleteEvent,
  } = useEvents(currentRestaurant?.id ?? null)
  const { persons } = usePersons(currentRestaurant?.id ?? null)

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [responsibleFilter, setResponsibleFilter] = useState('')
  const [dateFromFilter, setDateFromFilter] = useState('')
  const [dateToFilter, setDateToFilter] = useState('')

  const groupedEvents = useMemo<DateGroup[]>(() => {
    const groups: Record<string, Event[]> = {}
    for (const event of events) {
      const dateKey = event.date.slice(0, 10)
      if (!groups[dateKey]) {
        groups[dateKey] = []
      }
      groups[dateKey].push(event)
    }
    return Object.keys(groups)
      .sort()
      .map((date) => ({ date, events: groups[date] }))
  }, [events])

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

  const handleOpenAddDialog = () => {
    console.log('INFO [RestaurantOSEventsPage]: Opening add event dialog')
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [RestaurantOSEventsPage]: Closing add event dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (event: Event) => {
    console.log('INFO [RestaurantOSEventsPage]: Opening edit dialog for event:', event.id)
    setSelectedEvent(event)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [RestaurantOSEventsPage]: Closing edit event dialog')
    setIsEditDialogOpen(false)
    setSelectedEvent(null)
  }

  const handleOpenDeleteDialog = (event: Event) => {
    console.log('INFO [RestaurantOSEventsPage]: Opening delete dialog for event:', event.id)
    setSelectedEvent(event)
    setIsDeleteDialogOpen(true)
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [RestaurantOSEventsPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedEvent(null)
  }

  const handleCreateEvent = async (data: EventCreate | EventUpdate) => {
    console.log('INFO [RestaurantOSEventsPage]: Creating event')
    setIsSubmitting(true)
    try {
      await createEvent(data as EventCreate)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to create event:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdateEvent = async (data: EventCreate | EventUpdate) => {
    if (!selectedEvent) return
    console.log('INFO [RestaurantOSEventsPage]: Updating event:', selectedEvent.id)
    setIsSubmitting(true)
    try {
      await updateEvent(selectedEvent.id, data as EventUpdate)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to update event:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteEvent = async () => {
    if (!selectedEvent) return
    console.log('INFO [RestaurantOSEventsPage]: Deleting event:', selectedEvent.id)
    setIsSubmitting(true)
    try {
      await deleteEvent(selectedEvent.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to delete event:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleQuickComplete = async (eventId: string) => {
    console.log('INFO [RestaurantOSEventsPage]: Quick-completing event:', eventId)
    try {
      await updateEventStatus(eventId, 'completed')
      console.log('INFO [RestaurantOSEventsPage]: Event quick-completed:', eventId)
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to quick-complete event:', err)
    }
  }

  const handleTypeFilterChange = (value: string) => {
    setTypeFilter(value)
    setFilters({
      type: value ? (value as EventType) : undefined,
      status: statusFilter ? (statusFilter as EventStatus) : undefined,
      responsible_id: responsibleFilter || undefined,
      date_from: dateFromFilter || undefined,
      date_to: dateToFilter || undefined,
    })
  }

  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value)
    setFilters({
      type: typeFilter ? (typeFilter as EventType) : undefined,
      status: value ? (value as EventStatus) : undefined,
      responsible_id: responsibleFilter || undefined,
      date_from: dateFromFilter || undefined,
      date_to: dateToFilter || undefined,
    })
  }

  const handleResponsibleFilterChange = (value: string) => {
    setResponsibleFilter(value)
    setFilters({
      type: typeFilter ? (typeFilter as EventType) : undefined,
      status: statusFilter ? (statusFilter as EventStatus) : undefined,
      responsible_id: value || undefined,
      date_from: dateFromFilter || undefined,
      date_to: dateToFilter || undefined,
    })
  }

  const handleDateFromFilterChange = (value: string) => {
    setDateFromFilter(value)
    setFilters({
      type: typeFilter ? (typeFilter as EventType) : undefined,
      status: statusFilter ? (statusFilter as EventStatus) : undefined,
      responsible_id: responsibleFilter || undefined,
      date_from: value || undefined,
      date_to: dateToFilter || undefined,
    })
  }

  const handleDateToFilterChange = (value: string) => {
    setDateToFilter(value)
    setFilters({
      type: typeFilter ? (typeFilter as EventType) : undefined,
      status: statusFilter ? (statusFilter as EventStatus) : undefined,
      responsible_id: responsibleFilter || undefined,
      date_from: dateFromFilter || undefined,
      date_to: value || undefined,
    })
  }

  const formatTime = (dateStr: string): string => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
    } catch {
      return '—'
    }
  }

  const formatDateHeader = (dateStr: string): string => {
    try {
      const d = new Date(dateStr + 'T12:00:00')
      return d.toLocaleDateString('es-CO', {
        weekday: 'long',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      })
    } catch {
      return dateStr
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Eventos / Tareas
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
          Agregar Evento
        </Button>
      </Box>

      {/* Error display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters row */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="type-filter-label">Filtrar por tipo</InputLabel>
          <Select
            labelId="type-filter-label"
            value={typeFilter}
            onChange={(e) => handleTypeFilterChange(e.target.value)}
            label="Filtrar por tipo"
          >
            <MenuItem value="">Todos</MenuItem>
            {EVENT_TYPE_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="status-filter-label">Filtrar por estado</InputLabel>
          <Select
            labelId="status-filter-label"
            value={statusFilter}
            onChange={(e) => handleStatusFilterChange(e.target.value)}
            label="Filtrar por estado"
          >
            <MenuItem value="">Todos</MenuItem>
            {EVENT_STATUS_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="responsible-filter-label">Filtrar por responsable</InputLabel>
          <Select
            labelId="responsible-filter-label"
            value={responsibleFilter}
            onChange={(e) => handleResponsibleFilterChange(e.target.value)}
            label="Filtrar por responsable"
          >
            <MenuItem value="">Todos</MenuItem>
            {persons.map((person) => (
              <MenuItem key={person.id} value={person.id}>
                {person.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          label="Desde"
          type="date"
          size="small"
          value={dateFromFilter}
          onChange={(e) => handleDateFromFilterChange(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 160 }}
        />

        <TextField
          label="Hasta"
          type="date"
          size="small"
          value={dateToFilter}
          onChange={(e) => handleDateToFilterChange(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 160 }}
        />
      </Box>

      {/* Data table */}
      {eventsLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : events.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No se encontraron eventos
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Fecha</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Descripción</TableCell>
                <TableCell>Responsable</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {groupedEvents.map((group) => (
                <React.Fragment key={group.date}>
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      sx={{
                        bgcolor: 'grey.100',
                        fontWeight: 'bold',
                        textTransform: 'capitalize',
                      }}
                    >
                      {formatDateHeader(group.date)}
                    </TableCell>
                  </TableRow>
                  {group.events.map((event) => (
                    <TableRow
                      key={event.id}
                      sx={{
                        bgcolor: event.is_overdue || event.status === 'overdue'
                          ? 'rgba(211, 47, 47, 0.08)'
                          : 'inherit',
                      }}
                    >
                      <TableCell>{formatTime(event.date)}</TableCell>
                      <TableCell>{EVENT_TYPE_LABELS[event.type] || event.type}</TableCell>
                      <TableCell>{event.description || '—'}</TableCell>
                      <TableCell>
                        {event.responsible_id ? personsMap[event.responsible_id] || '—' : '—'}
                      </TableCell>
                      <TableCell>
                        <TREventStatusBadge status={event.status} />
                      </TableCell>
                      <TableCell>
                        {event.status === 'pending' && (
                          <IconButton
                            size="small"
                            onClick={() => handleQuickComplete(event.id)}
                            aria-label="complete"
                            color="success"
                          >
                            <CheckCircle fontSize="small" />
                          </IconButton>
                        )}
                        <IconButton
                          size="small"
                          onClick={() => handleOpenEditDialog(event)}
                          aria-label="edit"
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDeleteDialog(event)}
                          aria-label="delete"
                          color="error"
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Evento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TREventForm
              onSubmit={handleCreateEvent}
              restaurantId={currentRestaurant?.id || ''}
              persons={persons}
              onCancel={handleCloseAddDialog}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Evento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedEvent && (
              <TREventForm
                onSubmit={handleUpdateEvent}
                initialData={selectedEvent}
                restaurantId={currentRestaurant?.id || ''}
                persons={persons}
                onCancel={handleCloseEditDialog}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Eliminar Evento</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro que desea eliminar este evento?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            onClick={handleDeleteEvent}
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

export default RestaurantOSEventsPage

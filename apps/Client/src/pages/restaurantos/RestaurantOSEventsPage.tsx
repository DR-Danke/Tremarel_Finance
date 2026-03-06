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
  ToggleButton,
  ToggleButtonGroup,
  TablePagination,
} from '@mui/material'
import { Add, Edit, Delete, CheckCircle, ViewList, CalendarMonth } from '@mui/icons-material'
import AssignmentLateIcon from '@mui/icons-material/AssignmentLate'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useEvents } from '@/hooks/useEvents'
import { usePersons } from '@/hooks/usePersons'
import { useSnackbar } from '@/hooks/useSnackbar'
import { useTablePagination } from '@/hooks/useTablePagination'
import { TREventForm } from '@/components/forms/TREventForm'
import { TREventStatusBadge } from '@/components/ui/TREventStatusBadge'
import { TRBreadcrumbs } from '@/components/ui/TRBreadcrumbs'
import { TRTableSkeleton } from '@/components/ui/TRTableSkeleton'
import { TREmptyState } from '@/components/ui/TREmptyState'
import { TRWeeklyCalendar } from '@/components/ui/TRWeeklyCalendar'
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
  const { showSnackbar } = useSnackbar()

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
  const [viewMode, setViewMode] = useState<'list' | 'week'>('list')

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

  // Overdue events
  const overdueEvents = useMemo(
    () => events.filter((e) => e.is_overdue || e.status === 'overdue'),
    [events]
  )

  // Flat list for pagination in list view
  const flatEvents = useMemo(() => {
    return groupedEvents.flatMap((g) => g.events)
  }, [groupedEvents])

  const { paginated, page, rowsPerPage, totalCount, onPageChange, onRowsPerPageChange } = useTablePagination(flatEvents, 25)

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

  const applyFilters = (overrides: Partial<{
    type: string; status: string; responsible_id: string; date_from: string; date_to: string
  }>) => {
    const t = overrides.type ?? typeFilter
    const s = overrides.status ?? statusFilter
    const r = overrides.responsible_id ?? responsibleFilter
    const df = overrides.date_from ?? dateFromFilter
    const dt = overrides.date_to ?? dateToFilter
    setFilters({
      type: t ? (t as EventType) : undefined,
      status: s ? (s as EventStatus) : undefined,
      responsible_id: r || undefined,
      date_from: df || undefined,
      date_to: dt || undefined,
    })
  }

  const handleCreateEvent = async (data: EventCreate | EventUpdate) => {
    console.log('INFO [RestaurantOSEventsPage]: Creating event')
    setIsSubmitting(true)
    try {
      await createEvent(data as EventCreate)
      setIsAddDialogOpen(false)
      showSnackbar('Evento creado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to create event:', err)
      showSnackbar('Error al crear evento', 'error')
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
      setIsEditDialogOpen(false)
      setSelectedEvent(null)
      showSnackbar('Evento actualizado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to update event:', err)
      showSnackbar('Error al actualizar evento', 'error')
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
      setIsDeleteDialogOpen(false)
      setSelectedEvent(null)
      showSnackbar('Evento eliminado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to delete event:', err)
      showSnackbar('Error al eliminar evento', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleQuickComplete = async (eventId: string) => {
    console.log('INFO [RestaurantOSEventsPage]: Quick-completing event:', eventId)
    try {
      await updateEventStatus(eventId, 'completed')
      showSnackbar('Tarea completada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSEventsPage]: Failed to quick-complete event:', err)
      showSnackbar('Error al completar tarea', 'error')
    }
  }

  const formatTime = (dateStr: string): string => {
    try {
      return new Date(dateStr).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
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

  // Group paginated events by date for display
  const paginatedGroups = useMemo<DateGroup[]>(() => {
    const groups: Record<string, Event[]> = {}
    for (const event of paginated) {
      const dateKey = event.date.slice(0, 10)
      if (!groups[dateKey]) groups[dateKey] = []
      groups[dateKey].push(event)
    }
    return Object.keys(groups).sort().map((date) => ({ date, events: groups[date] }))
  }, [paginated])

  return (
    <Box sx={{ p: 3 }}>
      <TRBreadcrumbs
        module="RestaurantOS"
        moduleHref="/poc/restaurant-os"
        restaurantName={currentRestaurant?.name}
        currentPage="Eventos / Tareas"
      />

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Eventos / Tareas
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, v) => v && setViewMode(v)}
            size="small"
          >
            <ToggleButton value="list"><ViewList fontSize="small" /></ToggleButton>
            <ToggleButton value="week"><CalendarMonth fontSize="small" /></ToggleButton>
          </ToggleButtonGroup>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsAddDialogOpen(true)}
          >
            Agregar Evento
          </Button>
        </Box>
      </Box>

      {/* Overdue Summary */}
      {overdueEvents.length > 0 && (
        <Alert
          severity="error"
          icon={<AssignmentLateIcon />}
          sx={{ mb: 2 }}
          action={
            <Typography variant="body2" fontWeight={600} sx={{ pr: 1 }}>
              {overdueEvents.length} vencida{overdueEvents.length !== 1 ? 's' : ''}
            </Typography>
          }
        >
          <Box>
            {overdueEvents.slice(0, 5).map((e) => (
              <Box key={e.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="body2">
                  {e.description || e.type} — {personsMap[e.responsible_id || ''] || 'Sin asignar'}
                </Typography>
                <IconButton size="small" color="success" onClick={() => handleQuickComplete(e.id)}>
                  <CheckCircle sx={{ fontSize: 16 }} />
                </IconButton>
              </Box>
            ))}
            {overdueEvents.length > 5 && (
              <Typography variant="caption" color="text.secondary">
                y {overdueEvents.length - 5} mas...
              </Typography>
            )}
          </Box>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="type-filter-label">Filtrar por tipo</InputLabel>
          <Select
            labelId="type-filter-label"
            value={typeFilter}
            onChange={(e) => { setTypeFilter(e.target.value); applyFilters({ type: e.target.value }) }}
            label="Filtrar por tipo"
          >
            <MenuItem value="">Todos</MenuItem>
            {EVENT_TYPE_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="status-filter-label">Filtrar por estado</InputLabel>
          <Select
            labelId="status-filter-label"
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); applyFilters({ status: e.target.value }) }}
            label="Filtrar por estado"
          >
            <MenuItem value="">Todos</MenuItem>
            {EVENT_STATUS_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="responsible-filter-label">Filtrar por responsable</InputLabel>
          <Select
            labelId="responsible-filter-label"
            value={responsibleFilter}
            onChange={(e) => { setResponsibleFilter(e.target.value); applyFilters({ responsible_id: e.target.value }) }}
            label="Filtrar por responsable"
          >
            <MenuItem value="">Todos</MenuItem>
            {persons.map((person) => (
              <MenuItem key={person.id} value={person.id}>{person.name}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          label="Desde"
          type="date"
          size="small"
          value={dateFromFilter}
          onChange={(e) => { setDateFromFilter(e.target.value); applyFilters({ date_from: e.target.value }) }}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 160 }}
        />

        <TextField
          label="Hasta"
          type="date"
          size="small"
          value={dateToFilter}
          onChange={(e) => { setDateToFilter(e.target.value); applyFilters({ date_to: e.target.value }) }}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 160 }}
        />
      </Box>

      {/* Content */}
      {eventsLoading ? (
        <TRTableSkeleton columns={6} />
      ) : events.length === 0 ? (
        <TREmptyState
          title="No se encontraron eventos"
          description="Crea tareas, turnos y alertas para tu equipo"
          actionLabel="Agregar Evento"
          onAction={() => setIsAddDialogOpen(true)}
        />
      ) : viewMode === 'week' ? (
        <TRWeeklyCalendar
          events={events}
          personsMap={personsMap}
          onQuickComplete={handleQuickComplete}
        />
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Descripcion</TableCell>
                  <TableCell>Responsable</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedGroups.map((group) => (
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
                            onClick={() => {
                              setSelectedEvent(event)
                              setIsEditDialogOpen(true)
                            }}
                            aria-label="edit"
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedEvent(event)
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
                  </React.Fragment>
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
        <DialogTitle>Agregar Evento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TREventForm
              onSubmit={handleCreateEvent}
              restaurantId={currentRestaurant?.id || ''}
              persons={persons}
              onCancel={() => setIsAddDialogOpen(false)}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => { setIsEditDialogOpen(false); setSelectedEvent(null) }} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Evento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedEvent && (
              <TREventForm
                onSubmit={handleUpdateEvent}
                initialData={selectedEvent}
                restaurantId={currentRestaurant?.id || ''}
                persons={persons}
                onCancel={() => { setIsEditDialogOpen(false); setSelectedEvent(null) }}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => { setIsDeleteDialogOpen(false); setSelectedEvent(null) }}>
        <DialogTitle>Eliminar Evento</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Esta seguro que desea eliminar este evento?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setIsDeleteDialogOpen(false); setSelectedEvent(null) }} disabled={isSubmitting}>
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

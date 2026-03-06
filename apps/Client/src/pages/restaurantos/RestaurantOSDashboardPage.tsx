import React, { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import InventoryIcon from '@mui/icons-material/Inventory'
import DescriptionIcon from '@mui/icons-material/Description'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import AssignmentIcon from '@mui/icons-material/Assignment'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import AddTaskIcon from '@mui/icons-material/AddTask'
import SwapHorizIcon from '@mui/icons-material/SwapHoriz'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useDashboardOverview } from '@/hooks/useDashboardOverview'
import { usePersons } from '@/hooks/usePersons'
import { useResources } from '@/hooks/useResources'
import { useEvents } from '@/hooks/useEvents'
import { useSnackbar } from '@/hooks/useSnackbar'
import { TRStatCard } from '@/components/ui/TRStatCard'
import { TRStatCardSkeleton } from '@/components/ui/TRStatCardSkeleton'
import { TRAlertsList } from '@/components/ui/TRAlertsList'
import { TREventStatusBadge } from '@/components/ui/TREventStatusBadge'
import { TRBreadcrumbs } from '@/components/ui/TRBreadcrumbs'
import { TREventForm } from '@/components/forms/TREventForm'
import { TRInventoryMovementForm } from '@/components/forms/TRInventoryMovementForm'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import { MOVEMENT_TYPE_LABELS, MOVEMENT_REASON_LABELS } from '@/types/resource'
import { inventoryMovementService } from '@/services/inventoryMovementService'
import type { Event, EventCreate, EventUpdate, EventStatus } from '@/types/event'
import type { MovementType, MovementReason, InventoryMovementCreate } from '@/types/resource'

interface TasksByResponsible {
  responsibleId: string | null
  tasks: Event[]
}

const getGreeting = (): string => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Buenos dias'
  if (hour < 18) return 'Buenas tardes'
  return 'Buenas noches'
}

const formatTodayDate = (): string => {
  return new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export const RestaurantOSDashboardPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading: isRestaurantLoading } = useRestaurant()
  const { overview, isLoading, error, refresh } = useDashboardOverview(currentRestaurant?.id)
  const { persons } = usePersons(currentRestaurant?.id ?? null)
  const { resources } = useResources(currentRestaurant?.id ?? null)
  const { updateEventStatus, createEvent } = useEvents(currentRestaurant?.id ?? null)
  const { showSnackbar } = useSnackbar()

  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false)
  const [isMovementDialogOpen, setIsMovementDialogOpen] = useState(false)

  const personsMap = useMemo(() => {
    const map: Record<string, string> = {}
    for (const person of persons) {
      map[person.id] = person.name
    }
    return map
  }, [persons])

  const resourcesMap = useMemo(() => {
    const map: Record<string, string> = {}
    for (const resource of resources) {
      map[resource.id] = resource.name
    }
    return map
  }, [resources])

  const tasksByResponsible = useMemo((): TasksByResponsible[] => {
    if (!overview?.today_tasks) return []

    const grouped = new Map<string | null, Event[]>()
    for (const task of overview.today_tasks) {
      const key = task.responsible_id
      const existing = grouped.get(key) || []
      existing.push(task)
      grouped.set(key, existing)
    }

    return Array.from(grouped.entries()).map(([responsibleId, tasks]) => ({
      responsibleId,
      tasks,
    }))
  }, [overview?.today_tasks])

  const overdueCount = useMemo(() => {
    if (!overview?.today_tasks) return 0
    return overview.today_tasks.filter((t) => t.is_overdue || t.status === 'overdue').length
  }, [overview?.today_tasks])

  const pendingCount = useMemo(() => {
    if (!overview?.today_tasks) return 0
    return overview.today_tasks.filter((t) => t.status === 'pending').length
  }, [overview?.today_tasks])

  const lowStockCount = overview?.low_stock_items?.length ?? 0
  const expiringCount = overview?.upcoming_expirations?.length ?? 0

  const briefingSummary = useMemo(() => {
    const parts: string[] = []
    if (pendingCount > 0) parts.push(`${pendingCount} tarea${pendingCount !== 1 ? 's' : ''} pendiente${pendingCount !== 1 ? 's' : ''}`)
    if (lowStockCount > 0) parts.push(`${lowStockCount} recurso${lowStockCount !== 1 ? 's' : ''} en stock bajo`)
    if (expiringCount > 0) parts.push(`${expiringCount} documento${expiringCount !== 1 ? 's' : ''} por vencer`)
    return parts.length > 0 ? parts.join(', ') : 'Todo en orden'
  }, [pendingCount, lowStockCount, expiringCount])

  const handleQuickComplete = async (eventId: string) => {
    console.log('INFO [DashboardPage]: Quick-completing task:', eventId)
    try {
      await updateEventStatus(eventId, 'completed')
      showSnackbar('Tarea completada', 'success')
      refresh()
    } catch (err) {
      console.error('ERROR [DashboardPage]: Failed to quick-complete task:', err)
      showSnackbar('Error al completar tarea', 'error')
    }
  }

  const handleCreateTask = async (data: EventCreate | EventUpdate) => {
    console.log('INFO [DashboardPage]: Creating task from dashboard')
    try {
      await createEvent(data as EventCreate)
      setIsTaskDialogOpen(false)
      showSnackbar('Tarea creada', 'success')
      refresh()
    } catch (err) {
      console.error('ERROR [DashboardPage]: Failed to create task:', err)
      showSnackbar('Error al crear tarea', 'error')
    }
  }

  if (isRestaurantLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={300} height={40} />
        <Skeleton variant="text" width={200} height={24} sx={{ mb: 3 }} />
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Grid item xs={12} sm={6} md={2.4} key={i}>
              <TRStatCardSkeleton />
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <TRBreadcrumbs
          module="RestaurantOS"
          moduleHref="/poc/restaurant-os"
          restaurantName={currentRestaurant?.name}
          currentPage="Dashboard"
        />
        <Skeleton variant="text" width={400} height={40} sx={{ mb: 1 }} />
        <Skeleton variant="text" width={500} height={24} sx={{ mb: 3 }} />
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Grid item xs={12} sm={6} md={2.4} key={i}>
              <TRStatCardSkeleton />
            </Grid>
          ))}
        </Grid>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Skeleton variant="rounded" height={300} />
          </Grid>
          <Grid item xs={12} md={6}>
            <Skeleton variant="rounded" height={300} />
          </Grid>
        </Grid>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={refresh}>
              Reintentar
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    )
  }

  const stats = overview?.stats

  return (
    <Box sx={{ p: 3 }}>
      {/* Breadcrumbs */}
      <TRBreadcrumbs
        module="RestaurantOS"
        moduleHref="/poc/restaurant-os"
        restaurantName={currentRestaurant?.name}
        currentPage="Dashboard"
      />

      {/* Morning Briefing Header */}
      <Typography variant="h4" gutterBottom>
        {getGreeting()}
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom sx={{ textTransform: 'capitalize' }}>
        {formatTodayDate()} &mdash; {briefingSummary}
      </Typography>

      {/* Quick Action Buttons */}
      <Box sx={{ display: 'flex', gap: 1, mb: 3, mt: 1 }}>
        <Button
          variant="outlined"
          size="small"
          startIcon={<AddTaskIcon />}
          onClick={() => setIsTaskDialogOpen(true)}
        >
          Nueva Tarea
        </Button>
        <Button
          variant="outlined"
          size="small"
          startIcon={<SwapHorizIcon />}
          onClick={() => setIsMovementDialogOpen(true)}
        >
          Registrar Movimiento
        </Button>
      </Box>

      {/* Stat Cards Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <TRStatCard
            title="Empleados"
            value={stats?.total_employees ?? 0}
            subtitle={`${stats?.total_employees ?? 0} activos hoy`}
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <TRStatCard
            title="Recursos"
            value={stats?.total_resources ?? 0}
            subtitle={lowStockCount > 0 ? `${lowStockCount} en stock bajo` : 'Stock OK'}
            icon={<InventoryIcon sx={{ fontSize: 40 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <TRStatCard
            title="Documentos Activos"
            value={stats?.active_documents ?? 0}
            subtitle={expiringCount > 0 ? `${expiringCount} por vencer` : 'Todos vigentes'}
            icon={<DescriptionIcon sx={{ fontSize: 40 }} />}
            color="#7b1fa2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <TRStatCard
            title="Completadas Hoy"
            value={stats?.tasks_completed_today ?? 0}
            subtitle={pendingCount > 0 ? `${pendingCount} pendientes` : 'Sin pendientes'}
            icon={<CheckCircleIcon sx={{ fontSize: 40 }} />}
            color="#00796b"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <TRStatCard
            title="Tareas Vencidas"
            value={overdueCount}
            subtitle={overdueCount > 0 ? 'Requieren atencion' : 'Sin vencidas'}
            icon={<WarningAmberIcon sx={{ fontSize: 40 }} />}
            color={overdueCount > 0 ? '#d32f2f' : '#757575'}
          />
        </Grid>
      </Grid>

      {/* Middle Row: Tasks + Alerts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Today's Tasks */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Tareas de Hoy
              </Typography>
              {tasksByResponsible.length === 0 ? (
                <Typography variant="body2" color="text.disabled">
                  No hay tareas para hoy
                </Typography>
              ) : (
                tasksByResponsible.map((group) => (
                  <Box key={group.responsibleId || 'unassigned'} sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 0.5 }}>
                      {group.responsibleId
                        ? personsMap[group.responsibleId] || 'Persona desconocida'
                        : 'Sin asignar'}
                    </Typography>
                    <List dense>
                      {group.tasks.map((task) => (
                        <ListItem key={task.id} disablePadding sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <AssignmentIcon fontSize="small" color="action" />
                          </ListItemIcon>
                          <ListItemText
                            primary={task.description || 'Tarea sin descripcion'}
                            secondary={new Date(task.date).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          />
                          {task.status === 'pending' && (
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleQuickComplete(task.id)}
                              aria-label="complete"
                              sx={{ mr: 0.5 }}
                            >
                              <CheckCircleIcon fontSize="small" />
                            </IconButton>
                          )}
                          <TREventStatusBadge status={task.status as EventStatus} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts Panel */}
        <Grid item xs={12} md={6}>
          <TRAlertsList
            expirations={overview?.upcoming_expirations ?? []}
            lowStockItems={overview?.low_stock_items ?? []}
            pendingAlerts={overview?.pending_alerts ?? []}
          />
        </Grid>
      </Grid>

      {/* Bottom Row: Recent Movements Table */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Movimientos Recientes de Inventario
          </Typography>
          {(overview?.recent_movements?.length ?? 0) === 0 ? (
            <Typography variant="body2" color="text.disabled">
              No hay movimientos recientes
            </Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Fecha</TableCell>
                    <TableCell>Recurso</TableCell>
                    <TableCell>Tipo</TableCell>
                    <TableCell>Cantidad</TableCell>
                    <TableCell>Razon</TableCell>
                    <TableCell>Notas</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {overview?.recent_movements.map((movement) => (
                    <TableRow key={movement.id}>
                      <TableCell>
                        {movement.date
                          ? new Date(movement.date).toLocaleDateString()
                          : '-'}
                      </TableCell>
                      <TableCell>
                        {resourcesMap[movement.resource_id] || movement.resource_id.substring(0, 8)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={MOVEMENT_TYPE_LABELS[movement.type as MovementType] || movement.type}
                          color={movement.type === 'entry' ? 'success' : 'error'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{movement.quantity}</TableCell>
                      <TableCell>
                        {MOVEMENT_REASON_LABELS[movement.reason as MovementReason] || movement.reason}
                      </TableCell>
                      <TableCell>{movement.notes || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* New Task Dialog */}
      <Dialog open={isTaskDialogOpen} onClose={() => setIsTaskDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Nueva Tarea</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TREventForm
              onSubmit={handleCreateTask}
              restaurantId={currentRestaurant?.id || ''}
              persons={persons}
              onCancel={() => setIsTaskDialogOpen(false)}
              isSubmitting={false}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Movement Dialog */}
      <Dialog open={isMovementDialogOpen} onClose={() => setIsMovementDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Registrar Movimiento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRInventoryMovementForm
              onSubmit={async (data: InventoryMovementCreate) => {
                await inventoryMovementService.create(data)
                setIsMovementDialogOpen(false)
                showSnackbar('Movimiento registrado', 'success')
                refresh()
              }}
              resources={resources}
              persons={persons}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={() => setIsMovementDialogOpen(false)}
              isSubmitting={false}
            />
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  )
}

export default RestaurantOSDashboardPage

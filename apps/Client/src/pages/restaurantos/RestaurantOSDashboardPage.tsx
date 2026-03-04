import React, { useMemo } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
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
import { useRestaurant } from '@/hooks/useRestaurant'
import { useDashboardOverview } from '@/hooks/useDashboardOverview'
import { TRStatCard } from '@/components/ui/TRStatCard'
import { TRAlertsList } from '@/components/ui/TRAlertsList'
import { TREventStatusBadge } from '@/components/ui/TREventStatusBadge'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import { MOVEMENT_TYPE_LABELS, MOVEMENT_REASON_LABELS } from '@/types/resource'
import type { Event, EventStatus } from '@/types/event'
import type { MovementType, MovementReason } from '@/types/resource'

interface TasksByResponsible {
  responsibleId: string | null
  tasks: Event[]
}

export const RestaurantOSDashboardPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading: isRestaurantLoading } = useRestaurant()
  const { overview, isLoading, error, refresh } = useDashboardOverview(currentRestaurant?.id)

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

  if (isRestaurantLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
        <CircularProgress />
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
      {/* Page Header */}
      <Typography variant="h4" gutterBottom>
        Dashboard Operativo
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {currentRestaurant?.name}
      </Typography>

      {/* Stat Cards Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <TRStatCard
            title="Empleados"
            value={stats?.total_employees ?? 0}
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TRStatCard
            title="Recursos"
            value={stats?.total_resources ?? 0}
            icon={<InventoryIcon sx={{ fontSize: 40 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TRStatCard
            title="Documentos Activos"
            value={stats?.active_documents ?? 0}
            icon={<DescriptionIcon sx={{ fontSize: 40 }} />}
            color="#7b1fa2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TRStatCard
            title="Tareas Completadas Hoy"
            value={stats?.tasks_completed_today ?? 0}
            icon={<CheckCircleIcon sx={{ fontSize: 40 }} />}
            color="#00796b"
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
                        ? `Responsable: ${group.responsibleId.substring(0, 8)}...`
                        : 'Sin asignar'}
                    </Typography>
                    <List dense>
                      {group.tasks.map((task) => (
                        <ListItem key={task.id} disablePadding sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            <AssignmentIcon fontSize="small" color="action" />
                          </ListItemIcon>
                          <ListItemText
                            primary={task.description || 'Tarea sin descripción'}
                            secondary={new Date(task.date).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          />
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
                    <TableCell>Tipo</TableCell>
                    <TableCell>Cantidad</TableCell>
                    <TableCell>Razón</TableCell>
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
    </Box>
  )
}

export default RestaurantOSDashboardPage

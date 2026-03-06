import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import InventoryIcon from '@mui/icons-material/Inventory'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import type { Document } from '@/types/document'
import type { Resource } from '@/types/resource'
import type { Event } from '@/types/event'
import { TRExpirationBadge } from '@/components/ui/TRExpirationBadge'

interface TRAlertsListProps {
  expirations: Document[]
  lowStockItems: Resource[]
  pendingAlerts: Event[]
}

const getDaysUntil = (dateStr: string | null): number | null => {
  if (!dateStr) return null
  const target = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return Math.ceil((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
}

const getUrgencyBgColor = (days: number | null): string => {
  if (days === null) return 'transparent'
  if (days < 3) return 'rgba(211, 47, 47, 0.08)'
  if (days < 7) return 'rgba(237, 108, 2, 0.08)'
  if (days <= 14) return 'rgba(255, 193, 7, 0.08)'
  return 'rgba(46, 125, 50, 0.06)'
}

export const TRAlertsList: React.FC<TRAlertsListProps> = ({
  expirations,
  lowStockItems,
  pendingAlerts,
}) => {
  const navigate = useNavigate()
  console.log('INFO [TRAlertsList]: Rendering alerts panel')

  const sortedExpirations = [...expirations].sort((a, b) => {
    const dA = getDaysUntil(a.expiration_date)
    const dB = getDaysUntil(b.expiration_date)
    if (dA === null) return 1
    if (dB === null) return -1
    return dA - dB
  })

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Alertas
        </Typography>

        {/* Document Expirations */}
        <Typography variant="subtitle2" sx={{ mt: 1, color: 'warning.main' }}>
          Vencimientos de Documentos
        </Typography>
        {sortedExpirations.length === 0 ? (
          <Typography variant="body2" color="text.disabled" sx={{ py: 1 }}>
            No hay documentos por vencer
          </Typography>
        ) : (
          <List dense>
            {sortedExpirations.map((doc) => {
              const daysUntil = getDaysUntil(doc.expiration_date)
              return (
                <ListItem key={doc.id} disablePadding sx={{ bgcolor: getUrgencyBgColor(daysUntil), borderRadius: 1, mb: 0.5 }}>
                  <ListItemButton
                    dense
                    onClick={() => navigate('/poc/restaurant-os/documents')}
                    sx={{ py: 0.5, borderRadius: 1 }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <DescriptionIcon color="warning" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={doc.description || doc.type}
                      secondary={
                        daysUntil !== null
                          ? daysUntil <= 0
                            ? 'Vencido'
                            : daysUntil === 0
                              ? 'Vence hoy'
                              : `Vence en ${daysUntil} dia${daysUntil !== 1 ? 's' : ''}`
                          : undefined
                      }
                    />
                    <TRExpirationBadge status={doc.expiration_status} />
                  </ListItemButton>
                </ListItem>
              )
            })}
          </List>
        )}

        <Divider sx={{ my: 1 }} />

        {/* Low Stock Items */}
        <Typography variant="subtitle2" sx={{ color: 'error.main' }}>
          Stock Bajo
        </Typography>
        {lowStockItems.length === 0 ? (
          <Typography variant="body2" color="text.disabled" sx={{ py: 1 }}>
            No hay alertas de stock
          </Typography>
        ) : (
          <List dense>
            {lowStockItems.map((resource) => (
              <ListItem key={resource.id} disablePadding>
                <ListItemButton
                  dense
                  onClick={() => navigate('/poc/restaurant-os/resources')}
                  sx={{ py: 0.5, borderRadius: 1 }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <InventoryIcon color="error" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={resource.name}
                    secondary={`${resource.current_stock} / ${resource.minimum_stock} ${resource.unit}`}
                  />
                  <Chip label="Bajo" color="error" size="small" />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}

        <Divider sx={{ my: 1 }} />

        {/* Pending Alerts */}
        <Typography variant="subtitle2" sx={{ color: 'warning.dark' }}>
          Alertas Pendientes
        </Typography>
        {pendingAlerts.length === 0 ? (
          <Typography variant="body2" color="text.disabled" sx={{ py: 1 }}>
            No hay alertas pendientes
          </Typography>
        ) : (
          <List dense>
            {pendingAlerts.map((alert) => (
              <ListItem key={alert.id} disablePadding>
                <ListItemButton
                  dense
                  onClick={() => navigate('/poc/restaurant-os/events')}
                  sx={{ py: 0.5, borderRadius: 1 }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <WarningAmberIcon color="warning" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.description || alert.type}
                    secondary={new Date(alert.date).toLocaleDateString()}
                  />
                  <Chip
                    label={
                      alert.type === 'alerta_stock'
                        ? 'Stock'
                        : alert.type === 'vencimiento'
                          ? 'Vencimiento'
                          : 'Rentabilidad'
                    }
                    color="warning"
                    size="small"
                    variant="outlined"
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  )
}

export default TRAlertsList

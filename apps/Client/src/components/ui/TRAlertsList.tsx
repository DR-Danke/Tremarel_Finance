import React from 'react'
import {
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
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

/**
 * TRAlertsList displays three alert sections: document expirations, low stock items, and pending alerts.
 */
export const TRAlertsList: React.FC<TRAlertsListProps> = ({
  expirations,
  lowStockItems,
  pendingAlerts,
}) => {
  console.log('INFO [TRAlertsList]: Rendering alerts panel')

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
        {expirations.length === 0 ? (
          <Typography variant="body2" color="text.disabled" sx={{ py: 1 }}>
            No hay documentos por vencer
          </Typography>
        ) : (
          <List dense>
            {expirations.map((doc) => {
              const daysUntil = getDaysUntil(doc.expiration_date)
              return (
                <ListItem key={doc.id} disablePadding sx={{ py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <DescriptionIcon color="warning" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={doc.description || doc.type}
                    secondary={
                      daysUntil !== null
                        ? daysUntil === 0
                          ? 'Vence hoy'
                          : `Vence en ${daysUntil} día${daysUntil !== 1 ? 's' : ''}`
                        : undefined
                    }
                  />
                  <TRExpirationBadge status={doc.expiration_status} />
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
              <ListItem key={resource.id} disablePadding sx={{ py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <InventoryIcon color="error" fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={resource.name}
                  secondary={`${resource.current_stock} / ${resource.minimum_stock} ${resource.unit}`}
                />
                <Chip label="Bajo" color="error" size="small" />
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
              <ListItem key={alert.id} disablePadding sx={{ py: 0.5 }}>
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
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  )
}

export default TRAlertsList

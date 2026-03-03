import { Chip } from '@mui/material'
import type { EventStatus } from '@/types/event'

interface TREventStatusBadgeProps {
  status: EventStatus
}

const STATUS_CONFIG: Record<EventStatus, { label: string; color: 'info' | 'success' | 'error' }> = {
  pending: { label: 'Pendiente', color: 'info' },
  completed: { label: 'Completado', color: 'success' },
  overdue: { label: 'Vencido', color: 'error' },
}

export const TREventStatusBadge: React.FC<TREventStatusBadgeProps> = ({ status }) => {
  console.log('INFO [TREventStatusBadge]: Rendering status:', status)

  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending

  return (
    <Chip
      label={config.label}
      color={config.color}
      size="small"
    />
  )
}

export default TREventStatusBadge

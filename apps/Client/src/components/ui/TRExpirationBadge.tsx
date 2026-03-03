import { Chip } from '@mui/material'
import type { ExpirationStatus } from '@/types/document'

interface TRExpirationBadgeProps {
  status: ExpirationStatus
}

const STATUS_CONFIG: Record<ExpirationStatus, { label: string; color: 'success' | 'warning' | 'error' }> = {
  valid: { label: 'Vigente', color: 'success' },
  expiring_soon: { label: 'Por Vencer', color: 'warning' },
  expired: { label: 'Vencido', color: 'error' },
}

export const TRExpirationBadge: React.FC<TRExpirationBadgeProps> = ({ status }) => {
  console.log('INFO [TRExpirationBadge]: Rendering status:', status)

  const config = STATUS_CONFIG[status] || STATUS_CONFIG.valid

  return (
    <Chip
      label={config.label}
      color={config.color}
      size="small"
    />
  )
}

export default TRExpirationBadge

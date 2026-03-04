import { Chip } from '@mui/material'
import type { CaseStatus } from '@/types/legaldesk'
import { CASE_STATUS_LABELS, CASE_STATUS_COLORS } from '@/types/legaldesk'

interface TRCaseStatusBadgeProps {
  status: CaseStatus
  size?: 'small' | 'medium'
}

export const TRCaseStatusBadge: React.FC<TRCaseStatusBadgeProps> = ({
  status,
  size = 'small',
}) => {
  console.log('INFO [TRCaseStatusBadge]: Rendering status:', status)

  const label = CASE_STATUS_LABELS[status] || status
  const backgroundColor = CASE_STATUS_COLORS[status] || '#9E9E9E'

  return (
    <Chip
      label={label}
      size={size}
      sx={{ backgroundColor, color: '#000', fontWeight: 500 }}
    />
  )
}

export default TRCaseStatusBadge

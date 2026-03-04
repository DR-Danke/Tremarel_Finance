import { Chip } from '@mui/material'
import type { CasePriority } from '@/types/legaldesk'
import { CASE_PRIORITY_LABELS, CASE_PRIORITY_COLORS } from '@/types/legaldesk'

interface TRCasePriorityBadgeProps {
  priority: CasePriority
}

export const TRCasePriorityBadge: React.FC<TRCasePriorityBadgeProps> = ({ priority }) => {
  console.log('INFO [TRCasePriorityBadge]: Rendering priority:', priority)

  const label = CASE_PRIORITY_LABELS[priority] || priority
  const backgroundColor = CASE_PRIORITY_COLORS[priority] || '#9E9E9E'

  return (
    <Chip
      label={label}
      size="small"
      sx={{ backgroundColor, color: '#fff', fontWeight: 500 }}
    />
  )
}

export default TRCasePriorityBadge

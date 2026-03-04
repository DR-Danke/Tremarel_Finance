import React from 'react'
import { Chip } from '@mui/material'
import type { CasePriority } from '@/types/legaldesk'
import { CASE_PRIORITY_LABELS, CASE_PRIORITY_COLORS } from '@/types/legaldesk'

interface TRCasePriorityBadgeProps {
  priority: CasePriority
  size?: 'small' | 'medium'
}

export const TRCasePriorityBadge: React.FC<TRCasePriorityBadgeProps> = ({ priority, size = 'small' }) => {
  return (
    <Chip
      label={CASE_PRIORITY_LABELS[priority]}
      size={size}
      sx={{
        backgroundColor: CASE_PRIORITY_COLORS[priority],
        color: '#fff',
        fontWeight: 500,
      }}
    />
  )
}

export default TRCasePriorityBadge

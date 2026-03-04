import React from 'react'
import { Chip } from '@mui/material'
import type { CaseStatus } from '@/types/legaldesk'
import { CASE_STATUS_LABELS, CASE_STATUS_COLORS } from '@/types/legaldesk'

interface TRCaseStatusBadgeProps {
  status: CaseStatus
  size?: 'small' | 'medium'
}

export const TRCaseStatusBadge: React.FC<TRCaseStatusBadgeProps> = ({ status, size = 'small' }) => {
  return (
    <Chip
      label={CASE_STATUS_LABELS[status]}
      size={size}
      sx={{
        backgroundColor: CASE_STATUS_COLORS[status],
        color: '#000',
        fontWeight: 500,
      }}
    />
  )
}

export default TRCaseStatusBadge

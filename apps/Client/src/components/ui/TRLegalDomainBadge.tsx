import React from 'react'
import { Chip } from '@mui/material'
import type { LegalDomain } from '@/types/legaldesk'
import { LEGAL_DOMAIN_LABELS, LEGAL_DOMAIN_COLORS } from '@/types/legaldesk'

interface TRLegalDomainBadgeProps {
  domain: LegalDomain
  size?: 'small' | 'medium'
}

export const TRLegalDomainBadge: React.FC<TRLegalDomainBadgeProps> = ({ domain, size = 'small' }) => {
  return (
    <Chip
      label={LEGAL_DOMAIN_LABELS[domain]}
      size={size}
      sx={{
        backgroundColor: LEGAL_DOMAIN_COLORS[domain],
        color: '#fff',
        fontWeight: 500,
      }}
    />
  )
}

export default TRLegalDomainBadge

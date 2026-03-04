import { Chip } from '@mui/material'
import type { LegalDomain } from '@/types/legaldesk'
import { LEGAL_DOMAIN_LABELS, LEGAL_DOMAIN_COLORS } from '@/types/legaldesk'

interface TRLegalDomainBadgeProps {
  domain: LegalDomain
  size?: 'small' | 'medium'
}

export const TRLegalDomainBadge: React.FC<TRLegalDomainBadgeProps> = ({ domain, size = 'small' }) => {
  console.log('INFO [TRLegalDomainBadge]: Rendering domain:', domain)

  const label = LEGAL_DOMAIN_LABELS[domain] || domain
  const backgroundColor = LEGAL_DOMAIN_COLORS[domain] || '#9E9E9E'

  return (
    <Chip
      label={label}
      size={size}
      sx={{ backgroundColor, color: '#fff', fontWeight: 500 }}
    />
  )
}

export default TRLegalDomainBadge

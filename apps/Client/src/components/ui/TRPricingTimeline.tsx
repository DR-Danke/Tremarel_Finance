import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
  Box,
} from '@mui/material'
import type { LdPricingHistory } from '@/types/legaldesk'
import { PRICING_ACTION_LABELS } from '@/types/legaldesk'

interface TRPricingTimelineProps {
  history: LdPricingHistory[]
}

const formatCurrency = (amount: number | null, currency: string): string => {
  if (amount === null) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(amount)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export const TRPricingTimeline: React.FC<TRPricingTimelineProps> = ({ history }) => {
  console.log('INFO [TRPricingTimeline]: Rendering timeline with', history.length, 'entries')

  if (history.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No pricing history
      </Typography>
    )
  }

  const sortedHistory = [...history].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  )

  return (
    <Stepper orientation="vertical" activeStep={sortedHistory.length - 1}>
      {sortedHistory.map((entry) => (
        <Step key={entry.id} completed>
          <StepLabel>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" fontWeight={600}>
                {PRICING_ACTION_LABELS[entry.action] || entry.action}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatDate(entry.created_at)}
              </Typography>
            </Box>
          </StepLabel>
          <StepContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Typography variant="body2">
                {entry.previous_amount !== null && (
                  <>
                    {formatCurrency(entry.previous_amount, entry.currency)}
                    {' → '}
                  </>
                )}
                {formatCurrency(entry.new_amount, entry.currency)}
              </Typography>
              {entry.changed_by && (
                <Typography variant="caption" color="text.secondary">
                  By: {entry.changed_by}
                </Typography>
              )}
              {entry.notes && (
                <Typography variant="caption" color="text.secondary" fontStyle="italic">
                  {entry.notes}
                </Typography>
              )}
            </Box>
          </StepContent>
        </Step>
      ))}
    </Stepper>
  )
}

export default TRPricingTimeline

import React from 'react'
import { Box, Typography, Paper, Chip, Divider } from '@mui/material'
import type { LdPricingHistory } from '@/types/legaldesk'
import { PRICING_ACTION_LABELS } from '@/types/legaldesk'

interface TRPricingTimelineProps {
  history: LdPricingHistory[]
}

const ACTION_COLORS: Record<string, string> = {
  proposal: '#1976d2',
  counter: '#ed6c02',
  accept: '#2e7d32',
  reject: '#d32f2f',
  adjust: '#9c27b0',
  final: '#0288d1',
}

export const TRPricingTimeline: React.FC<TRPricingTimelineProps> = ({ history }) => {
  if (history.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
        No pricing history yet.
      </Typography>
    )
  }

  const sorted = [...history].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  )

  return (
    <Box>
      {sorted.map((entry, index) => (
        <React.Fragment key={entry.id}>
          <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Chip
                label={PRICING_ACTION_LABELS[entry.action]}
                size="small"
                sx={{
                  backgroundColor: ACTION_COLORS[entry.action] || '#757575',
                  color: '#fff',
                  fontWeight: 600,
                }}
              />
              <Typography variant="caption" color="text.secondary">
                {new Date(entry.created_at).toLocaleString()}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'baseline' }}>
              {entry.new_amount != null && (
                <Typography variant="body1" fontWeight={600}>
                  {entry.currency} {entry.new_amount.toLocaleString()}
                </Typography>
              )}
              {entry.previous_amount != null && (
                <Typography variant="caption" color="text.secondary">
                  (prev: {entry.currency} {entry.previous_amount.toLocaleString()})
                </Typography>
              )}
            </Box>
            {entry.changed_by && (
              <Typography variant="caption" color="text.secondary">
                By: {entry.changed_by}
              </Typography>
            )}
            {entry.notes && (
              <Typography variant="body2" sx={{ mt: 0.5, fontStyle: 'italic' }}>
                {entry.notes}
              </Typography>
            )}
          </Paper>
          {index < sorted.length - 1 && (
            <Divider sx={{ my: 0.5, borderStyle: 'dashed' }} />
          )}
        </React.Fragment>
      ))}
    </Box>
  )
}

export default TRPricingTimeline

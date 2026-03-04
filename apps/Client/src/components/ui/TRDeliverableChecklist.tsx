import React from 'react'
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Typography,
  Chip,
  Box,
} from '@mui/material'
import type { LdCaseDeliverable, DeliverableStatus } from '@/types/legaldesk'
import { DELIVERABLE_STATUS_LABELS, DELIVERABLE_STATUS_COLORS } from '@/types/legaldesk'

interface TRDeliverableChecklistProps {
  deliverables: LdCaseDeliverable[]
  onStatusChange: (deliverableId: number, status: DeliverableStatus) => void
}

export const TRDeliverableChecklist: React.FC<TRDeliverableChecklistProps> = ({
  deliverables,
  onStatusChange,
}) => {
  if (deliverables.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
        No deliverables yet.
      </Typography>
    )
  }

  const handleToggle = (deliverable: LdCaseDeliverable) => {
    const newStatus: DeliverableStatus =
      deliverable.status === 'completed' ? 'pending' : 'completed'
    onStatusChange(deliverable.id, newStatus)
  }

  return (
    <List dense>
      {deliverables.map((deliverable) => (
        <ListItem key={deliverable.id} sx={{ py: 1 }}>
          <ListItemIcon>
            <Checkbox
              edge="start"
              checked={deliverable.status === 'completed'}
              onChange={() => handleToggle(deliverable)}
            />
          </ListItemIcon>
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    textDecoration: deliverable.status === 'completed' ? 'line-through' : 'none',
                  }}
                >
                  {deliverable.title}
                </Typography>
                <Chip
                  label={DELIVERABLE_STATUS_LABELS[deliverable.status]}
                  size="small"
                  sx={{
                    backgroundColor: DELIVERABLE_STATUS_COLORS[deliverable.status],
                    color: '#fff',
                    fontSize: '0.7rem',
                  }}
                />
              </Box>
            }
            secondary={
              <Box component="span">
                {deliverable.due_date && (
                  <Typography variant="caption" component="span">
                    Due: {new Date(deliverable.due_date).toLocaleDateString()}
                  </Typography>
                )}
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  )
}

export default TRDeliverableChecklist

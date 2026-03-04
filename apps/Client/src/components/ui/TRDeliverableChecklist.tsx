import {
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
} from '@mui/material'
import type { LdCaseDeliverable, DeliverableStatus } from '@/types/legaldesk'
import { DELIVERABLE_STATUS_LABELS, DELIVERABLE_STATUS_COLORS } from '@/types/legaldesk'

interface TRDeliverableChecklistProps {
  deliverables: LdCaseDeliverable[]
  onStatusChange?: (id: number, status: DeliverableStatus) => void
}

const ALL_STATUSES: DeliverableStatus[] = ['pending', 'in_progress', 'review', 'completed', 'cancelled']

const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'No due date'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export const TRDeliverableChecklist: React.FC<TRDeliverableChecklistProps> = ({
  deliverables,
  onStatusChange,
}) => {
  console.log('INFO [TRDeliverableChecklist]: Rendering', deliverables.length, 'deliverables')

  if (deliverables.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No deliverables
      </Typography>
    )
  }

  return (
    <List dense>
      {deliverables.map((deliverable) => (
        <ListItem
          key={deliverable.id}
          secondaryAction={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {onStatusChange ? (
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select
                    value={deliverable.status}
                    onChange={(e) =>
                      onStatusChange(deliverable.id, e.target.value as DeliverableStatus)
                    }
                    size="small"
                  >
                    {ALL_STATUSES.map((s) => (
                      <MenuItem key={s} value={s}>
                        {DELIVERABLE_STATUS_LABELS[s]}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ) : (
                <Chip
                  label={DELIVERABLE_STATUS_LABELS[deliverable.status]}
                  size="small"
                  sx={{
                    backgroundColor: DELIVERABLE_STATUS_COLORS[deliverable.status],
                    color: '#fff',
                    fontWeight: 500,
                  }}
                />
              )}
            </Box>
          }
        >
          <ListItemText
            primary={deliverable.title}
            secondary={`${deliverable.specialist_id ? `Specialist #${deliverable.specialist_id}` : 'Unassigned'} · Due: ${formatDate(deliverable.due_date)}`}
          />
        </ListItem>
      ))}
    </List>
  )
}

export default TRDeliverableChecklist

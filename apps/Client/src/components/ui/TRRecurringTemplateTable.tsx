import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Typography,
  Box,
  Skeleton,
  Tooltip,
} from '@mui/material'
import { Edit, Delete, PauseCircle } from '@mui/icons-material'
import type { RecurringTemplate, Category } from '@/types'

interface TRRecurringTemplateTableProps {
  templates: RecurringTemplate[]
  categories: Record<string, Category>
  onEdit: (template: RecurringTemplate) => void
  onDeactivate: (templateId: string) => void
  onDelete: (templateId: string) => void
  isLoading?: boolean
  canDelete?: boolean
}

/**
 * Format a number as currency.
 */
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

/**
 * Format a date string to a readable format.
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

/**
 * Format frequency to human-readable label.
 */
const formatFrequency = (frequency: string): string => {
  const labels: Record<string, string> = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    yearly: 'Yearly',
  }
  return labels[frequency] || frequency
}

export const TRRecurringTemplateTable: React.FC<TRRecurringTemplateTableProps> = ({
  templates,
  categories,
  onEdit,
  onDeactivate,
  onDelete,
  isLoading = false,
  canDelete = true,
}) => {
  console.log('INFO [TRRecurringTemplateTable]: Rendering with', templates.length, 'templates')

  if (isLoading) {
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Frequency</TableCell>
              <TableCell>Start Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {[1, 2, 3].map((n) => (
              <TableRow key={n}>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  if (templates.length === 0) {
    return (
      <Paper sx={{ p: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4,
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Recurring Templates Found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Create your first recurring template to track regular income or expenses.
          </Typography>
        </Box>
      </Paper>
    )
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Category</TableCell>
            <TableCell align="right">Amount</TableCell>
            <TableCell>Frequency</TableCell>
            <TableCell>Start Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {templates.map((template) => {
            const category = categories[template.category_id]
            return (
              <TableRow key={template.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {template.name}
                  </Typography>
                  {template.description && (
                    <Typography variant="caption" color="text.secondary">
                      {template.description}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={template.type.charAt(0).toUpperCase() + template.type.slice(1)}
                    color={template.type === 'income' ? 'success' : 'error'}
                    size="small"
                    variant="filled"
                  />
                </TableCell>
                <TableCell>{category?.name || 'Unknown'}</TableCell>
                <TableCell
                  align="right"
                  sx={{
                    fontWeight: 'medium',
                    color: template.type === 'income' ? 'success.main' : 'error.main',
                  }}
                >
                  {formatCurrency(template.amount)}
                </TableCell>
                <TableCell>
                  <Chip
                    label={formatFrequency(template.frequency)}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {formatDate(template.start_date)}
                  </Typography>
                  {template.end_date && (
                    <Typography variant="caption" color="text.secondary">
                      until {formatDate(template.end_date)}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={template.is_active ? 'Active' : 'Inactive'}
                    color={template.is_active ? 'success' : 'default'}
                    size="small"
                    variant={template.is_active ? 'filled' : 'outlined'}
                  />
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5 }}>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => onEdit(template)}
                        aria-label="edit template"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {template.is_active && (
                      <Tooltip title="Deactivate">
                        <IconButton
                          size="small"
                          onClick={() => onDeactivate(template.id)}
                          aria-label="deactivate template"
                          color="warning"
                        >
                          <PauseCircle fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {canDelete && (
                      <Tooltip title="Delete permanently">
                        <IconButton
                          size="small"
                          onClick={() => onDelete(template.id)}
                          aria-label="delete template"
                          color="error"
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </TableContainer>
  )
}

export default TRRecurringTemplateTable

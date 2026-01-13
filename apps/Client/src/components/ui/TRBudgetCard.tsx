import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  LinearProgress,
  IconButton,
  Tooltip,
  Chip,
  Alert,
} from '@mui/material'
import { Edit, Delete, Warning } from '@mui/icons-material'
import type { BudgetWithSpending } from '@/types'

interface TRBudgetCardProps {
  budget: BudgetWithSpending
  onEdit: (budget: BudgetWithSpending) => void
  onDelete: (budgetId: string) => void
  canDelete?: boolean
}

/**
 * Get the color for the progress bar based on spending percentage.
 * - Green: < 75%
 * - Yellow/Amber: 75-100%
 * - Red: > 100%
 */
const getProgressColor = (percentage: number): 'success' | 'warning' | 'error' => {
  if (percentage > 100) return 'error'
  if (percentage >= 75) return 'warning'
  return 'success'
}

/**
 * Format currency value.
 */
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

/**
 * Format period type for display.
 */
const formatPeriodType = (periodType: string): string => {
  return periodType.charAt(0).toUpperCase() + periodType.slice(1)
}

export const TRBudgetCard: React.FC<TRBudgetCardProps> = ({
  budget,
  onEdit,
  onDelete,
  canDelete = false,
}) => {
  const progressColor = getProgressColor(budget.spent_percentage)
  const isOverBudget = budget.spent_percentage > 100
  const isNearLimit = budget.spent_percentage >= 75 && budget.spent_percentage <= 100

  const handleEdit = () => {
    console.log('INFO [TRBudgetCard]: Edit budget:', budget.id)
    onEdit(budget)
  }

  const handleDelete = () => {
    console.log('INFO [TRBudgetCard]: Delete budget:', budget.id)
    onDelete(budget.id)
  }

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        border: isOverBudget ? '2px solid' : '1px solid',
        borderColor: isOverBudget ? 'error.main' : 'divider',
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        {/* Header with category name and period chip */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            mb: 1,
          }}
        >
          <Typography variant="h6" component="h3" noWrap sx={{ flex: 1, mr: 1 }}>
            {budget.category_name || 'Unknown Category'}
          </Typography>
          <Chip
            label={formatPeriodType(budget.period_type)}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>

        {/* Budget amount */}
        <Typography variant="h5" color="primary" gutterBottom>
          {formatCurrency(budget.amount)}
        </Typography>

        {/* Progress bar */}
        <Box sx={{ mt: 2, mb: 1 }}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 0.5,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Spent: {formatCurrency(budget.spent_amount)}
            </Typography>
            <Typography
              variant="body2"
              fontWeight="bold"
              color={`${progressColor}.main`}
            >
              {budget.spent_percentage.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(budget.spent_percentage, 100)}
            color={progressColor}
            sx={{ height: 10, borderRadius: 1 }}
          />
        </Box>

        {/* Spending summary */}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {formatCurrency(budget.spent_amount)} / {formatCurrency(budget.amount)}
        </Typography>

        {/* Period dates */}
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
          Period: {budget.start_date}
          {budget.end_date && ` to ${budget.end_date}`}
        </Typography>

        {/* Warning alerts */}
        {isOverBudget && (
          <Alert
            severity="error"
            icon={<Warning />}
            sx={{ mt: 2, py: 0 }}
          >
            Over budget by {formatCurrency(budget.spent_amount - budget.amount)}!
          </Alert>
        )}
        {isNearLimit && (
          <Alert
            severity="warning"
            icon={<Warning />}
            sx={{ mt: 2, py: 0 }}
          >
            Approaching budget limit
          </Alert>
        )}
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
        <Tooltip title="Edit Budget">
          <IconButton
            size="small"
            onClick={handleEdit}
            color="primary"
            aria-label="edit budget"
          >
            <Edit />
          </IconButton>
        </Tooltip>
        {canDelete && (
          <Tooltip title="Delete Budget">
            <IconButton
              size="small"
              onClick={handleDelete}
              color="error"
              aria-label="delete budget"
            >
              <Delete />
            </IconButton>
          </Tooltip>
        )}
      </CardActions>
    </Card>
  )
}

export default TRBudgetCard

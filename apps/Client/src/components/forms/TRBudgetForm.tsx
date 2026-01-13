import { useEffect, useMemo } from 'react'
import { useForm, Controller } from 'react-hook-form'
import {
  TextField,
  Button,
  Box,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  FormHelperText,
  InputAdornment,
  CircularProgress,
} from '@mui/material'
import type { BudgetWithSpending, BudgetCreate, BudgetPeriodType, Category } from '@/types'

interface BudgetFormData {
  category_id: string
  amount: string
  period_type: BudgetPeriodType
  start_date: string
}

interface TRBudgetFormProps {
  onSubmit: (data: BudgetCreate) => Promise<void>
  initialData?: BudgetWithSpending
  categories: Category[]
  entityId: string
  isLoading?: boolean
  onCancel?: () => void
}

export const TRBudgetForm: React.FC<TRBudgetFormProps> = ({
  onSubmit,
  initialData,
  categories,
  entityId,
  isLoading = false,
  onCancel,
}) => {
  const isEditMode = !!initialData

  // Get the first day of the current month as default start date
  const defaultStartDate = useMemo(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
  }, [])

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BudgetFormData>({
    defaultValues: {
      category_id: initialData?.category_id || '',
      amount: initialData?.amount.toString() || '',
      period_type: initialData?.period_type || 'monthly',
      start_date: initialData?.start_date || defaultStartDate,
    },
  })

  // Reset form when initialData changes
  useEffect(() => {
    if (initialData) {
      reset({
        category_id: initialData.category_id,
        amount: initialData.amount.toString(),
        period_type: initialData.period_type,
        start_date: initialData.start_date,
      })
    }
  }, [initialData, reset])

  // Filter categories to expense only
  const expenseCategories = useMemo(
    () => categories.filter((cat) => cat.type === 'expense' && cat.is_active),
    [categories]
  )

  const handleFormSubmit = async (data: BudgetFormData) => {
    console.log('INFO [TRBudgetForm]: Form submitted', data)
    try {
      const budgetData: BudgetCreate = {
        entity_id: entityId,
        category_id: data.category_id,
        amount: parseFloat(data.amount),
        period_type: data.period_type,
        start_date: data.start_date,
      }
      await onSubmit(budgetData)
      console.log('INFO [TRBudgetForm]: Budget submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRBudgetForm]: Failed to submit budget:', error)
    }
  }

  const isFormLoading = isLoading || isSubmitting

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      noValidate
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <Controller
        name="category_id"
        control={control}
        rules={{ required: 'Category is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.category_id} disabled={isEditMode}>
            <InputLabel id="category-label">Category</InputLabel>
            <Select
              {...field}
              labelId="category-label"
              label="Category"
              disabled={isFormLoading || expenseCategories.length === 0 || isEditMode}
            >
              {expenseCategories.length === 0 ? (
                <MenuItem value="" disabled>
                  No expense categories available
                </MenuItem>
              ) : (
                expenseCategories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))
              )}
            </Select>
            {errors.category_id && (
              <FormHelperText>{errors.category_id.message}</FormHelperText>
            )}
            {expenseCategories.length === 0 && (
              <FormHelperText>
                No expense categories available. Please create an expense category first.
              </FormHelperText>
            )}
            {isEditMode && (
              <FormHelperText>
                Category cannot be changed for existing budgets.
              </FormHelperText>
            )}
          </FormControl>
        )}
      />

      <TextField
        {...register('amount', {
          required: 'Amount is required',
          min: { value: 0.01, message: 'Amount must be greater than 0' },
          pattern: {
            value: /^\d+(\.\d{1,2})?$/,
            message: 'Invalid amount format',
          },
        })}
        label="Budget Amount"
        type="number"
        fullWidth
        error={!!errors.amount}
        helperText={errors.amount?.message}
        disabled={isFormLoading}
        InputProps={{
          startAdornment: <InputAdornment position="start">$</InputAdornment>,
        }}
        inputProps={{
          step: '0.01',
          min: '0.01',
        }}
      />

      <Controller
        name="period_type"
        control={control}
        rules={{ required: 'Period type is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.period_type}>
            <InputLabel id="period-type-label">Period Type</InputLabel>
            <Select
              {...field}
              labelId="period-type-label"
              label="Period Type"
              disabled={isFormLoading}
            >
              <MenuItem value="monthly">Monthly</MenuItem>
              <MenuItem value="quarterly">Quarterly</MenuItem>
              <MenuItem value="yearly">Yearly</MenuItem>
            </Select>
            {errors.period_type && (
              <FormHelperText>{errors.period_type.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      <TextField
        {...register('start_date', {
          required: 'Start date is required',
        })}
        label="Start Date"
        type="date"
        fullWidth
        error={!!errors.start_date}
        helperText={errors.start_date?.message || 'Budget period starts from this date'}
        disabled={isFormLoading}
        InputLabelProps={{
          shrink: true,
        }}
      />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 1 }}>
        {onCancel && (
          <Button
            type="button"
            variant="outlined"
            onClick={onCancel}
            disabled={isFormLoading}
          >
            Cancel
          </Button>
        )}
        <Button
          type="submit"
          variant="contained"
          disabled={isFormLoading}
        >
          {isFormLoading ? (
            <CircularProgress size={24} />
          ) : isEditMode ? (
            'Update Budget'
          ) : (
            'Add Budget'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRBudgetForm

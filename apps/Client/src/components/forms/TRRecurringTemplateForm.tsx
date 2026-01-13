import { useEffect } from 'react'
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
import type {
  RecurringTemplate,
  RecurringTemplateCreate,
  TransactionType,
  RecurrenceFrequency,
  Category,
} from '@/types'

interface RecurringTemplateFormData {
  name: string
  amount: string
  type: TransactionType
  category_id: string
  frequency: RecurrenceFrequency
  start_date: string
  end_date: string
  description: string
  notes: string
}

interface TRRecurringTemplateFormProps {
  onSubmit: (data: RecurringTemplateCreate) => Promise<void>
  initialData?: RecurringTemplate
  categories: Category[]
  entityId: string
  isLoading?: boolean
  onCancel?: () => void
}

const FREQUENCY_OPTIONS: { value: RecurrenceFrequency; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
]

export const TRRecurringTemplateForm: React.FC<TRRecurringTemplateFormProps> = ({
  onSubmit,
  initialData,
  categories,
  entityId,
  isLoading = false,
  onCancel,
}) => {
  const isEditMode = !!initialData

  const {
    register,
    handleSubmit,
    control,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RecurringTemplateFormData>({
    defaultValues: {
      name: initialData?.name || '',
      amount: initialData?.amount.toString() || '',
      type: initialData?.type || 'expense',
      category_id: initialData?.category_id || '',
      frequency: initialData?.frequency || 'monthly',
      start_date: initialData?.start_date || new Date().toISOString().split('T')[0],
      end_date: initialData?.end_date || '',
      description: initialData?.description || '',
      notes: initialData?.notes || '',
    },
  })

  const selectedType = watch('type')

  // Reset form when initialData changes
  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        amount: initialData.amount.toString(),
        type: initialData.type,
        category_id: initialData.category_id,
        frequency: initialData.frequency,
        start_date: initialData.start_date,
        end_date: initialData.end_date || '',
        description: initialData.description || '',
        notes: initialData.notes || '',
      })
    }
  }, [initialData, reset])

  // Filter categories by selected type
  const filteredCategories = categories.filter((cat) => cat.type === selectedType)

  const handleFormSubmit = async (data: RecurringTemplateFormData) => {
    console.log('INFO [TRRecurringTemplateForm]: Form submitted', data)
    try {
      const templateData: RecurringTemplateCreate = {
        entity_id: entityId,
        category_id: data.category_id,
        name: data.name,
        amount: parseFloat(data.amount),
        type: data.type,
        frequency: data.frequency,
        start_date: data.start_date,
        end_date: data.end_date || undefined,
        description: data.description || undefined,
        notes: data.notes || undefined,
      }
      await onSubmit(templateData)
      console.log('INFO [TRRecurringTemplateForm]: Template submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRRecurringTemplateForm]: Failed to submit template:', error)
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
      <TextField
        {...register('name', {
          required: 'Name is required',
          maxLength: { value: 255, message: 'Name must be less than 255 characters' },
        })}
        label="Template Name"
        fullWidth
        error={!!errors.name}
        helperText={errors.name?.message}
        disabled={isFormLoading}
        placeholder="e.g., Netflix Subscription, Monthly Rent"
      />

      <Controller
        name="type"
        control={control}
        rules={{ required: 'Transaction type is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.type}>
            <InputLabel id="type-label">Type</InputLabel>
            <Select
              {...field}
              labelId="type-label"
              label="Type"
              disabled={isFormLoading}
            >
              <MenuItem value="income">Income</MenuItem>
              <MenuItem value="expense">Expense</MenuItem>
            </Select>
            {errors.type && <FormHelperText>{errors.type.message}</FormHelperText>}
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
        label="Amount"
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
        name="category_id"
        control={control}
        rules={{ required: 'Category is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.category_id}>
            <InputLabel id="category-label">Category</InputLabel>
            <Select
              {...field}
              labelId="category-label"
              label="Category"
              disabled={isFormLoading || filteredCategories.length === 0}
            >
              {filteredCategories.length === 0 ? (
                <MenuItem value="" disabled>
                  No categories available
                </MenuItem>
              ) : (
                filteredCategories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))
              )}
            </Select>
            {errors.category_id && (
              <FormHelperText>{errors.category_id.message}</FormHelperText>
            )}
            {filteredCategories.length === 0 && (
              <FormHelperText>
                No categories available for {selectedType}. Please create a category first.
              </FormHelperText>
            )}
          </FormControl>
        )}
      />

      <Controller
        name="frequency"
        control={control}
        rules={{ required: 'Frequency is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.frequency}>
            <InputLabel id="frequency-label">Frequency</InputLabel>
            <Select
              {...field}
              labelId="frequency-label"
              label="Frequency"
              disabled={isFormLoading}
            >
              {FREQUENCY_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {errors.frequency && <FormHelperText>{errors.frequency.message}</FormHelperText>}
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
        helperText={errors.start_date?.message}
        disabled={isFormLoading}
        InputLabelProps={{
          shrink: true,
        }}
      />

      <TextField
        {...register('end_date')}
        label="End Date (Optional)"
        type="date"
        fullWidth
        error={!!errors.end_date}
        helperText={errors.end_date?.message || 'Leave empty for no end date'}
        disabled={isFormLoading}
        InputLabelProps={{
          shrink: true,
        }}
      />

      <TextField
        {...register('description', {
          maxLength: { value: 500, message: 'Description must be less than 500 characters' },
        })}
        label="Description"
        fullWidth
        error={!!errors.description}
        helperText={errors.description?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('notes')}
        label="Notes"
        fullWidth
        multiline
        rows={3}
        error={!!errors.notes}
        helperText={errors.notes?.message}
        disabled={isFormLoading}
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
            'Update Template'
          ) : (
            'Add Template'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRRecurringTemplateForm

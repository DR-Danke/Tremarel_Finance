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
import type { Transaction, TransactionCreate, TransactionType, Category } from '@/types'

interface TransactionFormData {
  amount: string
  type: TransactionType
  category_id: string
  date: string
  description: string
  notes: string
}

interface TRTransactionFormProps {
  onSubmit: (data: TransactionCreate) => Promise<void>
  initialData?: Transaction
  categories: Category[]
  entityId: string
  isLoading?: boolean
  onCancel?: () => void
}

export const TRTransactionForm: React.FC<TRTransactionFormProps> = ({
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
  } = useForm<TransactionFormData>({
    defaultValues: {
      amount: initialData?.amount.toString() || '',
      type: initialData?.type || 'expense',
      category_id: initialData?.category_id || '',
      date: initialData?.date || new Date().toISOString().split('T')[0],
      description: initialData?.description || '',
      notes: initialData?.notes || '',
    },
  })

  const selectedType = watch('type')

  // Reset form when initialData changes
  useEffect(() => {
    if (initialData) {
      reset({
        amount: initialData.amount.toString(),
        type: initialData.type,
        category_id: initialData.category_id,
        date: initialData.date,
        description: initialData.description || '',
        notes: initialData.notes || '',
      })
    }
  }, [initialData, reset])

  // Filter categories by selected type
  const filteredCategories = categories.filter((cat) => cat.type === selectedType)

  const handleFormSubmit = async (data: TransactionFormData) => {
    console.log('INFO [TRTransactionForm]: Form submitted', data)
    try {
      const transactionData: TransactionCreate = {
        entity_id: entityId,
        category_id: data.category_id,
        amount: parseFloat(data.amount),
        type: data.type,
        date: data.date,
        description: data.description || undefined,
        notes: data.notes || undefined,
      }
      await onSubmit(transactionData)
      console.log('INFO [TRTransactionForm]: Transaction submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRTransactionForm]: Failed to submit transaction:', error)
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

      <TextField
        {...register('date', {
          required: 'Date is required',
        })}
        label="Date"
        type="date"
        fullWidth
        error={!!errors.date}
        helperText={errors.date?.message}
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
            'Update Transaction'
          ) : (
            'Add Transaction'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRTransactionForm

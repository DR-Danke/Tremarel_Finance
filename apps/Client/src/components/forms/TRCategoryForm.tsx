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
  CircularProgress,
} from '@mui/material'
import type { Category, CategoryType, CategoryCreateInput, CategoryUpdateInput } from '@/types'

interface CategoryFormData {
  name: string
  type: CategoryType
  parent_id: string
  description: string
}

interface TRCategoryFormProps {
  onSubmit: (data: CategoryCreateInput | CategoryUpdateInput) => Promise<void>
  category?: Category
  parentCategories: Category[]
  entityId: string
  onCancel?: () => void
  isLoading?: boolean
}

/**
 * Form component for creating and editing categories.
 * Uses react-hook-form with Material-UI components.
 */
export const TRCategoryForm: React.FC<TRCategoryFormProps> = ({
  onSubmit,
  category,
  parentCategories,
  entityId,
  onCancel,
  isLoading = false,
}) => {
  const isEditMode = !!category

  const {
    control,
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CategoryFormData>({
    defaultValues: {
      name: category?.name || '',
      type: category?.type || 'expense',
      parent_id: category?.parent_id || '',
      description: category?.description || '',
    },
  })

  // Watch the type field to filter parent categories
  const selectedType = watch('type')

  // Filter parent categories by selected type (only show same type as potential parents)
  const filteredParentCategories = parentCategories.filter(
    (cat) => cat.type === selectedType && cat.id !== category?.id
  )

  // Reset form when category changes
  useEffect(() => {
    if (category) {
      reset({
        name: category.name,
        type: category.type,
        parent_id: category.parent_id || '',
        description: category.description || '',
      })
    } else {
      reset({
        name: '',
        type: 'expense',
        parent_id: '',
        description: '',
      })
    }
  }, [category, reset])

  const handleFormSubmit = async (data: CategoryFormData) => {
    console.log(`INFO [TRCategoryForm]: Submitting form - ${isEditMode ? 'update' : 'create'}`)

    if (isEditMode) {
      // For updates, only send changed fields
      const updateData: CategoryUpdateInput = {}
      if (data.name !== category.name) updateData.name = data.name
      if (data.parent_id !== (category.parent_id || '')) {
        updateData.parent_id = data.parent_id || null
      }
      if (data.description !== (category.description || '')) {
        updateData.description = data.description || null
      }
      await onSubmit(updateData)
    } else {
      // For creation, send all required fields
      const createData: CategoryCreateInput = {
        entity_id: entityId,
        name: data.name,
        type: data.type,
        parent_id: data.parent_id || null,
        description: data.description || null,
      }
      await onSubmit(createData)
    }

    console.log(`INFO [TRCategoryForm]: Form submitted successfully`)
  }

  const isFormDisabled = isSubmitting || isLoading

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      {/* Name Field */}
      <TextField
        {...register('name', {
          required: 'Name is required',
          minLength: { value: 1, message: 'Name is required' },
          maxLength: { value: 255, message: 'Name must be 255 characters or less' },
        })}
        label="Category Name"
        fullWidth
        error={!!errors.name}
        helperText={errors.name?.message}
        disabled={isFormDisabled}
        autoFocus
      />

      {/* Type Field - Disabled in edit mode */}
      <Controller
        name="type"
        control={control}
        rules={{ required: 'Type is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.type} disabled={isEditMode || isFormDisabled}>
            <InputLabel id="category-type-label">Type</InputLabel>
            <Select {...field} labelId="category-type-label" label="Type">
              <MenuItem value="income">Income</MenuItem>
              <MenuItem value="expense">Expense</MenuItem>
            </Select>
            {errors.type && <FormHelperText>{errors.type.message}</FormHelperText>}
            {isEditMode && (
              <FormHelperText>Type cannot be changed after creation</FormHelperText>
            )}
          </FormControl>
        )}
      />

      {/* Parent Category Field */}
      <Controller
        name="parent_id"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth disabled={isFormDisabled}>
            <InputLabel id="parent-category-label">Parent Category (Optional)</InputLabel>
            <Select {...field} labelId="parent-category-label" label="Parent Category (Optional)">
              <MenuItem value="">
                <em>None (Root Category)</em>
              </MenuItem>
              {filteredParentCategories.map((cat) => (
                <MenuItem key={cat.id} value={cat.id}>
                  {cat.name}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>
              Select a parent to create a subcategory. Only categories of the same type are shown.
            </FormHelperText>
          </FormControl>
        )}
      />

      {/* Description Field */}
      <TextField
        {...register('description')}
        label="Description (Optional)"
        fullWidth
        multiline
        rows={3}
        disabled={isFormDisabled}
      />

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
        {onCancel && (
          <Button onClick={onCancel} disabled={isFormDisabled} variant="outlined">
            Cancel
          </Button>
        )}
        <Button type="submit" variant="contained" disabled={isFormDisabled}>
          {isFormDisabled ? (
            <CircularProgress size={24} />
          ) : isEditMode ? (
            'Update Category'
          ) : (
            'Create Category'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRCategoryForm

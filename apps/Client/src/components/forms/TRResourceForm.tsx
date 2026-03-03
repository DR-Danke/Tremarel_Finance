import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import {
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
} from '@mui/material'
import type { Resource, ResourceCreate, ResourceUpdate } from '@/types/resource'

interface ResourceFormData {
  name: string
  type: string
  unit: string
  current_stock: string
  minimum_stock: string
  last_unit_cost: string
}

interface TRResourceFormProps {
  onSubmit: (data: ResourceCreate | ResourceUpdate) => Promise<void>
  initialData?: Resource
  restaurantId: string
  onCancel: () => void
  isSubmitting?: boolean
}

const RESOURCE_TYPE_OPTIONS = [
  { value: 'producto', label: 'Producto' },
  { value: 'activo', label: 'Activo' },
  { value: 'servicio', label: 'Servicio' },
]

export const TRResourceForm: React.FC<TRResourceFormProps> = ({
  onSubmit,
  initialData,
  restaurantId,
  onCancel,
  isSubmitting = false,
}) => {
  const isEditMode = !!initialData

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting: formSubmitting },
  } = useForm<ResourceFormData>({
    defaultValues: {
      name: initialData?.name || '',
      type: initialData?.type || 'producto',
      unit: initialData?.unit || '',
      current_stock: initialData?.current_stock?.toString() || '0',
      minimum_stock: initialData?.minimum_stock?.toString() || '0',
      last_unit_cost: initialData?.last_unit_cost?.toString() || '0',
    },
  })

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        type: initialData.type,
        unit: initialData.unit,
        current_stock: initialData.current_stock.toString(),
        minimum_stock: initialData.minimum_stock.toString(),
        last_unit_cost: initialData.last_unit_cost.toString(),
      })
    }
  }, [initialData, reset])

  const handleFormSubmit = async (data: ResourceFormData) => {
    console.log('INFO [TRResourceForm]: Submitting resource form', data)
    try {
      if (isEditMode) {
        const updateData: ResourceUpdate = {
          name: data.name,
          type: data.type as ResourceCreate['type'],
          unit: data.unit,
          current_stock: parseFloat(data.current_stock),
          minimum_stock: parseFloat(data.minimum_stock),
          last_unit_cost: parseFloat(data.last_unit_cost),
        }
        await onSubmit(updateData)
      } else {
        const createData: ResourceCreate = {
          restaurant_id: restaurantId,
          name: data.name,
          type: (data.type as ResourceCreate['type']) || 'producto',
          unit: data.unit,
          current_stock: parseFloat(data.current_stock),
          minimum_stock: parseFloat(data.minimum_stock),
          last_unit_cost: parseFloat(data.last_unit_cost),
        }
        await onSubmit(createData)
      }
      console.log('INFO [TRResourceForm]: Resource submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRResourceForm]: Failed to submit resource:', error)
    }
  }

  const isFormLoading = isSubmitting || formSubmitting

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      noValidate
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <TextField
        {...register('name', {
          required: 'El nombre es obligatorio',
          maxLength: { value: 255, message: 'Máximo 255 caracteres' },
        })}
        label="Nombre"
        fullWidth
        error={!!errors.name}
        helperText={errors.name?.message}
        disabled={isFormLoading}
      />

      <Controller
        name="type"
        control={control}
        rules={{ required: 'El tipo es obligatorio' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.type}>
            <InputLabel id="resource-type-label">Tipo</InputLabel>
            <Select
              {...field}
              labelId="resource-type-label"
              label="Tipo"
              disabled={isFormLoading}
            >
              {RESOURCE_TYPE_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
            {errors.type && <FormHelperText>{errors.type.message}</FormHelperText>}
          </FormControl>
        )}
      />

      <TextField
        {...register('unit', {
          required: 'La unidad es obligatoria',
          maxLength: { value: 50, message: 'Máximo 50 caracteres' },
        })}
        label="Unidad"
        fullWidth
        error={!!errors.unit}
        helperText={errors.unit?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('current_stock', {
          required: 'El stock actual es obligatorio',
          validate: (value) => parseFloat(value) >= 0 || 'El stock debe ser >= 0',
        })}
        label="Stock Actual"
        type="number"
        fullWidth
        error={!!errors.current_stock}
        helperText={errors.current_stock?.message}
        disabled={isFormLoading}
        inputProps={{ min: 0, step: 'any' }}
      />

      <TextField
        {...register('minimum_stock', {
          required: 'El stock mínimo es obligatorio',
          validate: (value) => parseFloat(value) >= 0 || 'El stock mínimo debe ser >= 0',
        })}
        label="Stock Mínimo"
        type="number"
        fullWidth
        error={!!errors.minimum_stock}
        helperText={errors.minimum_stock?.message}
        disabled={isFormLoading}
        inputProps={{ min: 0, step: 'any' }}
      />

      <TextField
        {...register('last_unit_cost', {
          required: 'El costo unitario es obligatorio',
          validate: (value) => parseFloat(value) >= 0 || 'El costo debe ser >= 0',
        })}
        label="Último Costo Unitario"
        type="number"
        fullWidth
        error={!!errors.last_unit_cost}
        helperText={errors.last_unit_cost?.message}
        disabled={isFormLoading}
        inputProps={{ min: 0, step: 'any' }}
      />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 1 }}>
        <Button
          type="button"
          variant="outlined"
          onClick={onCancel}
          disabled={isFormLoading}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={isFormLoading}
        >
          {isFormLoading ? (
            <CircularProgress size={24} />
          ) : isEditMode ? (
            'Actualizar Recurso'
          ) : (
            'Agregar Recurso'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRResourceForm

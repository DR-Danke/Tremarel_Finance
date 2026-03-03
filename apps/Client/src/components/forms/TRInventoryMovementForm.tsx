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
  Alert,
} from '@mui/material'
import type { Resource, InventoryMovementCreate } from '@/types/resource'
import type { Person } from '@/types/person'
import { MOVEMENT_TYPE_LABELS, MOVEMENT_REASON_LABELS } from '@/types/resource'
import type { MovementType, MovementReason } from '@/types/resource'

interface MovementFormData {
  resource_id: string
  type: string
  quantity: string
  reason: string
  person_id: string
  notes: string
}

interface TRInventoryMovementFormProps {
  onSubmit: (data: InventoryMovementCreate) => Promise<void>
  resources: Resource[]
  persons?: Person[]
  restaurantId: string
  onCancel: () => void
  isSubmitting?: boolean
}

const MOVEMENT_TYPE_OPTIONS: { value: MovementType; label: string }[] = [
  { value: 'entry', label: MOVEMENT_TYPE_LABELS.entry },
  { value: 'exit', label: MOVEMENT_TYPE_LABELS.exit },
]

const MOVEMENT_REASON_OPTIONS: { value: MovementReason; label: string }[] = [
  { value: 'compra', label: MOVEMENT_REASON_LABELS.compra },
  { value: 'uso', label: MOVEMENT_REASON_LABELS.uso },
  { value: 'produccion', label: MOVEMENT_REASON_LABELS.produccion },
  { value: 'merma', label: MOVEMENT_REASON_LABELS.merma },
  { value: 'receta', label: MOVEMENT_REASON_LABELS.receta },
  { value: 'ajuste', label: MOVEMENT_REASON_LABELS.ajuste },
]

export const TRInventoryMovementForm: React.FC<TRInventoryMovementFormProps> = ({
  onSubmit,
  resources,
  persons,
  restaurantId,
  onCancel,
  isSubmitting = false,
}) => {
  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors, isSubmitting: formSubmitting },
  } = useForm<MovementFormData>({
    defaultValues: {
      resource_id: '',
      type: 'entry',
      quantity: '',
      reason: 'compra',
      person_id: '',
      notes: '',
    },
  })

  const watchedResourceId = watch('resource_id')
  const watchedType = watch('type')
  const watchedQuantity = watch('quantity')

  const selectedResource = resources.find((r) => r.id === watchedResourceId)
  const showStockWarning =
    watchedType === 'exit' &&
    selectedResource &&
    watchedQuantity &&
    parseFloat(watchedQuantity) > selectedResource.current_stock

  const handleFormSubmit = async (data: MovementFormData) => {
    console.log('INFO [TRInventoryMovementForm]: Submitting movement form', data)
    try {
      const createData: InventoryMovementCreate = {
        resource_id: data.resource_id,
        restaurant_id: restaurantId,
        type: data.type as MovementType,
        quantity: parseFloat(data.quantity),
        reason: data.reason as MovementReason,
        person_id: data.person_id || undefined,
        notes: data.notes || undefined,
      }
      await onSubmit(createData)
      console.log('INFO [TRInventoryMovementForm]: Movement submitted successfully')
    } catch (error) {
      console.error('ERROR [TRInventoryMovementForm]: Failed to submit movement:', error)
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
      <Controller
        name="resource_id"
        control={control}
        rules={{ required: 'El recurso es obligatorio' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.resource_id}>
            <InputLabel id="movement-resource-label">Recurso</InputLabel>
            <Select
              {...field}
              labelId="movement-resource-label"
              label="Recurso"
              disabled={isFormLoading}
            >
              {resources.map((resource) => (
                <MenuItem key={resource.id} value={resource.id}>
                  {resource.name} ({resource.current_stock} {resource.unit})
                </MenuItem>
              ))}
            </Select>
            {errors.resource_id && (
              <FormHelperText>{errors.resource_id.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      <Controller
        name="type"
        control={control}
        rules={{ required: 'El tipo es obligatorio' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.type}>
            <InputLabel id="movement-type-label">Tipo</InputLabel>
            <Select
              {...field}
              labelId="movement-type-label"
              label="Tipo"
              disabled={isFormLoading}
            >
              {MOVEMENT_TYPE_OPTIONS.map((opt) => (
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
        {...register('quantity', {
          required: 'La cantidad es obligatoria',
          validate: (value) =>
            parseFloat(value) > 0 || 'La cantidad debe ser mayor a 0',
        })}
        label="Cantidad"
        type="number"
        fullWidth
        error={!!errors.quantity}
        helperText={errors.quantity?.message}
        disabled={isFormLoading}
        inputProps={{ min: 0, step: 'any' }}
      />

      {showStockWarning && (
        <Alert severity="warning">
          La cantidad excede el stock actual ({selectedResource?.current_stock}{' '}
          {selectedResource?.unit}). El stock quedará en negativo.
        </Alert>
      )}

      <Controller
        name="reason"
        control={control}
        rules={{ required: 'La razón es obligatoria' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.reason}>
            <InputLabel id="movement-reason-label">Razón</InputLabel>
            <Select
              {...field}
              labelId="movement-reason-label"
              label="Razón"
              disabled={isFormLoading}
            >
              {MOVEMENT_REASON_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
            {errors.reason && <FormHelperText>{errors.reason.message}</FormHelperText>}
          </FormControl>
        )}
      />

      {persons && persons.length > 0 && (
        <Controller
          name="person_id"
          control={control}
          render={({ field }) => (
            <FormControl fullWidth>
              <InputLabel id="movement-person-label">Persona</InputLabel>
              <Select
                {...field}
                labelId="movement-person-label"
                label="Persona"
                disabled={isFormLoading}
              >
                <MenuItem value="">Ninguna</MenuItem>
                {persons.map((person) => (
                  <MenuItem key={person.id} value={person.id}>
                    {person.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        />
      )}

      <TextField
        {...register('notes')}
        label="Notas"
        fullWidth
        multiline
        rows={3}
        disabled={isFormLoading}
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
          {isFormLoading ? <CircularProgress size={24} /> : 'Registrar Movimiento'}
        </Button>
      </Box>
    </Box>
  )
}

export default TRInventoryMovementForm

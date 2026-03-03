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
import type { Event, EventCreate, EventUpdate } from '@/types/event'
import type { Person } from '@/types/person'
import {
  EVENT_TYPE_OPTIONS,
  EVENT_FREQUENCY_OPTIONS,
  NOTIFICATION_CHANNEL_OPTIONS,
} from '@/types/event'

interface EventFormData {
  type: string
  description: string
  date: string
  frequency: string
  responsible_id: string
  notification_channel: string
}

interface TREventFormProps {
  onSubmit: (data: EventCreate | EventUpdate) => Promise<void>
  initialData?: Event
  restaurantId: string
  persons: Person[]
  onCancel: () => void
  isSubmitting?: boolean
}

export const TREventForm: React.FC<TREventFormProps> = ({
  onSubmit,
  initialData,
  restaurantId,
  persons,
  onCancel,
  isSubmitting = false,
}) => {
  const isEditMode = !!initialData

  const {
    register,
    handleSubmit,
    control,
    reset,
    watch,
    formState: { errors, isSubmitting: formSubmitting },
  } = useForm<EventFormData>({
    defaultValues: {
      type: initialData?.type || '',
      description: initialData?.description || '',
      date: initialData?.date ? initialData.date.slice(0, 16) : '',
      frequency: initialData?.frequency || 'none',
      responsible_id: initialData?.responsible_id || '',
      notification_channel: initialData?.notification_channel || 'email',
    },
  })

  useEffect(() => {
    if (initialData) {
      reset({
        type: initialData.type,
        description: initialData.description || '',
        date: initialData.date ? initialData.date.slice(0, 16) : '',
        frequency: initialData.frequency || 'none',
        responsible_id: initialData.responsible_id || '',
        notification_channel: initialData.notification_channel || 'email',
      })
    }
  }, [initialData, reset])

  const watchedType = watch('type')

  const handleFormSubmit = async (data: EventFormData) => {
    console.log('INFO [TREventForm]: Submitting event form', data)
    try {
      if (isEditMode) {
        const updateData: EventUpdate = {
          type: data.type as EventCreate['type'],
          description: data.description || undefined,
          date: data.date || undefined,
          frequency: data.frequency as EventCreate['frequency'],
          responsible_id: data.responsible_id || undefined,
          notification_channel: data.notification_channel || undefined,
        }
        await onSubmit(updateData)
      } else {
        const createData: EventCreate = {
          restaurant_id: restaurantId,
          type: data.type as EventCreate['type'],
          date: data.date,
          description: data.description || undefined,
          frequency: (data.frequency as EventCreate['frequency']) || 'none',
          responsible_id: data.responsible_id || undefined,
          notification_channel: data.notification_channel || 'email',
        }
        await onSubmit(createData)
      }
      console.log('INFO [TREventForm]: Event submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TREventForm]: Failed to submit event:', error)
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
        name="type"
        control={control}
        rules={{ required: 'El tipo es obligatorio' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.type}>
            <InputLabel id="event-type-label">Tipo</InputLabel>
            <Select
              {...field}
              labelId="event-type-label"
              label="Tipo"
              disabled={isFormLoading}
            >
              {EVENT_TYPE_OPTIONS.map((opt) => (
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
        {...register('description')}
        label="Descripción"
        fullWidth
        multiline
        rows={2}
        error={!!errors.description}
        helperText={errors.description?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('date', { required: 'La fecha es obligatoria' })}
        label="Fecha"
        type="datetime-local"
        fullWidth
        error={!!errors.date}
        helperText={errors.date?.message}
        disabled={isFormLoading}
        InputLabelProps={{ shrink: true }}
      />

      <Controller
        name="frequency"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.frequency}>
            <InputLabel id="event-frequency-label">Frecuencia</InputLabel>
            <Select
              {...field}
              labelId="event-frequency-label"
              label="Frecuencia"
              disabled={isFormLoading}
            >
              {EVENT_FREQUENCY_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
            {errors.frequency && <FormHelperText>{errors.frequency.message}</FormHelperText>}
          </FormControl>
        )}
      />

      <Controller
        name="responsible_id"
        control={control}
        rules={{
          validate: (value) => {
            if (watchedType === 'tarea' && !value) {
              return 'El responsable es obligatorio para tareas'
            }
            return true
          },
        }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.responsible_id}>
            <InputLabel id="event-responsible-label">Responsable</InputLabel>
            <Select
              {...field}
              labelId="event-responsible-label"
              label="Responsable"
              disabled={isFormLoading}
            >
              <MenuItem value="">
                <em>Ninguno</em>
              </MenuItem>
              {persons.map((person) => (
                <MenuItem key={person.id} value={person.id}>
                  {person.name}
                </MenuItem>
              ))}
            </Select>
            {errors.responsible_id && (
              <FormHelperText>{errors.responsible_id.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      <Controller
        name="notification_channel"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.notification_channel}>
            <InputLabel id="event-notification-label">Canal de Notificación</InputLabel>
            <Select
              {...field}
              labelId="event-notification-label"
              label="Canal de Notificación"
              disabled={isFormLoading}
            >
              {NOTIFICATION_CHANNEL_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
            {errors.notification_channel && (
              <FormHelperText>{errors.notification_channel.message}</FormHelperText>
            )}
          </FormControl>
        )}
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
            'Actualizar Evento'
          ) : (
            'Agregar Evento'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TREventForm

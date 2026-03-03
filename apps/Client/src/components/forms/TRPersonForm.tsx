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
import type { Person, PersonCreate, PersonUpdate } from '@/types/person'

interface PersonFormData {
  name: string
  role: string
  type: string
  email: string
  whatsapp: string
}

interface TRPersonFormProps {
  onSubmit: (data: PersonCreate | PersonUpdate) => Promise<void>
  initialData?: Person
  restaurantId: string
  onCancel: () => void
  isSubmitting?: boolean
}

const PERSON_TYPE_OPTIONS = [
  { value: 'employee', label: 'Empleado' },
  { value: 'supplier', label: 'Proveedor' },
  { value: 'owner', label: 'Dueño' },
]

export const TRPersonForm: React.FC<TRPersonFormProps> = ({
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
  } = useForm<PersonFormData>({
    defaultValues: {
      name: initialData?.name || '',
      role: initialData?.role || '',
      type: initialData?.type || 'employee',
      email: initialData?.email || '',
      whatsapp: initialData?.whatsapp || '',
    },
  })

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        role: initialData.role,
        type: initialData.type,
        email: initialData.email || '',
        whatsapp: initialData.whatsapp || '',
      })
    }
  }, [initialData, reset])

  const handleFormSubmit = async (data: PersonFormData) => {
    console.log('INFO [TRPersonForm]: Submitting person form', data)
    try {
      if (isEditMode) {
        const updateData: PersonUpdate = {
          name: data.name,
          role: data.role,
          type: data.type as PersonCreate['type'],
          email: data.email || undefined,
          whatsapp: data.whatsapp || undefined,
        }
        await onSubmit(updateData)
      } else {
        const createData: PersonCreate = {
          restaurant_id: restaurantId,
          name: data.name,
          role: data.role,
          type: (data.type as PersonCreate['type']) || 'employee',
          email: data.email || undefined,
          whatsapp: data.whatsapp || undefined,
        }
        await onSubmit(createData)
      }
      console.log('INFO [TRPersonForm]: Person submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRPersonForm]: Failed to submit person:', error)
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

      <TextField
        {...register('role', {
          required: 'El rol es obligatorio',
        })}
        label="Rol"
        fullWidth
        error={!!errors.role}
        helperText={errors.role?.message}
        disabled={isFormLoading}
      />

      <Controller
        name="type"
        control={control}
        rules={{ required: 'El tipo es obligatorio' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.type}>
            <InputLabel id="person-type-label">Tipo</InputLabel>
            <Select
              {...field}
              labelId="person-type-label"
              label="Tipo"
              disabled={isFormLoading}
            >
              {PERSON_TYPE_OPTIONS.map((opt) => (
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
        {...register('email', {
          pattern: {
            value: /^$|^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Formato de correo inválido',
          },
        })}
        label="Correo Electrónico"
        type="email"
        fullWidth
        error={!!errors.email}
        helperText={errors.email?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('whatsapp')}
        label="WhatsApp"
        fullWidth
        error={!!errors.whatsapp}
        helperText={errors.whatsapp?.message}
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
          {isFormLoading ? (
            <CircularProgress size={24} />
          ) : isEditMode ? (
            'Actualizar Persona'
          ) : (
            'Agregar Persona'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRPersonForm

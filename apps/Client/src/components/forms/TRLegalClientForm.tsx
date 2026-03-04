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
import type { LdClient, LdClientCreate, LdClientUpdate, ClientType } from '@/types/legaldesk'
import { CLIENT_TYPE_LABELS } from '@/types/legaldesk'

interface ClientFormData {
  name: string
  client_type: ClientType
  contact_email: string
  contact_phone: string
  country: string
  industry: string
}

interface TRLegalClientFormProps {
  onSubmit: (data: LdClientCreate | LdClientUpdate) => Promise<void>
  initialData?: LdClient
  onCancel: () => void
  isSubmitting?: boolean
}

const CLIENT_TYPES = Object.entries(CLIENT_TYPE_LABELS) as [ClientType, string][]

export const TRLegalClientForm: React.FC<TRLegalClientFormProps> = ({
  onSubmit,
  initialData,
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
  } = useForm<ClientFormData>({
    defaultValues: {
      name: initialData?.name || '',
      client_type: initialData?.client_type || 'company',
      contact_email: initialData?.contact_email || '',
      contact_phone: initialData?.contact_phone || '',
      country: initialData?.country || '',
      industry: initialData?.industry || '',
    },
  })

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        client_type: initialData.client_type,
        contact_email: initialData.contact_email || '',
        contact_phone: initialData.contact_phone || '',
        country: initialData.country || '',
        industry: initialData.industry || '',
      })
    }
  }, [initialData, reset])

  const handleFormSubmit = async (data: ClientFormData) => {
    console.log('INFO [TRLegalClientForm]: Submitting client form', data)
    try {
      if (isEditMode) {
        const updateData: LdClientUpdate = {
          name: data.name,
          client_type: data.client_type,
          contact_email: data.contact_email || undefined,
          contact_phone: data.contact_phone || undefined,
          country: data.country || undefined,
          industry: data.industry || undefined,
        }
        await onSubmit(updateData)
      } else {
        const createData: LdClientCreate = {
          name: data.name,
          client_type: data.client_type,
          contact_email: data.contact_email || undefined,
          contact_phone: data.contact_phone || undefined,
          country: data.country || undefined,
          industry: data.industry || undefined,
        }
        await onSubmit(createData)
      }
      console.log('INFO [TRLegalClientForm]: Client submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRLegalClientForm]: Failed to submit client:', error)
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
          required: 'Name is required',
          maxLength: { value: 255, message: 'Maximum 255 characters' },
        })}
        label="Name"
        fullWidth
        error={!!errors.name}
        helperText={errors.name?.message}
        disabled={isFormLoading}
      />

      <Controller
        name="client_type"
        control={control}
        rules={{ required: 'Client type is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.client_type}>
            <InputLabel id="client-type-label">Client Type</InputLabel>
            <Select
              {...field}
              labelId="client-type-label"
              label="Client Type"
              disabled={isFormLoading}
            >
              {CLIENT_TYPES.map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
            {errors.client_type && (
              <FormHelperText>{errors.client_type.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      <TextField
        {...register('contact_email', {
          pattern: {
            value: /^$|^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Invalid email format',
          },
        })}
        label="Contact Email"
        type="email"
        fullWidth
        error={!!errors.contact_email}
        helperText={errors.contact_email?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('contact_phone')}
        label="Contact Phone"
        fullWidth
        disabled={isFormLoading}
      />

      <TextField
        {...register('country')}
        label="Country"
        fullWidth
        disabled={isFormLoading}
      />

      <TextField
        {...register('industry')}
        label="Industry"
        fullWidth
        disabled={isFormLoading}
      />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 1 }}>
        <Button
          type="button"
          variant="outlined"
          onClick={onCancel}
          disabled={isFormLoading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={isFormLoading}
        >
          {isFormLoading ? (
            <CircularProgress size={24} />
          ) : isEditMode ? (
            'Update Client'
          ) : (
            'Create Client'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRLegalClientForm

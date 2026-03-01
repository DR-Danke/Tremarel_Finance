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
import type { Prospect, ProspectCreate, ProspectStage } from '@/types'

interface ProspectFormData {
  company_name: string
  contact_name: string
  contact_email: string
  contact_phone: string
  stage: ProspectStage
  estimated_value: string
  source: string
  notes: string
}

interface TRProspectFormProps {
  onSubmit: (data: ProspectCreate) => Promise<void>
  initialData?: Prospect
  entityId: string
  isLoading?: boolean
  onCancel?: () => void
}

const STAGE_OPTIONS: { value: ProspectStage; label: string }[] = [
  { value: 'lead', label: 'Lead' },
  { value: 'contacted', label: 'Contacted' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'proposal', label: 'Proposal' },
  { value: 'negotiation', label: 'Negotiation' },
  { value: 'won', label: 'Won' },
  { value: 'lost', label: 'Lost' },
]

export const TRProspectForm: React.FC<TRProspectFormProps> = ({
  onSubmit,
  initialData,
  entityId,
  isLoading = false,
  onCancel,
}) => {
  const isEditMode = !!initialData

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProspectFormData>({
    defaultValues: {
      company_name: initialData?.company_name || '',
      contact_name: initialData?.contact_name || '',
      contact_email: initialData?.contact_email || '',
      contact_phone: initialData?.contact_phone || '',
      stage: initialData?.stage || 'lead',
      estimated_value: initialData?.estimated_value?.toString() || '',
      source: initialData?.source || '',
      notes: initialData?.notes || '',
    },
  })

  // Reset form when initialData changes
  useEffect(() => {
    if (initialData) {
      reset({
        company_name: initialData.company_name,
        contact_name: initialData.contact_name || '',
        contact_email: initialData.contact_email || '',
        contact_phone: initialData.contact_phone || '',
        stage: initialData.stage,
        estimated_value: initialData.estimated_value?.toString() || '',
        source: initialData.source || '',
        notes: initialData.notes || '',
      })
    }
  }, [initialData, reset])

  const handleFormSubmit = async (data: ProspectFormData) => {
    console.log('INFO [TRProspectForm]: Form submitted', data)
    try {
      const payload: ProspectCreate = {
        entity_id: entityId,
        company_name: data.company_name,
        stage: data.stage,
        contact_name: data.contact_name || undefined,
        contact_email: data.contact_email || undefined,
        contact_phone: data.contact_phone || undefined,
        estimated_value: data.estimated_value ? parseFloat(data.estimated_value) : undefined,
        source: data.source || undefined,
        notes: data.notes || undefined,
      }
      await onSubmit(payload)
      console.log('INFO [TRProspectForm]: Prospect submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRProspectForm]: Failed to submit prospect:', error)
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
        {...register('company_name', {
          required: 'Company name is required',
          maxLength: { value: 255, message: 'Company name must be 255 characters or less' },
        })}
        label="Company Name"
        fullWidth
        error={!!errors.company_name}
        helperText={errors.company_name?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('contact_name', {
          maxLength: { value: 255, message: 'Contact name must be 255 characters or less' },
        })}
        label="Contact Name"
        fullWidth
        error={!!errors.contact_name}
        helperText={errors.contact_name?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('contact_email', {
          maxLength: { value: 255, message: 'Contact email must be 255 characters or less' },
          pattern: {
            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
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
        {...register('contact_phone', {
          maxLength: { value: 100, message: 'Contact phone must be 100 characters or less' },
        })}
        label="Contact Phone"
        fullWidth
        error={!!errors.contact_phone}
        helperText={errors.contact_phone?.message}
        disabled={isFormLoading}
      />

      <Controller
        name="stage"
        control={control}
        rules={{ required: 'Pipeline stage is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.stage}>
            <InputLabel id="stage-label">Pipeline Stage</InputLabel>
            <Select
              {...field}
              labelId="stage-label"
              label="Pipeline Stage"
              disabled={isFormLoading}
            >
              {STAGE_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {errors.stage && (
              <FormHelperText>{errors.stage.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      <TextField
        {...register('estimated_value', {
          min: { value: 0, message: 'Estimated value must be 0 or greater' },
        })}
        label="Estimated Value"
        type="number"
        fullWidth
        error={!!errors.estimated_value}
        helperText={errors.estimated_value?.message}
        disabled={isFormLoading}
        InputProps={{
          startAdornment: <InputAdornment position="start">$</InputAdornment>,
        }}
        inputProps={{
          step: '0.01',
          min: '0',
        }}
      />

      <TextField
        {...register('source', {
          maxLength: { value: 100, message: 'Source must be 100 characters or less' },
        })}
        label="Source"
        fullWidth
        error={!!errors.source}
        helperText={errors.source?.message}
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
            'Update Prospect'
          ) : (
            'Add Prospect'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRProspectForm

import React from 'react'
import { useForm, Controller } from 'react-hook-form'
import { TextField, Button, Grid, Box } from '@mui/material'
import type { LdSpecialistCreate } from '@/types/legaldesk'

interface TRLegalSpecialistFormProps {
  onSubmit: (data: LdSpecialistCreate) => Promise<void>
  loading?: boolean
}

export const TRLegalSpecialistForm: React.FC<TRLegalSpecialistFormProps> = ({
  onSubmit,
  loading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LdSpecialistCreate>({
    defaultValues: {
      full_name: '',
      email: '',
      phone: '',
      years_experience: undefined,
      hourly_rate: undefined,
      currency: 'USD',
      max_concurrent_cases: undefined,
    },
  })

  const handleFormSubmit = async (data: LdSpecialistCreate) => {
    console.log('INFO [TRLegalSpecialistForm]: Submitting specialist form')
    await onSubmit(data)
  }

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Controller
            name="full_name"
            control={control}
            rules={{ required: 'Full name is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Full Name"
                fullWidth
                error={!!errors.full_name}
                helperText={errors.full_name?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="email"
            control={control}
            rules={{
              required: 'Email is required',
              pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email' },
            }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Email"
                type="email"
                fullWidth
                error={!!errors.email}
                helperText={errors.email?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="phone"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Phone" fullWidth />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="years_experience"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                value={value ?? ''}
                onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
                label="Years Experience"
                type="number"
                fullWidth
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="hourly_rate"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                value={value ?? ''}
                onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
                label="Hourly Rate"
                type="number"
                fullWidth
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="currency"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Currency" fullWidth />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="max_concurrent_cases"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                value={value ?? ''}
                onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
                label="Max Concurrent Cases"
                type="number"
                fullWidth
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Button type="submit" variant="contained" fullWidth disabled={loading}>
            {loading ? 'Creating...' : 'Create Specialist'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  )
}

export default TRLegalSpecialistForm

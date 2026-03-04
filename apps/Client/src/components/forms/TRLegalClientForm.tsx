import React from 'react'
import { useForm, Controller } from 'react-hook-form'
import { TextField, Button, MenuItem, Grid, Box } from '@mui/material'
import type { LdClientCreate } from '@/types/legaldesk'
import { CLIENT_TYPE_LABELS } from '@/types/legaldesk'

interface TRLegalClientFormProps {
  onSubmit: (data: LdClientCreate) => Promise<void>
  loading?: boolean
}

export const TRLegalClientForm: React.FC<TRLegalClientFormProps> = ({
  onSubmit,
  loading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LdClientCreate>({
    defaultValues: {
      name: '',
      client_type: 'company',
      contact_email: '',
      contact_phone: '',
      country: '',
      industry: '',
      notes: '',
    },
  })

  const handleFormSubmit = async (data: LdClientCreate) => {
    console.log('INFO [TRLegalClientForm]: Submitting client form')
    await onSubmit(data)
  }

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Controller
            name="name"
            control={control}
            rules={{ required: 'Name is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Name"
                fullWidth
                error={!!errors.name}
                helperText={errors.name?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="client_type"
            control={control}
            render={({ field }) => (
              <TextField {...field} select label="Client Type" fullWidth>
                {Object.entries(CLIENT_TYPE_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="contact_email"
            control={control}
            rules={{
              pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email' },
            }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Contact Email"
                type="email"
                fullWidth
                error={!!errors.contact_email}
                helperText={errors.contact_email?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="contact_phone"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Contact Phone" fullWidth />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="country"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Country" fullWidth />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="industry"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Industry" fullWidth />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="notes"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Notes" fullWidth multiline rows={2} />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Button type="submit" variant="contained" fullWidth disabled={loading}>
            {loading ? 'Creating...' : 'Create Client'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  )
}

export default TRLegalClientForm

import React from 'react'
import { useForm, Controller } from 'react-hook-form'
import {
  TextField,
  Button,
  MenuItem,
  Grid,
  Box,
} from '@mui/material'
import type { LdCaseCreate, LdClient } from '@/types/legaldesk'
import {
  LEGAL_DOMAIN_LABELS,
  CASE_COMPLEXITY_LABELS,
  CASE_PRIORITY_LABELS,
} from '@/types/legaldesk'

interface TRLegalCaseFormProps {
  onSubmit: (data: LdCaseCreate) => Promise<void>
  clients: LdClient[]
  loading?: boolean
}

export const TRLegalCaseForm: React.FC<TRLegalCaseFormProps> = ({
  onSubmit,
  clients,
  loading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LdCaseCreate>({
    defaultValues: {
      title: '',
      client_id: 0,
      legal_domain: 'corporate',
      description: '',
      complexity: 'medium',
      priority: 'medium',
      budget: undefined,
      estimated_cost: undefined,
      deadline: '',
    },
  })

  const handleFormSubmit = async (data: LdCaseCreate) => {
    console.log('INFO [TRLegalCaseForm]: Submitting case form')
    await onSubmit(data)
  }

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Controller
            name="title"
            control={control}
            rules={{ required: 'Title is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="Title"
                fullWidth
                error={!!errors.title}
                helperText={errors.title?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="client_id"
            control={control}
            rules={{ required: 'Client is required', min: { value: 1, message: 'Select a client' } }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Client"
                fullWidth
                error={!!errors.client_id}
                helperText={errors.client_id?.message}
              >
                <MenuItem value={0} disabled>Select a client</MenuItem>
                {clients.map((client) => (
                  <MenuItem key={client.id} value={client.id}>
                    {client.name}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="legal_domain"
            control={control}
            rules={{ required: 'Legal domain is required' }}
            render={({ field }) => (
              <TextField
                {...field}
                select
                label="Legal Domain"
                fullWidth
                error={!!errors.legal_domain}
                helperText={errors.legal_domain?.message}
              >
                {Object.entries(LEGAL_DOMAIN_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Description"
                fullWidth
                multiline
                rows={3}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="complexity"
            control={control}
            render={({ field }) => (
              <TextField {...field} select label="Complexity" fullWidth>
                {Object.entries(CASE_COMPLEXITY_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="priority"
            control={control}
            render={({ field }) => (
              <TextField {...field} select label="Priority" fullWidth>
                {Object.entries(CASE_PRIORITY_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="budget"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                value={value ?? ''}
                onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
                label="Budget"
                type="number"
                fullWidth
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="estimated_cost"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                value={value ?? ''}
                onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
                label="Estimated Cost"
                type="number"
                fullWidth
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={4}>
          <Controller
            name="deadline"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Deadline"
                type="date"
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            )}
          />
        </Grid>

        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Case'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  )
}

export default TRLegalCaseForm

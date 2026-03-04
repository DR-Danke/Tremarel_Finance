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
  Autocomplete,
} from '@mui/material'
import type {
  LdCase,
  LdCaseCreate,
  LdCaseUpdate,
  LdClient,
  LegalDomain,
  CaseType,
  CaseComplexity,
  CasePriority,
} from '@/types/legaldesk'
import {
  LEGAL_DOMAIN_LABELS,
  CASE_TYPE_LABELS,
  CASE_COMPLEXITY_LABELS,
  CASE_PRIORITY_LABELS,
} from '@/types/legaldesk'

interface CaseFormData {
  title: string
  description: string
  client_id: number | null
  legal_domain: LegalDomain | ''
  case_type: CaseType | ''
  complexity: CaseComplexity | ''
  priority: CasePriority | ''
  client_budget: string
  deadline: string
  jurisdiction: string
}

interface TRLegalCaseFormProps {
  onSubmit: (data: LdCaseCreate | LdCaseUpdate) => Promise<void>
  initialData?: LdCase
  clients: LdClient[]
  onCancel: () => void
  isSubmitting?: boolean
}

const DOMAIN_OPTIONS = Object.entries(LEGAL_DOMAIN_LABELS) as [LegalDomain, string][]
const TYPE_OPTIONS = Object.entries(CASE_TYPE_LABELS) as [CaseType, string][]
const COMPLEXITY_OPTIONS = Object.entries(CASE_COMPLEXITY_LABELS) as [CaseComplexity, string][]
const PRIORITY_OPTIONS = Object.entries(CASE_PRIORITY_LABELS) as [CasePriority, string][]

export const TRLegalCaseForm: React.FC<TRLegalCaseFormProps> = ({
  onSubmit,
  initialData,
  clients,
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
  } = useForm<CaseFormData>({
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
      client_id: initialData?.client_id || null,
      legal_domain: initialData?.legal_domain || '',
      case_type: initialData?.case_type || '',
      complexity: initialData?.complexity || '',
      priority: initialData?.priority || '',
      client_budget: initialData?.budget?.toString() || '',
      deadline: initialData?.deadline || '',
      jurisdiction: '',
    },
  })

  useEffect(() => {
    if (initialData) {
      reset({
        title: initialData.title,
        description: initialData.description || '',
        client_id: initialData.client_id,
        legal_domain: initialData.legal_domain,
        case_type: initialData.case_type || '',
        complexity: initialData.complexity,
        priority: initialData.priority,
        client_budget: initialData.budget?.toString() || '',
        deadline: initialData.deadline || '',
        jurisdiction: '',
      })
    }
  }, [initialData, reset])

  const handleFormSubmit = async (data: CaseFormData) => {
    console.log('INFO [TRLegalCaseForm]: Submitting case form', data)
    try {
      if (isEditMode) {
        const updateData: LdCaseUpdate = {
          title: data.title,
          description: data.description || undefined,
          legal_domain: data.legal_domain as LegalDomain || undefined,
          complexity: data.complexity as CaseComplexity || undefined,
          priority: data.priority as CasePriority || undefined,
          budget: data.client_budget ? parseFloat(data.client_budget) : undefined,
          deadline: data.deadline || undefined,
        }
        await onSubmit(updateData)
      } else {
        const createData: LdCaseCreate = {
          title: data.title,
          client_id: data.client_id as number,
          legal_domain: data.legal_domain as LegalDomain,
          description: data.description || undefined,
          complexity: data.complexity as CaseComplexity || undefined,
          priority: data.priority as CasePriority || undefined,
          budget: data.client_budget ? parseFloat(data.client_budget) : undefined,
          deadline: data.deadline || undefined,
        }
        await onSubmit(createData)
      }
      console.log('INFO [TRLegalCaseForm]: Case submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRLegalCaseForm]: Failed to submit case:', error)
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
        {...register('title', {
          required: 'Title is required',
          maxLength: { value: 255, message: 'Maximum 255 characters' },
        })}
        label="Title"
        fullWidth
        error={!!errors.title}
        helperText={errors.title?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('description')}
        label="Description"
        fullWidth
        multiline
        rows={3}
        disabled={isFormLoading}
      />

      <Controller
        name="client_id"
        control={control}
        rules={{ required: 'Client is required' }}
        render={({ field }) => (
          <Autocomplete
            options={clients}
            getOptionLabel={(option) => option.name}
            value={clients.find((c) => c.id === field.value) || null}
            onChange={(_, newValue) => field.onChange(newValue?.id || null)}
            disabled={isFormLoading}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Client"
                error={!!errors.client_id}
                helperText={errors.client_id?.message}
              />
            )}
          />
        )}
      />

      <Controller
        name="legal_domain"
        control={control}
        rules={{ required: 'Legal domain is required' }}
        render={({ field }) => (
          <FormControl fullWidth error={!!errors.legal_domain}>
            <InputLabel id="legal-domain-label">Legal Domain</InputLabel>
            <Select
              {...field}
              labelId="legal-domain-label"
              label="Legal Domain"
              disabled={isFormLoading}
            >
              {DOMAIN_OPTIONS.map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
            {errors.legal_domain && (
              <FormHelperText>{errors.legal_domain.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      <Controller
        name="case_type"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth>
            <InputLabel id="case-type-label">Case Type</InputLabel>
            <Select
              {...field}
              labelId="case-type-label"
              label="Case Type"
              disabled={isFormLoading}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {TYPE_OPTIONS.map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      />

      <Controller
        name="complexity"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth>
            <InputLabel id="complexity-label">Complexity</InputLabel>
            <Select
              {...field}
              labelId="complexity-label"
              label="Complexity"
              disabled={isFormLoading}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {COMPLEXITY_OPTIONS.map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      />

      <Controller
        name="priority"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth>
            <InputLabel id="priority-label">Priority</InputLabel>
            <Select
              {...field}
              labelId="priority-label"
              label="Priority"
              disabled={isFormLoading}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {PRIORITY_OPTIONS.map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      />

      <TextField
        {...register('client_budget')}
        label="Client Budget"
        type="number"
        fullWidth
        disabled={isFormLoading}
        inputProps={{ step: '0.01', min: '0' }}
      />

      <TextField
        {...register('deadline')}
        label="Deadline"
        type="date"
        fullWidth
        disabled={isFormLoading}
        InputLabelProps={{ shrink: true }}
      />

      <TextField
        {...register('jurisdiction')}
        label="Jurisdiction"
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
            'Update Case'
          ) : (
            'Create Case'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRLegalCaseForm

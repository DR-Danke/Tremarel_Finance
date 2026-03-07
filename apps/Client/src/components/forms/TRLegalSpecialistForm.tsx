import { useEffect } from 'react'
import { useForm, Controller, useFieldArray } from 'react-hook-form'
import {
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Typography,
  IconButton,
  Divider,
  Checkbox,
  FormControlLabel,
} from '@mui/material'
import { Add, Delete } from '@mui/icons-material'
import type {
  LdSpecialistDetail,
  LdSpecialistCreate,
  LdSpecialistUpdate,
  SpecialistType,
  LegalDomain,
  ProficiencyLevel,
} from '@/types/legaldesk'
import { LEGAL_DOMAIN_LABELS, PROFICIENCY_LEVEL_LABELS } from '@/types/legaldesk'

interface ExpertiseEntry {
  legal_domain: LegalDomain
  proficiency_level: ProficiencyLevel
}

interface JurisdictionEntry {
  country: string
  region: string
  is_primary: boolean
}

interface SpecialistFormData {
  name: string
  specialist_type: SpecialistType
  email: string
  phone: string
  country: string
  years_experience: string
  hourly_rate: string
  expertise: ExpertiseEntry[]
  jurisdictions: JurisdictionEntry[]
}

interface TRLegalSpecialistFormProps {
  onSubmit: (
    data: LdSpecialistCreate | LdSpecialistUpdate,
    expertise?: ExpertiseEntry[],
    jurisdictions?: JurisdictionEntry[]
  ) => Promise<void>
  initialData?: LdSpecialistDetail
  onCancel: () => void
  isSubmitting?: boolean
}

const SPECIALIST_TYPES: [SpecialistType, string][] = [
  ['individual', 'Individual'],
  ['boutique_firm', 'Boutique Firm'],
]

const DOMAIN_OPTIONS = Object.entries(LEGAL_DOMAIN_LABELS) as [LegalDomain, string][]
const PROFICIENCY_OPTIONS = Object.entries(PROFICIENCY_LEVEL_LABELS) as [ProficiencyLevel, string][]

export const TRLegalSpecialistForm: React.FC<TRLegalSpecialistFormProps> = ({
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
  } = useForm<SpecialistFormData>({
    defaultValues: {
      name: initialData?.full_name || '',
      specialist_type: 'individual',
      email: initialData?.email || '',
      phone: initialData?.phone || '',
      country: '',
      years_experience: initialData?.years_experience?.toString() || '',
      hourly_rate: initialData?.hourly_rate?.toString() || '',
      expertise: initialData?.expertise?.map((e) => ({
        legal_domain: e.legal_domain,
        proficiency_level: e.proficiency_level,
      })) || [],
      jurisdictions: initialData?.jurisdictions?.map((j) => ({
        country: j.country,
        region: j.region || '',
        is_primary: j.is_primary,
      })) || [],
    },
  })

  const {
    fields: expertiseFields,
    append: appendExpertise,
    remove: removeExpertise,
  } = useFieldArray({ control, name: 'expertise' })

  const {
    fields: jurisdictionFields,
    append: appendJurisdiction,
    remove: removeJurisdiction,
  } = useFieldArray({ control, name: 'jurisdictions' })

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.full_name,
        specialist_type: 'individual',
        email: initialData.email,
        phone: initialData.phone || '',
        country: '',
        years_experience: initialData.years_experience?.toString() || '',
        hourly_rate: initialData.hourly_rate?.toString() || '',
        expertise: initialData.expertise?.map((e) => ({
          legal_domain: e.legal_domain,
          proficiency_level: e.proficiency_level,
        })) || [],
        jurisdictions: initialData.jurisdictions?.map((j) => ({
          country: j.country,
          region: j.region || '',
          is_primary: j.is_primary,
        })) || [],
      })
    }
  }, [initialData, reset])

  const handleFormSubmit = async (data: SpecialistFormData) => {
    console.log('INFO [TRLegalSpecialistForm]: Submitting specialist form', data)
    try {
      if (isEditMode) {
        const updateData: LdSpecialistUpdate = {
          full_name: data.name,
          email: data.email,
          phone: data.phone || undefined,
          years_experience: data.years_experience ? parseInt(data.years_experience) : undefined,
          hourly_rate: data.hourly_rate ? parseFloat(data.hourly_rate) : undefined,
        }
        await onSubmit(updateData, data.expertise, data.jurisdictions)
      } else {
        const createData: LdSpecialistCreate = {
          full_name: data.name,
          email: data.email,
          phone: data.phone || undefined,
          years_experience: data.years_experience ? parseInt(data.years_experience) : undefined,
          hourly_rate: data.hourly_rate ? parseFloat(data.hourly_rate) : undefined,
        }
        await onSubmit(createData, data.expertise, data.jurisdictions)
      }
      console.log('INFO [TRLegalSpecialistForm]: Specialist submitted successfully')
      if (!isEditMode) {
        reset()
      }
    } catch (error) {
      console.error('ERROR [TRLegalSpecialistForm]: Failed to submit specialist:', error)
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
        label="Full Name"
        fullWidth
        error={!!errors.name}
        helperText={errors.name?.message}
        disabled={isFormLoading}
      />

      <Controller
        name="specialist_type"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth>
            <InputLabel id="specialist-type-label">Specialist Type</InputLabel>
            <Select
              {...field}
              labelId="specialist-type-label"
              label="Specialist Type"
              disabled={isFormLoading}
            >
              {SPECIALIST_TYPES.map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      />

      <TextField
        {...register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Invalid email format',
          },
        })}
        label="Email"
        type="email"
        fullWidth
        error={!!errors.email}
        helperText={errors.email?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('phone')}
        label="Phone"
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
        {...register('years_experience', {
          min: { value: 0, message: 'Must be 0 or greater' },
        })}
        label="Years of Experience"
        type="number"
        fullWidth
        error={!!errors.years_experience}
        helperText={errors.years_experience?.message}
        disabled={isFormLoading}
        inputProps={{ min: 0 }}
      />

      <TextField
        {...register('hourly_rate', {
          min: { value: 0, message: 'Must be 0 or greater' },
        })}
        label="Hourly Rate"
        type="number"
        fullWidth
        error={!!errors.hourly_rate}
        helperText={errors.hourly_rate?.message}
        disabled={isFormLoading}
        inputProps={{ step: '0.01', min: 0 }}
      />

      <Divider />

      {/* Expertise Section */}
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            Expertise
          </Typography>
          <Button
            size="small"
            startIcon={<Add />}
            onClick={() =>
              appendExpertise({ legal_domain: 'corporate', proficiency_level: 'junior' })
            }
            disabled={isFormLoading}
          >
            Add Expertise
          </Button>
        </Box>
        {expertiseFields.map((field, index) => (
          <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
            <Controller
              name={`expertise.${index}.legal_domain`}
              control={control}
              render={({ field: domainField }) => (
                <FormControl size="small" sx={{ flex: 1 }}>
                  <InputLabel id={`expertise-domain-${index}`}>Domain</InputLabel>
                  <Select
                    {...domainField}
                    labelId={`expertise-domain-${index}`}
                    label="Domain"
                    disabled={isFormLoading}
                  >
                    {DOMAIN_OPTIONS.map(([value, label]) => (
                      <MenuItem key={value} value={value}>
                        {label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            />
            <Controller
              name={`expertise.${index}.proficiency_level`}
              control={control}
              render={({ field: profField }) => (
                <FormControl size="small" sx={{ flex: 1 }}>
                  <InputLabel id={`expertise-prof-${index}`}>Proficiency</InputLabel>
                  <Select
                    {...profField}
                    labelId={`expertise-prof-${index}`}
                    label="Proficiency"
                    disabled={isFormLoading}
                  >
                    {PROFICIENCY_OPTIONS.map(([value, label]) => (
                      <MenuItem key={value} value={value}>
                        {label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            />
            <IconButton
              size="small"
              onClick={() => removeExpertise(index)}
              disabled={isFormLoading}
              color="error"
            >
              <Delete />
            </IconButton>
          </Box>
        ))}
        {expertiseFields.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No expertise added
          </Typography>
        )}
      </Box>

      <Divider />

      {/* Jurisdictions Section */}
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            Jurisdictions
          </Typography>
          <Button
            size="small"
            startIcon={<Add />}
            onClick={() =>
              appendJurisdiction({ country: '', region: '', is_primary: false })
            }
            disabled={isFormLoading}
          >
            Add Jurisdiction
          </Button>
        </Box>
        {jurisdictionFields.map((field, index) => (
          <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
            <TextField
              {...register(`jurisdictions.${index}.country`)}
              label="Country"
              size="small"
              sx={{ flex: 1 }}
              disabled={isFormLoading}
            />
            <TextField
              {...register(`jurisdictions.${index}.region`)}
              label="Region"
              size="small"
              sx={{ flex: 1 }}
              disabled={isFormLoading}
            />
            <Controller
              name={`jurisdictions.${index}.is_primary`}
              control={control}
              render={({ field: primaryField }) => (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={primaryField.value}
                      onChange={primaryField.onChange}
                      disabled={isFormLoading}
                      size="small"
                    />
                  }
                  label="Primary"
                />
              )}
            />
            <IconButton
              size="small"
              onClick={() => removeJurisdiction(index)}
              disabled={isFormLoading}
              color="error"
            >
              <Delete />
            </IconButton>
          </Box>
        ))}
        {jurisdictionFields.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No jurisdictions added
          </Typography>
        )}
      </Box>

      <Divider />

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
            'Update Specialist'
          ) : (
            'Create Specialist'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRLegalSpecialistForm

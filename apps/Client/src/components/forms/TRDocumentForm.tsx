import { useEffect, useState, useRef } from 'react'
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
  Typography,
} from '@mui/material'
import { CloudUpload } from '@mui/icons-material'
import type { Document, DocumentCreate, DocumentUpdate } from '@/types/document'
import type { Person } from '@/types/person'
import { DOCUMENT_TYPES } from '@/types/document'

interface DocumentFormData {
  type: string
  issue_date: string
  expiration_date: string
  person_id: string
  description: string
}

interface TRDocumentFormProps {
  onSubmit: (data: DocumentCreate | DocumentUpdate, file?: File) => Promise<void>
  initialData?: Document
  restaurantId: string
  onCancel: () => void
  isSubmitting?: boolean
  persons: Person[]
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export const TRDocumentForm: React.FC<TRDocumentFormProps> = ({
  onSubmit,
  initialData,
  restaurantId,
  onCancel,
  isSubmitting = false,
  persons,
}) => {
  const isEditMode = !!initialData
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const {
    register,
    handleSubmit,
    control,
    reset,
    watch,
    formState: { errors, isSubmitting: formSubmitting },
  } = useForm<DocumentFormData>({
    defaultValues: {
      type: initialData?.type || '',
      issue_date: initialData?.issue_date || '',
      expiration_date: initialData?.expiration_date || '',
      person_id: initialData?.person_id || '',
      description: initialData?.description || '',
    },
  })

  const issueDate = watch('issue_date')

  useEffect(() => {
    if (initialData) {
      reset({
        type: initialData.type,
        issue_date: initialData.issue_date || '',
        expiration_date: initialData.expiration_date || '',
        person_id: initialData.person_id || '',
        description: initialData.description || '',
      })
    }
  }, [initialData, reset])

  const handleFileSelect = (file: File) => {
    setFileError(null)
    if (file.size > MAX_FILE_SIZE) {
      setFileError('El archivo no debe superar los 10MB')
      return
    }
    setSelectedFile(file)
    console.log('INFO [TRDocumentForm]: File selected:', file.name)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDropZoneClick = () => {
    fileInputRef.current?.click()
  }

  const handleFormSubmit = async (data: DocumentFormData) => {
    console.log('INFO [TRDocumentForm]: Submitting document form', data)
    try {
      if (isEditMode) {
        const updateData: DocumentUpdate = {
          type: data.type as DocumentCreate['type'],
          issue_date: data.issue_date || undefined,
          expiration_date: data.expiration_date || undefined,
          person_id: data.person_id || undefined,
          description: data.description || undefined,
        }
        await onSubmit(updateData)
      } else {
        const createData: DocumentCreate = {
          restaurant_id: restaurantId,
          type: data.type as DocumentCreate['type'],
          issue_date: data.issue_date || undefined,
          expiration_date: data.expiration_date || undefined,
          person_id: data.person_id || undefined,
          description: data.description || undefined,
        }
        await onSubmit(createData, selectedFile || undefined)
      }
      console.log('INFO [TRDocumentForm]: Document submitted successfully')
      if (!isEditMode) {
        reset()
        setSelectedFile(null)
      }
    } catch (error) {
      console.error('ERROR [TRDocumentForm]: Failed to submit document:', error)
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
            <InputLabel id="document-type-label">Tipo</InputLabel>
            <Select
              {...field}
              labelId="document-type-label"
              label="Tipo"
              disabled={isFormLoading}
            >
              {DOCUMENT_TYPES.map((opt) => (
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
        {...register('issue_date')}
        label="Fecha de Emisión"
        type="date"
        fullWidth
        InputLabelProps={{ shrink: true }}
        disabled={isFormLoading}
      />

      <TextField
        {...register('expiration_date', {
          validate: (value) => {
            if (value && issueDate && value <= issueDate) {
              return 'La fecha de vencimiento debe ser posterior a la fecha de emisión'
            }
            return true
          },
        })}
        label="Fecha de Vencimiento"
        type="date"
        fullWidth
        InputLabelProps={{ shrink: true }}
        error={!!errors.expiration_date}
        helperText={errors.expiration_date?.message}
        disabled={isFormLoading}
      />

      <Controller
        name="person_id"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth>
            <InputLabel id="document-person-label">Persona</InputLabel>
            <Select
              {...field}
              labelId="document-person-label"
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

      <TextField
        {...register('description')}
        label="Descripción"
        multiline
        rows={3}
        fullWidth
        disabled={isFormLoading}
      />

      {!isEditMode && (
        <Box>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
          <Box
            onClick={handleDropZoneClick}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            sx={{
              border: '2px dashed',
              borderColor: isDragOver ? 'primary.main' : fileError ? 'error.main' : 'grey.400',
              borderRadius: 1,
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragOver ? 'action.hover' : 'transparent',
              transition: 'all 0.2s',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'action.hover',
              },
            }}
          >
            <CloudUpload sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
            {selectedFile ? (
              <Typography variant="body2" color="primary">
                {selectedFile.name}
              </Typography>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Arrastra un archivo aquí o haz clic para seleccionar
              </Typography>
            )}
          </Box>
          {fileError && (
            <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
              {fileError}
            </Typography>
          )}
        </Box>
      )}

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
            'Actualizar Documento'
          ) : (
            'Agregar Documento'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRDocumentForm

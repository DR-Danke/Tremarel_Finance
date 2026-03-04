import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  CircularProgress,
} from '@mui/material'
import { Add, Edit, Delete } from '@mui/icons-material'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useDocuments } from '@/hooks/useDocuments'
import { usePersons } from '@/hooks/usePersons'
import { TRDocumentForm } from '@/components/forms/TRDocumentForm'
import { TRExpirationBadge } from '@/components/ui/TRExpirationBadge'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Document, DocumentCreate, DocumentUpdate, DocumentType, ExpirationStatus, PermitPreset } from '@/types/document'
import { DOCUMENT_TYPES, EXPIRATION_STATUS_OPTIONS } from '@/types/document'
import { documentService } from '@/services/documentService'

const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  contrato: 'Contrato',
  permiso: 'Permiso',
  factura: 'Factura',
  licencia: 'Licencia',
  factura_proveedor: 'Factura Proveedor',
  certificado: 'Certificado',
  manipulacion_alimentos: 'Cert. Manipulación de Alimentos',
  bomberos: 'Permiso de Bomberos',
  camara_comercio: 'Reg. Cámara de Comercio',
  extintor: 'Servicio de Extintores',
  sanidad: 'Cert. Inspección Sanitaria',
  otro: 'Otro',
}

export const RestaurantOSDocumentsPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading } = useRestaurant()
  const {
    documents,
    isLoading: documentsLoading,
    error,
    setFilters,
    createDocument,
    updateDocument,
    deleteDocument,
  } = useDocuments(currentRestaurant?.id ?? null)

  const { persons } = usePersons(currentRestaurant?.id ?? null)

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [permitPresets, setPermitPresets] = useState<PermitPreset[]>([])

  useEffect(() => {
    documentService.getPermitPresets()
      .then(setPermitPresets)
      .catch((err) => console.error('ERROR [RestaurantOSDocumentsPage]: Failed to fetch permit presets:', err))
  }, [])

  // Loading state
  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <CircularProgress size={24} />
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  // No restaurants
  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  const handleOpenAddDialog = () => {
    console.log('INFO [RestaurantOSDocumentsPage]: Opening add document dialog')
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [RestaurantOSDocumentsPage]: Closing add document dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (document: Document) => {
    console.log('INFO [RestaurantOSDocumentsPage]: Opening edit dialog for document:', document.id)
    setSelectedDocument(document)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [RestaurantOSDocumentsPage]: Closing edit document dialog')
    setIsEditDialogOpen(false)
    setSelectedDocument(null)
  }

  const handleOpenDeleteDialog = (document: Document) => {
    console.log('INFO [RestaurantOSDocumentsPage]: Opening delete dialog for document:', document.id)
    setSelectedDocument(document)
    setIsDeleteDialogOpen(true)
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [RestaurantOSDocumentsPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedDocument(null)
  }

  const handleCreateDocument = async (data: DocumentCreate | DocumentUpdate, file?: File) => {
    console.log('INFO [RestaurantOSDocumentsPage]: Creating document')
    setIsSubmitting(true)
    try {
      await createDocument(data as DocumentCreate, file)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSDocumentsPage]: Failed to create document:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdateDocument = async (data: DocumentCreate | DocumentUpdate) => {
    if (!selectedDocument) return
    console.log('INFO [RestaurantOSDocumentsPage]: Updating document:', selectedDocument.id)
    setIsSubmitting(true)
    try {
      await updateDocument(selectedDocument.id, data as DocumentUpdate)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSDocumentsPage]: Failed to update document:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteDocument = async () => {
    if (!selectedDocument) return
    console.log('INFO [RestaurantOSDocumentsPage]: Deleting document:', selectedDocument.id)
    setIsSubmitting(true)
    try {
      await deleteDocument(selectedDocument.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSDocumentsPage]: Failed to delete document:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTypeFilterChange = (value: string) => {
    setTypeFilter(value)
    setFilters({
      type: value ? (value as DocumentType) : undefined,
      expiration_status: statusFilter ? (statusFilter as ExpirationStatus) : undefined,
    })
  }

  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value)
    setFilters({
      type: typeFilter ? (typeFilter as DocumentType) : undefined,
      expiration_status: value ? (value as ExpirationStatus) : undefined,
    })
  }

  const getPersonName = (personId: string | null): string => {
    if (!personId) return '—'
    const person = persons.find((p) => p.id === personId)
    return person?.name || '—'
  }

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '—'
    return dateStr
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Documentos
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {currentRestaurant?.name}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenAddDialog}
        >
          Agregar Documento
        </Button>
      </Box>

      {/* Error display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters row */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="type-filter-label">Filtrar por tipo</InputLabel>
          <Select
            labelId="type-filter-label"
            value={typeFilter}
            onChange={(e) => handleTypeFilterChange(e.target.value)}
            label="Filtrar por tipo"
          >
            <MenuItem value="">Todos</MenuItem>
            {DOCUMENT_TYPES.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="status-filter-label">Filtrar por estado</InputLabel>
          <Select
            labelId="status-filter-label"
            value={statusFilter}
            onChange={(e) => handleStatusFilterChange(e.target.value)}
            label="Filtrar por estado"
          >
            <MenuItem value="">Todos</MenuItem>
            {EXPIRATION_STATUS_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Data table */}
      {documentsLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : documents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No se encontraron documentos
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Tipo</TableCell>
                <TableCell>Descripción</TableCell>
                <TableCell>Persona</TableCell>
                <TableCell>Fecha de Emisión</TableCell>
                <TableCell>Fecha de Vencimiento</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>{DOCUMENT_TYPE_LABELS[doc.type] || doc.type}</TableCell>
                  <TableCell>{doc.description || '—'}</TableCell>
                  <TableCell>{getPersonName(doc.person_id)}</TableCell>
                  <TableCell>{formatDate(doc.issue_date)}</TableCell>
                  <TableCell>{formatDate(doc.expiration_date)}</TableCell>
                  <TableCell>
                    <TRExpirationBadge status={doc.expiration_status} />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenEditDialog(doc)}
                      aria-label="edit"
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDeleteDialog(doc)}
                      aria-label="delete"
                      color="error"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Documento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRDocumentForm
              onSubmit={handleCreateDocument}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={handleCloseAddDialog}
              isSubmitting={isSubmitting}
              persons={persons}
              permitPresets={permitPresets}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Documento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedDocument && (
              <TRDocumentForm
                onSubmit={handleUpdateDocument}
                initialData={selectedDocument}
                restaurantId={currentRestaurant?.id || ''}
                onCancel={handleCloseEditDialog}
                isSubmitting={isSubmitting}
                persons={persons}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Eliminar Documento</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro que desea eliminar este documento?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            onClick={handleDeleteDocument}
            color="error"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default RestaurantOSDocumentsPage

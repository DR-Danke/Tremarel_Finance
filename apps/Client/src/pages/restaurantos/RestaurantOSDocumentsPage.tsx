import React, { useEffect, useState, useMemo } from 'react'
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
  Chip,
  TableSortLabel,
  TablePagination,
} from '@mui/material'
import { Add, Edit, Delete } from '@mui/icons-material'
import DescriptionIcon from '@mui/icons-material/Description'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useDocuments } from '@/hooks/useDocuments'
import { usePersons } from '@/hooks/usePersons'
import { useSnackbar } from '@/hooks/useSnackbar'
import { useTableSort } from '@/hooks/useTableSort'
import { useTablePagination } from '@/hooks/useTablePagination'
import { TRDocumentForm } from '@/components/forms/TRDocumentForm'
import { TRExpirationBadge } from '@/components/ui/TRExpirationBadge'
import { TRBreadcrumbs } from '@/components/ui/TRBreadcrumbs'
import { TRTableSkeleton } from '@/components/ui/TRTableSkeleton'
import { TREmptyState } from '@/components/ui/TREmptyState'
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
  manipulacion_alimentos: 'Cert. Manipulacion de Alimentos',
  bomberos: 'Permiso de Bomberos',
  camara_comercio: 'Reg. Camara de Comercio',
  extintor: 'Servicio de Extintores',
  sanidad: 'Cert. Inspeccion Sanitaria',
  otro: 'Otro',
}

const STATUS_COLORS: Record<string, 'success' | 'warning' | 'error'> = {
  valid: 'success',
  expiring_soon: 'warning',
  expired: 'error',
}

const STATUS_LABELS: Record<string, string> = {
  valid: 'Vigente',
  expiring_soon: 'Por Vencer',
  expired: 'Vencido',
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
  const { showSnackbar } = useSnackbar()

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [permitPresets, setPermitPresets] = useState<PermitPreset[]>([])

  const { sorted, orderBy, order, onSort } = useTableSort<Document>(documents)
  const { paginated, page, rowsPerPage, totalCount, onPageChange, onRowsPerPageChange } = useTablePagination(sorted)

  useEffect(() => {
    documentService.getPermitPresets()
      .then(setPermitPresets)
      .catch((err) => console.error('ERROR [RestaurantOSDocumentsPage]: Failed to fetch permit presets:', err))
  }, [])

  // Summary stats
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { valid: 0, expiring_soon: 0, expired: 0 }
    for (const doc of documents) {
      counts[doc.expiration_status] = (counts[doc.expiration_status] || 0) + 1
    }
    return counts
  }, [documents])

  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <CircularProgress size={24} />
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  const handleCreateDocument = async (data: DocumentCreate | DocumentUpdate, file?: File) => {
    console.log('INFO [RestaurantOSDocumentsPage]: Creating document')
    setIsSubmitting(true)
    try {
      await createDocument(data as DocumentCreate, file)
      setIsAddDialogOpen(false)
      showSnackbar('Documento creado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSDocumentsPage]: Failed to create document:', err)
      showSnackbar('Error al crear documento', 'error')
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
      setIsEditDialogOpen(false)
      setSelectedDocument(null)
      showSnackbar('Documento actualizado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSDocumentsPage]: Failed to update document:', err)
      showSnackbar('Error al actualizar documento', 'error')
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
      setIsDeleteDialogOpen(false)
      setSelectedDocument(null)
      showSnackbar('Documento eliminado', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSDocumentsPage]: Failed to delete document:', err)
      showSnackbar('Error al eliminar documento', 'error')
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

  const sortableHeader = (label: string, column: keyof Document) => (
    <TableSortLabel
      active={orderBy === column}
      direction={orderBy === column ? order : 'asc'}
      onClick={() => onSort(column)}
    >
      {label}
    </TableSortLabel>
  )

  return (
    <Box sx={{ p: 3 }}>
      <TRBreadcrumbs
        module="RestaurantOS"
        moduleHref="/poc/restaurant-os"
        restaurantName={currentRestaurant?.name}
        currentPage="Documentos"
      />

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Documentos
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setIsAddDialogOpen(true)}
        >
          Agregar Documento
        </Button>
      </Box>

      {/* Summary Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        {Object.entries(statusCounts).map(([status, count]) => (
          <Chip
            key={status}
            label={`${count} ${STATUS_LABELS[status] || status}`}
            color={STATUS_COLORS[status] || 'default'}
            variant="outlined"
          />
        ))}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
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

      {/* Table */}
      {documentsLoading ? (
        <TRTableSkeleton columns={7} />
      ) : documents.length === 0 ? (
        <TREmptyState
          icon={<DescriptionIcon sx={{ fontSize: 64 }} />}
          title="No se encontraron documentos"
          description="Agrega contratos, permisos y certificados"
          actionLabel="Agregar Documento"
          onAction={() => setIsAddDialogOpen(true)}
        />
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{sortableHeader('Tipo', 'type')}</TableCell>
                  <TableCell>{sortableHeader('Descripcion', 'description')}</TableCell>
                  <TableCell>Persona</TableCell>
                  <TableCell>{sortableHeader('Emision', 'issue_date')}</TableCell>
                  <TableCell>{sortableHeader('Vencimiento', 'expiration_date')}</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginated.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>{DOCUMENT_TYPE_LABELS[doc.type] || doc.type}</TableCell>
                    <TableCell>{doc.description || '—'}</TableCell>
                    <TableCell>{getPersonName(doc.person_id)}</TableCell>
                    <TableCell>{doc.issue_date || '—'}</TableCell>
                    <TableCell>{doc.expiration_date || '—'}</TableCell>
                    <TableCell>
                      <TRExpirationBadge status={doc.expiration_status} />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedDocument(doc)
                          setIsEditDialogOpen(true)
                        }}
                        aria-label="edit"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedDocument(doc)
                          setIsDeleteDialogOpen(true)
                        }}
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
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={(_, p) => onPageChange(p)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => onRowsPerPageChange(parseInt(e.target.value, 10))}
            rowsPerPageOptions={[10, 25, 50]}
            labelRowsPerPage="Filas por pagina"
          />
        </>
      )}

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Documento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRDocumentForm
              onSubmit={handleCreateDocument}
              restaurantId={currentRestaurant?.id || ''}
              onCancel={() => setIsAddDialogOpen(false)}
              isSubmitting={isSubmitting}
              persons={persons}
              permitPresets={permitPresets}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => { setIsEditDialogOpen(false); setSelectedDocument(null) }} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Documento</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedDocument && (
              <TRDocumentForm
                onSubmit={handleUpdateDocument}
                initialData={selectedDocument}
                restaurantId={currentRestaurant?.id || ''}
                onCancel={() => { setIsEditDialogOpen(false); setSelectedDocument(null) }}
                isSubmitting={isSubmitting}
                persons={persons}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => { setIsDeleteDialogOpen(false); setSelectedDocument(null) }}>
        <DialogTitle>Eliminar Documento</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Esta seguro que desea eliminar este documento?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setIsDeleteDialogOpen(false); setSelectedDocument(null) }} disabled={isSubmitting}>
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

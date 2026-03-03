import { useState, useEffect, useCallback } from 'react'
import { documentService } from '@/services/documentService'
import type { Document, DocumentCreate, DocumentUpdate, DocumentFilters } from '@/types/document'

interface UseDocumentsResult {
  documents: Document[]
  isLoading: boolean
  error: string | null
  filters: DocumentFilters
  fetchDocuments: () => Promise<void>
  createDocument: (data: DocumentCreate, file?: File) => Promise<void>
  updateDocument: (id: string, data: DocumentUpdate) => Promise<void>
  deleteDocument: (id: string) => Promise<void>
  setFilters: (filters: DocumentFilters) => void
}

export const useDocuments = (restaurantId: string | null): UseDocumentsResult => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<DocumentFilters>({})

  const fetchDocuments = useCallback(async () => {
    if (!restaurantId) {
      console.log('INFO [useDocuments]: No restaurantId provided, skipping fetch')
      return
    }

    console.log('INFO [useDocuments]: Fetching documents for restaurant:', restaurantId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await documentService.getAll(restaurantId, filters.type, filters.expiration_status)
      setDocuments(data)
      console.log('INFO [useDocuments]: Fetched', data.length, 'documents')
    } catch (err) {
      console.error('ERROR [useDocuments]: Failed to fetch documents:', err)
      setError('Error al cargar documentos. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [restaurantId, filters])

  const createDocument = useCallback(
    async (data: DocumentCreate, file?: File) => {
      console.log('INFO [useDocuments]: Creating document')
      setError(null)

      try {
        await documentService.create(data, file)
        console.log('INFO [useDocuments]: Document created, refreshing list')
        await fetchDocuments()
      } catch (err) {
        console.error('ERROR [useDocuments]: Failed to create document:', err)
        setError('Error al crear documento. Intente de nuevo.')
        throw err
      }
    },
    [fetchDocuments]
  )

  const updateDocument = useCallback(
    async (id: string, data: DocumentUpdate) => {
      if (!restaurantId) return
      console.log('INFO [useDocuments]: Updating document:', id)
      setError(null)

      try {
        await documentService.update(id, data)
        console.log('INFO [useDocuments]: Document updated, refreshing list')
        await fetchDocuments()
      } catch (err) {
        console.error('ERROR [useDocuments]: Failed to update document:', err)
        setError('Error al actualizar documento. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchDocuments]
  )

  const deleteDocument = useCallback(
    async (id: string) => {
      if (!restaurantId) return
      console.log('INFO [useDocuments]: Deleting document:', id)
      setError(null)

      try {
        await documentService.delete(id)
        console.log('INFO [useDocuments]: Document deleted, refreshing list')
        await fetchDocuments()
      } catch (err) {
        console.error('ERROR [useDocuments]: Failed to delete document:', err)
        setError('Error al eliminar documento. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchDocuments]
  )

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  return {
    documents,
    isLoading,
    error,
    filters,
    fetchDocuments,
    createDocument,
    updateDocument,
    deleteDocument,
    setFilters,
  }
}

export default useDocuments

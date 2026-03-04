import { apiClient } from '@/api/clients'
import type { Document, DocumentCreate, DocumentUpdate, PermitPreset } from '@/types/document'

/**
 * Document service for CRUD operations on restaurant documents.
 */
export const documentService = {
  /**
   * Get available permit type presets with their alert schedules.
   * @returns List of permit presets
   */
  async getPermitPresets(): Promise<PermitPreset[]> {
    console.log('INFO [DocumentService]: Fetching permit presets')
    try {
      const response = await apiClient.get<PermitPreset[]>('/documents/permit-presets')
      console.log('INFO [DocumentService]: Permit presets fetched:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [DocumentService]: Failed to fetch permit presets:', error)
      throw error
    }
  },

  /**
   * Get all documents for a restaurant, with optional type and expiration status filters.
   * @param restaurantId - Restaurant UUID
   * @param type - Optional document type filter
   * @param expirationStatus - Optional expiration status filter
   * @returns List of documents
   */
  async getAll(restaurantId: string, type?: string, expirationStatus?: string): Promise<Document[]> {
    console.log('INFO [DocumentService]: Fetching documents for restaurant:', restaurantId)
    try {
      const params: Record<string, string> = { restaurant_id: restaurantId }
      if (type) {
        params.type = type
      }
      if (expirationStatus) {
        params.expiration_status = expirationStatus
      }
      const response = await apiClient.get<Document[]>('/documents', { params })
      console.log('INFO [DocumentService]: Documents fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [DocumentService]: Failed to fetch documents:', error)
      throw error
    }
  },

  /**
   * Create a new document with optional file upload.
   * Uses multipart/form-data for file support.
   * @param data - Document creation data
   * @param file - Optional file to upload
   * @returns Created document
   */
  async create(data: DocumentCreate, file?: File): Promise<Document> {
    console.log('INFO [DocumentService]: Creating document type:', data.type)
    try {
      const formData = new FormData()
      formData.append('restaurant_id', data.restaurant_id)
      formData.append('type', data.type)
      if (data.issue_date) {
        formData.append('issue_date', data.issue_date)
      }
      if (data.expiration_date) {
        formData.append('expiration_date', data.expiration_date)
      }
      if (data.person_id) {
        formData.append('person_id', data.person_id)
      }
      if (data.description) {
        formData.append('description', data.description)
      }
      if (data.custom_alert_windows && data.custom_alert_windows.length > 0) {
        formData.append('custom_alert_windows', JSON.stringify(data.custom_alert_windows))
      }
      if (file) {
        formData.append('file', file)
      }

      const response = await apiClient.post<Document>('/documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      console.log('INFO [DocumentService]: Document created:', response.data.type)
      return response.data
    } catch (error) {
      console.error('ERROR [DocumentService]: Failed to create document:', error)
      throw error
    }
  },

  /**
   * Update an existing document (JSON body, no file upload).
   * @param id - Document UUID
   * @param data - Document update data
   * @returns Updated document
   */
  async update(id: string, data: DocumentUpdate): Promise<Document> {
    console.log('INFO [DocumentService]: Updating document:', id)
    try {
      const response = await apiClient.put<Document>(`/documents/${id}`, data)
      console.log('INFO [DocumentService]: Document updated:', response.data.type)
      return response.data
    } catch (error) {
      console.error('ERROR [DocumentService]: Failed to update document:', error)
      throw error
    }
  },

  /**
   * Delete a document.
   * @param id - Document UUID
   */
  async delete(id: string): Promise<void> {
    console.log('INFO [DocumentService]: Deleting document:', id)
    try {
      await apiClient.delete(`/documents/${id}`)
      console.log('INFO [DocumentService]: Document deleted:', id)
    } catch (error) {
      console.error('ERROR [DocumentService]: Failed to delete document:', error)
      throw error
    }
  },
}

export default documentService

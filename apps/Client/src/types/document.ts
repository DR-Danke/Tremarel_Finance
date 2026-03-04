/**
 * Document types for RestaurantOS document management.
 * Matches backend DocumentResponseDTO, DocumentCreateDTO, DocumentUpdateDTO.
 */

export type DocumentType =
  | 'contrato'
  | 'permiso'
  | 'factura'
  | 'licencia'
  | 'factura_proveedor'
  | 'certificado'
  | 'manipulacion_alimentos'
  | 'bomberos'
  | 'camara_comercio'
  | 'extintor'
  | 'sanidad'
  | 'otro'

export type ExpirationStatus = 'valid' | 'expiring_soon' | 'expired'

export const DOCUMENT_TYPES: { value: DocumentType; label: string }[] = [
  { value: 'contrato', label: 'Contrato' },
  { value: 'permiso', label: 'Permiso' },
  { value: 'factura', label: 'Factura' },
  { value: 'licencia', label: 'Licencia' },
  { value: 'factura_proveedor', label: 'Factura Proveedor' },
  { value: 'certificado', label: 'Certificado' },
  { value: 'manipulacion_alimentos', label: 'Certificado de Manipulación de Alimentos' },
  { value: 'bomberos', label: 'Permiso de Bomberos' },
  { value: 'camara_comercio', label: 'Registro de Cámara de Comercio' },
  { value: 'extintor', label: 'Servicio de Extintores' },
  { value: 'sanidad', label: 'Certificado de Inspección Sanitaria' },
  { value: 'otro', label: 'Otro' },
]

export const EXPIRATION_STATUS_OPTIONS: { value: ExpirationStatus; label: string }[] = [
  { value: 'valid', label: 'Vigente' },
  { value: 'expiring_soon', label: 'Por Vencer' },
  { value: 'expired', label: 'Vencido' },
]

export interface Document {
  id: string
  restaurant_id: string
  type: string
  file_url: string | null
  issue_date: string | null
  expiration_date: string | null
  person_id: string | null
  description: string | null
  expiration_status: ExpirationStatus
  created_at: string
  updated_at: string | null
}

export interface DocumentCreate {
  restaurant_id: string
  type: DocumentType
  issue_date?: string
  expiration_date?: string
  person_id?: string
  description?: string
  custom_alert_windows?: number[]
}

export interface PermitPreset {
  type_key: string
  name: string
  alert_windows: number[]
  notification_channel: string
}

export interface DocumentUpdate {
  type?: DocumentType
  issue_date?: string
  expiration_date?: string
  person_id?: string
  description?: string
}

export interface DocumentFilters {
  type?: DocumentType
  expiration_status?: ExpirationStatus
}

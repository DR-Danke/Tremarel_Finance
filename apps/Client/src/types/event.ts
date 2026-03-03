/**
 * Event types for RestaurantOS event/task management.
 * Matches backend EventResponseDTO, EventCreateDTO, EventUpdateDTO, EventStatusUpdateDTO.
 */

export type EventType = 'tarea' | 'vencimiento' | 'pago' | 'turno' | 'checklist' | 'alerta_stock' | 'alerta_rentabilidad'

export type EventFrequency = 'none' | 'daily' | 'weekly' | 'monthly' | 'yearly'

export type EventStatus = 'pending' | 'completed' | 'overdue'

export interface Event {
  id: string
  restaurant_id: string
  type: EventType
  description: string | null
  date: string
  frequency: EventFrequency
  responsible_id: string | null
  notification_channel: string
  status: EventStatus
  related_document_id: string | null
  parent_event_id: string | null
  completed_at: string | null
  is_overdue: boolean
  created_at: string
  updated_at: string | null
}

export interface EventCreate {
  restaurant_id: string
  type: EventType
  date: string
  description?: string
  frequency?: EventFrequency
  responsible_id?: string
  notification_channel?: string
  related_document_id?: string
}

export interface EventUpdate {
  type?: EventType
  description?: string
  date?: string
  frequency?: EventFrequency
  responsible_id?: string
  notification_channel?: string
  related_document_id?: string
}

export interface EventStatusUpdate {
  status: EventStatus
}

export interface EventFilters {
  type?: EventType
  status?: EventStatus
  responsible_id?: string
  date_from?: string
  date_to?: string
}

export const EVENT_TYPE_OPTIONS = [
  { value: 'tarea', label: 'Tarea' },
  { value: 'vencimiento', label: 'Vencimiento' },
  { value: 'pago', label: 'Pago' },
  { value: 'turno', label: 'Turno' },
  { value: 'checklist', label: 'Checklist' },
] as const

export const EVENT_FREQUENCY_OPTIONS = [
  { value: 'none', label: 'Sin repetición' },
  { value: 'daily', label: 'Diario' },
  { value: 'weekly', label: 'Semanal' },
  { value: 'monthly', label: 'Mensual' },
  { value: 'yearly', label: 'Anual' },
] as const

export const EVENT_STATUS_OPTIONS = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'completed', label: 'Completado' },
  { value: 'overdue', label: 'Vencido' },
] as const

export const NOTIFICATION_CHANNEL_OPTIONS = [
  { value: 'email', label: 'Email' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'push', label: 'Push' },
] as const

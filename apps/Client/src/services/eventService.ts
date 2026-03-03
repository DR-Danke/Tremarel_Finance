import { apiClient } from '@/api/clients'
import type { Event, EventCreate, EventUpdate, EventStatusUpdate, EventFilters } from '@/types/event'

/**
 * Event service for CRUD operations on restaurant events and tasks.
 */
export const eventService = {
  /**
   * Get all events for a restaurant, with optional filters.
   * @param restaurantId - Restaurant UUID
   * @param filters - Optional event filters
   * @returns List of events
   */
  async getAll(restaurantId: string, filters?: EventFilters): Promise<Event[]> {
    console.log('INFO [EventService]: Fetching events for restaurant:', restaurantId)
    try {
      const params: Record<string, string> = { restaurant_id: restaurantId }
      if (filters?.type) {
        params.type = filters.type
      }
      if (filters?.status) {
        params.status = filters.status
      }
      if (filters?.responsible_id) {
        params.responsible_id = filters.responsible_id
      }
      if (filters?.date_from) {
        params.date_from = filters.date_from
      }
      if (filters?.date_to) {
        params.date_to = filters.date_to
      }
      const response = await apiClient.get<Event[]>('/events', { params })
      console.log('INFO [EventService]: Events fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [EventService]: Failed to fetch events:', error)
      throw error
    }
  },

  /**
   * Create a new event.
   * @param data - Event creation data
   * @returns Created event
   */
  async create(data: EventCreate): Promise<Event> {
    console.log('INFO [EventService]: Creating event:', data.type)
    try {
      const response = await apiClient.post<Event>('/events', data)
      console.log('INFO [EventService]: Event created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [EventService]: Failed to create event:', error)
      throw error
    }
  },

  /**
   * Update an existing event.
   * @param id - Event UUID
   * @param data - Event update data
   * @returns Updated event
   */
  async update(id: string, data: EventUpdate): Promise<Event> {
    console.log('INFO [EventService]: Updating event:', id)
    try {
      const response = await apiClient.put<Event>(`/events/${id}`, data)
      console.log('INFO [EventService]: Event updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [EventService]: Failed to update event:', error)
      throw error
    }
  },

  /**
   * Update an event's status.
   * @param id - Event UUID
   * @param data - Status update data
   * @returns Updated event
   */
  async updateStatus(id: string, data: EventStatusUpdate): Promise<Event> {
    console.log('INFO [EventService]: Updating event status:', id, data.status)
    try {
      const response = await apiClient.patch<Event>(`/events/${id}/status`, data)
      console.log('INFO [EventService]: Event status updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [EventService]: Failed to update event status:', error)
      throw error
    }
  },

  /**
   * Delete an event.
   * @param id - Event UUID
   */
  async delete(id: string): Promise<void> {
    console.log('INFO [EventService]: Deleting event:', id)
    try {
      await apiClient.delete(`/events/${id}`)
      console.log('INFO [EventService]: Event deleted:', id)
    } catch (error) {
      console.error('ERROR [EventService]: Failed to delete event:', error)
      throw error
    }
  },
}

export default eventService

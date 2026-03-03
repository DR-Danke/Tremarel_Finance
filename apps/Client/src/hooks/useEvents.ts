import { useState, useEffect, useCallback } from 'react'
import { eventService } from '@/services/eventService'
import type { Event, EventCreate, EventUpdate, EventStatus, EventFilters } from '@/types/event'

interface UseEventsResult {
  events: Event[]
  isLoading: boolean
  error: string | null
  filters: EventFilters
  fetchEvents: () => Promise<void>
  createEvent: (data: EventCreate) => Promise<void>
  updateEvent: (id: string, data: EventUpdate) => Promise<void>
  updateEventStatus: (id: string, status: EventStatus) => Promise<void>
  deleteEvent: (id: string) => Promise<void>
  setFilters: (filters: EventFilters) => void
}

export const useEvents = (restaurantId: string | null): UseEventsResult => {
  const [events, setEvents] = useState<Event[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<EventFilters>({})

  const fetchEvents = useCallback(async () => {
    if (!restaurantId) {
      console.log('INFO [useEvents]: No restaurantId provided, skipping fetch')
      return
    }

    console.log('INFO [useEvents]: Fetching events for restaurant:', restaurantId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await eventService.getAll(restaurantId, filters)
      setEvents(data)
      console.log('INFO [useEvents]: Fetched', data.length, 'events')
    } catch (err) {
      console.error('ERROR [useEvents]: Failed to fetch events:', err)
      setError('Error al cargar eventos. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [restaurantId, filters])

  const createEvent = useCallback(
    async (data: EventCreate) => {
      console.log('INFO [useEvents]: Creating event')
      setError(null)

      try {
        await eventService.create(data)
        console.log('INFO [useEvents]: Event created, refreshing list')
        await fetchEvents()
      } catch (err) {
        console.error('ERROR [useEvents]: Failed to create event:', err)
        setError('Error al crear evento. Intente de nuevo.')
        throw err
      }
    },
    [fetchEvents]
  )

  const updateEvent = useCallback(
    async (id: string, data: EventUpdate) => {
      if (!restaurantId) return
      console.log('INFO [useEvents]: Updating event:', id)
      setError(null)

      try {
        await eventService.update(id, data)
        console.log('INFO [useEvents]: Event updated, refreshing list')
        await fetchEvents()
      } catch (err) {
        console.error('ERROR [useEvents]: Failed to update event:', err)
        setError('Error al actualizar evento. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchEvents]
  )

  const updateEventStatus = useCallback(
    async (id: string, status: EventStatus) => {
      if (!restaurantId) return
      console.log('INFO [useEvents]: Updating event status:', id, status)
      setError(null)

      try {
        await eventService.updateStatus(id, { status })
        console.log('INFO [useEvents]: Event status updated, refreshing list')
        await fetchEvents()
      } catch (err) {
        console.error('ERROR [useEvents]: Failed to update event status:', err)
        setError('Error al actualizar estado del evento. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchEvents]
  )

  const deleteEvent = useCallback(
    async (id: string) => {
      if (!restaurantId) return
      console.log('INFO [useEvents]: Deleting event:', id)
      setError(null)

      try {
        await eventService.delete(id)
        console.log('INFO [useEvents]: Event deleted, refreshing list')
        await fetchEvents()
      } catch (err) {
        console.error('ERROR [useEvents]: Failed to delete event:', err)
        setError('Error al eliminar evento. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchEvents]
  )

  useEffect(() => {
    fetchEvents()
  }, [fetchEvents])

  return {
    events,
    isLoading,
    error,
    filters,
    fetchEvents,
    createEvent,
    updateEvent,
    updateEventStatus,
    deleteEvent,
    setFilters,
  }
}

export default useEvents

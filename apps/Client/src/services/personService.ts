import { apiClient } from '@/api/clients'
import type { Person, PersonType, PersonCreate, PersonUpdate } from '@/types/person'

/**
 * Person service for CRUD operations on restaurant persons.
 */
export const personService = {
  /**
   * Get all persons for a restaurant, with optional type filter.
   * @param restaurantId - Restaurant UUID
   * @param type - Optional person type filter
   * @returns List of persons
   */
  async getAll(restaurantId: string, type?: PersonType): Promise<Person[]> {
    console.log('INFO [PersonService]: Fetching persons for restaurant:', restaurantId)
    try {
      const params: Record<string, string> = { restaurant_id: restaurantId }
      if (type) {
        params.type = type
      }
      const response = await apiClient.get<Person[]>('/persons', { params })
      console.log('INFO [PersonService]: Persons fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [PersonService]: Failed to fetch persons:', error)
      throw error
    }
  },

  /**
   * Create a new person.
   * @param data - Person creation data
   * @returns Created person
   */
  async create(data: PersonCreate): Promise<Person> {
    console.log('INFO [PersonService]: Creating person:', data.name)
    try {
      const response = await apiClient.post<Person>('/persons', data)
      console.log('INFO [PersonService]: Person created:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [PersonService]: Failed to create person:', error)
      throw error
    }
  },

  /**
   * Update an existing person.
   * @param id - Person UUID
   * @param data - Person update data
   * @returns Updated person
   */
  async update(id: string, data: PersonUpdate): Promise<Person> {
    console.log('INFO [PersonService]: Updating person:', id)
    try {
      const response = await apiClient.put<Person>(`/persons/${id}`, data)
      console.log('INFO [PersonService]: Person updated:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [PersonService]: Failed to update person:', error)
      throw error
    }
  },

  /**
   * Delete a person.
   * @param id - Person UUID
   */
  async delete(id: string): Promise<void> {
    console.log('INFO [PersonService]: Deleting person:', id)
    try {
      await apiClient.delete(`/persons/${id}`)
      console.log('INFO [PersonService]: Person deleted:', id)
    } catch (error) {
      console.error('ERROR [PersonService]: Failed to delete person:', error)
      throw error
    }
  },
}

export default personService

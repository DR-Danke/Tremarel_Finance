import { apiClient } from '@/api/clients'
import type { Restaurant, CreateRestaurantData, UpdateRestaurantData } from '@/types/restaurant'

/**
 * Restaurant service for CRUD operations on restaurants.
 */
export const restaurantService = {
  /**
   * Get all restaurants the current user belongs to.
   * @returns List of restaurants
   */
  async getRestaurants(): Promise<Restaurant[]> {
    console.log('INFO [RestaurantService]: Fetching restaurants')
    try {
      const response = await apiClient.get<Restaurant[]>('/restaurants')
      console.log('INFO [RestaurantService]: Restaurants fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [RestaurantService]: Failed to fetch restaurants:', error)
      throw error
    }
  },

  /**
   * Get a specific restaurant by ID.
   * @param id - Restaurant ID
   * @returns Restaurant data
   */
  async getRestaurant(id: string): Promise<Restaurant> {
    console.log('INFO [RestaurantService]: Fetching restaurant:', id)
    try {
      const response = await apiClient.get<Restaurant>(`/restaurants/${id}`)
      console.log('INFO [RestaurantService]: Restaurant fetched:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [RestaurantService]: Failed to fetch restaurant:', error)
      throw error
    }
  },

  /**
   * Create a new restaurant.
   * @param data - Restaurant creation data
   * @returns Created restaurant
   */
  async createRestaurant(data: CreateRestaurantData): Promise<Restaurant> {
    console.log('INFO [RestaurantService]: Creating restaurant:', data.name)
    try {
      const response = await apiClient.post<Restaurant>('/restaurants', data)
      console.log('INFO [RestaurantService]: Restaurant created:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [RestaurantService]: Failed to create restaurant:', error)
      throw error
    }
  },

  /**
   * Update an existing restaurant.
   * @param id - Restaurant ID
   * @param data - Restaurant update data
   * @returns Updated restaurant
   */
  async updateRestaurant(id: string, data: UpdateRestaurantData): Promise<Restaurant> {
    console.log('INFO [RestaurantService]: Updating restaurant:', id)
    try {
      const response = await apiClient.put<Restaurant>(`/restaurants/${id}`, data)
      console.log('INFO [RestaurantService]: Restaurant updated:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [RestaurantService]: Failed to update restaurant:', error)
      throw error
    }
  },

  /**
   * Delete a restaurant.
   * @param id - Restaurant ID
   */
  async deleteRestaurant(id: string): Promise<void> {
    console.log('INFO [RestaurantService]: Deleting restaurant:', id)
    try {
      await apiClient.delete(`/restaurants/${id}`)
      console.log('INFO [RestaurantService]: Restaurant deleted:', id)
    } catch (error) {
      console.error('ERROR [RestaurantService]: Failed to delete restaurant:', error)
      throw error
    }
  },
}

export default restaurantService

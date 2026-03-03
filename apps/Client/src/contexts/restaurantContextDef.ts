import { createContext } from 'react'
import type { Restaurant, CreateRestaurantData, UpdateRestaurantData } from '@/types/restaurant'

export interface RestaurantContextType {
  restaurants: Restaurant[]
  currentRestaurant: Restaurant | null
  isLoading: boolean
  switchRestaurant: (restaurantId: string) => void
  createRestaurant: (data: CreateRestaurantData) => Promise<Restaurant>
  updateRestaurant: (id: string, data: UpdateRestaurantData) => Promise<Restaurant>
  deleteRestaurant: (id: string) => Promise<void>
  refreshRestaurants: () => Promise<void>
}

export const RestaurantContext = createContext<RestaurantContextType | undefined>(undefined)

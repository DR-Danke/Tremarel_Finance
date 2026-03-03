import React, { useState, useEffect, useCallback, useMemo } from 'react'
import type { Restaurant, CreateRestaurantData, UpdateRestaurantData } from '@/types/restaurant'
import { restaurantService } from '@/services/restaurantService'
import { RestaurantContext, type RestaurantContextType } from './restaurantContextDef'
import { useAuth } from '@/hooks/useAuth'

const RESTAURANT_KEY = 'currentRestaurantId'

interface RestaurantProviderProps {
  children: React.ReactNode
}

export const RestaurantProvider: React.FC<RestaurantProviderProps> = ({ children }) => {
  const { isAuthenticated } = useAuth()
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [currentRestaurant, setCurrentRestaurant] = useState<Restaurant | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Fetch restaurants when user is authenticated
  useEffect(() => {
    const fetchRestaurants = async () => {
      if (!isAuthenticated) {
        console.log('INFO [RestaurantContext]: User not authenticated, clearing restaurants')
        setRestaurants([])
        setCurrentRestaurant(null)
        setIsLoading(false)
        return
      }

      console.log('INFO [RestaurantContext]: Fetching restaurants for user')
      setIsLoading(true)

      try {
        const userRestaurants = await restaurantService.getRestaurants()
        setRestaurants(userRestaurants)
        console.log('INFO [RestaurantContext]: Restaurants loaded successfully:', userRestaurants.length)

        // Restore current restaurant from localStorage or select first
        const storedRestaurantId = localStorage.getItem(RESTAURANT_KEY)
        if (storedRestaurantId) {
          const storedRestaurant = userRestaurants.find((r) => r.id === storedRestaurantId)
          if (storedRestaurant) {
            setCurrentRestaurant(storedRestaurant)
            console.log('INFO [RestaurantContext]: Restored restaurant from storage:', storedRestaurant.name)
          } else if (userRestaurants.length > 0) {
            setCurrentRestaurant(userRestaurants[0])
            localStorage.setItem(RESTAURANT_KEY, userRestaurants[0].id)
            console.log('INFO [RestaurantContext]: Stored restaurant not found, selecting first:', userRestaurants[0].name)
          }
        } else if (userRestaurants.length > 0) {
          setCurrentRestaurant(userRestaurants[0])
          localStorage.setItem(RESTAURANT_KEY, userRestaurants[0].id)
          console.log('INFO [RestaurantContext]: No stored restaurant, selecting first:', userRestaurants[0].name)
        }
      } catch (error) {
        console.error('ERROR [RestaurantContext]: Failed to fetch restaurants:', error)
        setRestaurants([])
        setCurrentRestaurant(null)
      } finally {
        setIsLoading(false)
      }
    }

    fetchRestaurants()
  }, [isAuthenticated])

  const switchRestaurant = useCallback(
    (restaurantId: string) => {
      console.log('INFO [RestaurantContext]: Switching to restaurant:', restaurantId)
      const restaurant = restaurants.find((r) => r.id === restaurantId)
      if (restaurant) {
        setCurrentRestaurant(restaurant)
        localStorage.setItem(RESTAURANT_KEY, restaurantId)
        console.log('INFO [RestaurantContext]: Switched to restaurant:', restaurant.name)
      } else {
        console.error('ERROR [RestaurantContext]: Restaurant not found:', restaurantId)
      }
    },
    [restaurants]
  )

  const createRestaurant = useCallback(async (data: CreateRestaurantData): Promise<Restaurant> => {
    console.log('INFO [RestaurantContext]: Creating restaurant:', data.name)
    const newRestaurant = await restaurantService.createRestaurant(data)
    setRestaurants((prev) => [...prev, newRestaurant])

    // Set as current restaurant if it's the first one
    if (restaurants.length === 0) {
      setCurrentRestaurant(newRestaurant)
      localStorage.setItem(RESTAURANT_KEY, newRestaurant.id)
      console.log('INFO [RestaurantContext]: Set new restaurant as current:', newRestaurant.name)
    }

    console.log('INFO [RestaurantContext]: Restaurant created:', newRestaurant.name)
    return newRestaurant
  }, [restaurants.length])

  const updateRestaurant = useCallback(
    async (id: string, data: UpdateRestaurantData): Promise<Restaurant> => {
      console.log('INFO [RestaurantContext]: Updating restaurant:', id)
      const updatedRestaurant = await restaurantService.updateRestaurant(id, data)
      setRestaurants((prev) => prev.map((r) => (r.id === id ? updatedRestaurant : r)))

      // Update current restaurant if it was the one updated
      if (currentRestaurant?.id === id) {
        setCurrentRestaurant(updatedRestaurant)
      }

      console.log('INFO [RestaurantContext]: Restaurant updated:', updatedRestaurant.name)
      return updatedRestaurant
    },
    [currentRestaurant?.id]
  )

  const deleteRestaurant = useCallback(
    async (id: string): Promise<void> => {
      console.log('INFO [RestaurantContext]: Deleting restaurant:', id)
      await restaurantService.deleteRestaurant(id)
      setRestaurants((prev) => prev.filter((r) => r.id !== id))

      // If deleted restaurant was current, switch to first remaining
      if (currentRestaurant?.id === id) {
        const remaining = restaurants.filter((r) => r.id !== id)
        if (remaining.length > 0) {
          setCurrentRestaurant(remaining[0])
          localStorage.setItem(RESTAURANT_KEY, remaining[0].id)
          console.log('INFO [RestaurantContext]: Switched to restaurant after deletion:', remaining[0].name)
        } else {
          setCurrentRestaurant(null)
          localStorage.removeItem(RESTAURANT_KEY)
          console.log('INFO [RestaurantContext]: No restaurants remaining after deletion')
        }
      }

      console.log('INFO [RestaurantContext]: Restaurant deleted:', id)
    },
    [currentRestaurant?.id, restaurants]
  )

  const refreshRestaurants = useCallback(async (): Promise<void> => {
    console.log('INFO [RestaurantContext]: Refreshing restaurants')
    setIsLoading(true)
    try {
      const userRestaurants = await restaurantService.getRestaurants()
      setRestaurants(userRestaurants)

      // Update current restaurant reference if it still exists
      if (currentRestaurant) {
        const updated = userRestaurants.find((r) => r.id === currentRestaurant.id)
        if (updated) {
          setCurrentRestaurant(updated)
        } else if (userRestaurants.length > 0) {
          setCurrentRestaurant(userRestaurants[0])
          localStorage.setItem(RESTAURANT_KEY, userRestaurants[0].id)
        } else {
          setCurrentRestaurant(null)
          localStorage.removeItem(RESTAURANT_KEY)
        }
      }

      console.log('INFO [RestaurantContext]: Restaurants refreshed:', userRestaurants.length)
    } catch (error) {
      console.error('ERROR [RestaurantContext]: Failed to refresh restaurants:', error)
    } finally {
      setIsLoading(false)
    }
  }, [currentRestaurant])

  const value = useMemo<RestaurantContextType>(
    () => ({
      restaurants,
      currentRestaurant,
      isLoading,
      switchRestaurant,
      createRestaurant,
      updateRestaurant,
      deleteRestaurant,
      refreshRestaurants,
    }),
    [restaurants, currentRestaurant, isLoading, switchRestaurant, createRestaurant, updateRestaurant, deleteRestaurant, refreshRestaurants]
  )

  return <RestaurantContext.Provider value={value}>{children}</RestaurantContext.Provider>
}

export default RestaurantProvider

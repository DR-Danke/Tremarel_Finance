import { useContext } from 'react'
import { RestaurantContext, type RestaurantContextType } from '@/contexts/restaurantContextDef'

/**
 * Custom hook for accessing restaurant context.
 * @throws Error if used outside of RestaurantProvider
 * @returns RestaurantContextType with restaurants, currentRestaurant, isLoading, and CRUD operations
 */
export const useRestaurant = (): RestaurantContextType => {
  const context = useContext(RestaurantContext)

  if (context === undefined) {
    throw new Error('useRestaurant must be used within a RestaurantProvider')
  }

  return context
}

export default useRestaurant

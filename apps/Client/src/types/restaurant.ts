// Restaurant interface matching backend RestaurantResponseDTO
export interface Restaurant {
  id: string
  name: string
  address?: string | null
  owner_id?: string | null
  created_at: string
  updated_at?: string | null
}

// Data for creating a new restaurant
export interface CreateRestaurantData {
  name: string
  address?: string
}

// Data for updating a restaurant
export interface UpdateRestaurantData {
  name?: string
  address?: string
}

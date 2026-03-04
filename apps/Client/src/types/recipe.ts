/**
 * Recipe and RecipeItem types for RestaurantOS recipe management.
 * Matches backend RecipeResponseDTO, RecipeCreateDTO, RecipeUpdateDTO,
 * RecipeItemResponseDTO, RecipeItemCreateDTO, RecipeProduceResponseDTO.
 */

export interface RecipeItem {
  id?: string
  resource_id: string
  resource_name?: string
  quantity: number
  unit: string
  item_cost?: number
  created_at?: string
}

export interface Recipe {
  id: string
  restaurant_id: string
  name: string
  sale_price: number
  current_cost: number
  margin_percent: number
  is_profitable: boolean
  is_active: boolean
  items: RecipeItem[]
  created_at: string
  updated_at: string | null
}

export interface RecipeCreate {
  restaurant_id: string
  name: string
  sale_price: number
  is_active?: boolean
  items: { resource_id: string; quantity: number; unit: string }[]
}

export interface RecipeUpdate {
  name?: string
  sale_price?: number
  is_active?: boolean
  items?: { resource_id: string; quantity: number; unit: string }[]
}

export interface RecipeProduceResponse {
  recipe_id: string
  recipe_name: string
  quantity: number
  movements_created: number
}

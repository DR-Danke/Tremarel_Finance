import { apiClient } from '@/api/clients'
import type { Recipe, RecipeCreate, RecipeUpdate, RecipeProduceResponse } from '@/types/recipe'

/**
 * Recipe service for CRUD and production operations on restaurant recipes.
 */
export const recipeService = {
  /**
   * Get all recipes for a restaurant.
   * @param restaurantId - Restaurant UUID
   * @returns List of recipes
   */
  async getAll(restaurantId: string): Promise<Recipe[]> {
    console.log('INFO [RecipeService]: Fetching recipes for restaurant:', restaurantId)
    try {
      const response = await apiClient.get<Recipe[]>('/recipes', {
        params: { restaurant_id: restaurantId },
      })
      console.log('INFO [RecipeService]: Recipes fetched successfully:', response.data.length)
      return response.data
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to fetch recipes:', error)
      throw error
    }
  },

  /**
   * Get a specific recipe by ID.
   * @param recipeId - Recipe UUID
   * @returns Recipe
   */
  async getById(recipeId: string): Promise<Recipe> {
    console.log('INFO [RecipeService]: Fetching recipe:', recipeId)
    try {
      const response = await apiClient.get<Recipe>(`/recipes/${recipeId}`)
      console.log('INFO [RecipeService]: Recipe fetched:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to fetch recipe:', error)
      throw error
    }
  },

  /**
   * Create a new recipe.
   * @param data - Recipe creation data
   * @returns Created recipe
   */
  async create(data: RecipeCreate): Promise<Recipe> {
    console.log('INFO [RecipeService]: Creating recipe:', data.name)
    try {
      const response = await apiClient.post<Recipe>('/recipes', data)
      console.log('INFO [RecipeService]: Recipe created:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to create recipe:', error)
      throw error
    }
  },

  /**
   * Update an existing recipe.
   * @param id - Recipe UUID
   * @param data - Recipe update data
   * @returns Updated recipe
   */
  async update(id: string, data: RecipeUpdate): Promise<Recipe> {
    console.log('INFO [RecipeService]: Updating recipe:', id)
    try {
      const response = await apiClient.put<Recipe>(`/recipes/${id}`, data)
      console.log('INFO [RecipeService]: Recipe updated:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to update recipe:', error)
      throw error
    }
  },

  /**
   * Delete a recipe.
   * @param id - Recipe UUID
   */
  async delete(id: string): Promise<void> {
    console.log('INFO [RecipeService]: Deleting recipe:', id)
    try {
      await apiClient.delete(`/recipes/${id}`)
      console.log('INFO [RecipeService]: Recipe deleted:', id)
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to delete recipe:', error)
      throw error
    }
  },

  /**
   * Produce a recipe (deduct ingredients from inventory).
   * @param recipeId - Recipe UUID
   * @param quantity - Number of portions to produce
   * @returns Production response with movements created
   */
  async produce(recipeId: string, quantity: number): Promise<RecipeProduceResponse> {
    console.log('INFO [RecipeService]: Producing recipe:', recipeId, 'quantity:', quantity)
    try {
      const response = await apiClient.post<RecipeProduceResponse>(
        `/recipes/${recipeId}/produce`,
        { quantity }
      )
      console.log('INFO [RecipeService]: Recipe produced:', response.data.recipe_name)
      return response.data
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to produce recipe:', error)
      throw error
    }
  },

  /**
   * Force cost recalculation for a recipe.
   * @param recipeId - Recipe UUID
   * @returns Updated cost info
   */
  async recalculate(recipeId: string): Promise<Recipe> {
    console.log('INFO [RecipeService]: Recalculating recipe cost:', recipeId)
    try {
      const response = await apiClient.post<Recipe>(`/recipes/${recipeId}/recalculate`)
      console.log('INFO [RecipeService]: Recipe cost recalculated:', recipeId)
      return response.data
    } catch (error) {
      console.error('ERROR [RecipeService]: Failed to recalculate recipe cost:', error)
      throw error
    }
  },
}

export default recipeService

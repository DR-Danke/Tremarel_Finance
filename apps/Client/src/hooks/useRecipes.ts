import { useState, useEffect, useCallback } from 'react'
import { recipeService } from '@/services/recipeService'
import type { Recipe, RecipeCreate, RecipeUpdate, RecipeProduceResponse } from '@/types/recipe'

interface UseRecipesResult {
  recipes: Recipe[]
  isLoading: boolean
  error: string | null
  fetchRecipes: () => Promise<void>
  createRecipe: (data: RecipeCreate) => Promise<void>
  updateRecipe: (id: string, data: RecipeUpdate) => Promise<void>
  deleteRecipe: (id: string) => Promise<void>
  produceRecipe: (recipeId: string, quantity: number) => Promise<RecipeProduceResponse>
}

export const useRecipes = (restaurantId: string | null): UseRecipesResult => {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchRecipes = useCallback(async () => {
    if (!restaurantId) {
      console.log('INFO [useRecipes]: No restaurantId provided, skipping fetch')
      return
    }

    console.log('INFO [useRecipes]: Fetching recipes for restaurant:', restaurantId)
    setIsLoading(true)
    setError(null)

    try {
      const data = await recipeService.getAll(restaurantId)
      setRecipes(data)
      console.log('INFO [useRecipes]: Fetched', data.length, 'recipes')
    } catch (err) {
      console.error('ERROR [useRecipes]: Failed to fetch recipes:', err)
      setError('Error al cargar recetas. Intente de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }, [restaurantId])

  const createRecipe = useCallback(
    async (data: RecipeCreate) => {
      console.log('INFO [useRecipes]: Creating recipe')
      setError(null)

      try {
        await recipeService.create(data)
        console.log('INFO [useRecipes]: Recipe created, refreshing list')
        await fetchRecipes()
      } catch (err) {
        console.error('ERROR [useRecipes]: Failed to create recipe:', err)
        setError('Error al crear receta. Intente de nuevo.')
        throw err
      }
    },
    [fetchRecipes]
  )

  const updateRecipe = useCallback(
    async (id: string, data: RecipeUpdate) => {
      if (!restaurantId) return
      console.log('INFO [useRecipes]: Updating recipe:', id)
      setError(null)

      try {
        await recipeService.update(id, data)
        console.log('INFO [useRecipes]: Recipe updated, refreshing list')
        await fetchRecipes()
      } catch (err) {
        console.error('ERROR [useRecipes]: Failed to update recipe:', err)
        setError('Error al actualizar receta. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchRecipes]
  )

  const deleteRecipe = useCallback(
    async (id: string) => {
      if (!restaurantId) return
      console.log('INFO [useRecipes]: Deleting recipe:', id)
      setError(null)

      try {
        await recipeService.delete(id)
        console.log('INFO [useRecipes]: Recipe deleted, refreshing list')
        await fetchRecipes()
      } catch (err) {
        console.error('ERROR [useRecipes]: Failed to delete recipe:', err)
        setError('Error al eliminar receta. Intente de nuevo.')
        throw err
      }
    },
    [restaurantId, fetchRecipes]
  )

  const produceRecipe = useCallback(
    async (recipeId: string, quantity: number): Promise<RecipeProduceResponse> => {
      console.log('INFO [useRecipes]: Producing recipe:', recipeId, 'quantity:', quantity)
      setError(null)

      try {
        const result = await recipeService.produce(recipeId, quantity)
        console.log('INFO [useRecipes]: Recipe produced, refreshing list')
        await fetchRecipes()
        return result
      } catch (err) {
        console.error('ERROR [useRecipes]: Failed to produce recipe:', err)
        setError('Error al producir receta. Intente de nuevo.')
        throw err
      }
    },
    [fetchRecipes]
  )

  useEffect(() => {
    fetchRecipes()
  }, [fetchRecipes])

  return {
    recipes,
    isLoading,
    error,
    fetchRecipes,
    createRecipe,
    updateRecipe,
    deleteRecipe,
    produceRecipe,
  }
}

export default useRecipes

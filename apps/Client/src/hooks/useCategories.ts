import { useState, useEffect, useCallback } from 'react'
import { categoryService } from '@/services/categoryService'
import type { Category, CategoryTree, CategoryCreateInput, CategoryUpdateInput } from '@/types'

interface UseCategoriesState {
  categories: Category[]
  categoryTree: CategoryTree[]
  loading: boolean
  error: string | null
}

interface UseCategoriesReturn extends UseCategoriesState {
  fetchCategories: () => Promise<void>
  fetchCategoryTree: () => Promise<void>
  createCategory: (data: CategoryCreateInput) => Promise<Category>
  updateCategory: (categoryId: string, data: CategoryUpdateInput) => Promise<Category>
  deleteCategory: (categoryId: string) => Promise<void>
  clearError: () => void
}

/**
 * Custom hook for managing category data and operations.
 * @param entityId - Entity ID to fetch categories for
 * @returns Categories state and CRUD functions
 */
export function useCategories(entityId: string | null): UseCategoriesReturn {
  const [state, setState] = useState<UseCategoriesState>({
    categories: [],
    categoryTree: [],
    loading: false,
    error: null,
  })

  const setLoading = (loading: boolean) => {
    setState((prev) => ({ ...prev, loading }))
  }

  const setError = (error: string | null) => {
    setState((prev) => ({ ...prev, error, loading: false }))
  }

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }))
  }, [])

  const fetchCategories = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useCategories]: No entityId provided, skipping fetch')
      return
    }

    console.log(`INFO [useCategories]: Fetching categories for entity ${entityId}`)
    setLoading(true)
    try {
      const categories = await categoryService.getCategories(entityId)
      setState((prev) => ({ ...prev, categories, loading: false, error: null }))
      console.log(`INFO [useCategories]: Fetched ${categories.length} categories`)
    } catch (err) {
      console.error('ERROR [useCategories]: Failed to fetch categories:', err)
      setError('Failed to load categories')
    }
  }, [entityId])

  const fetchCategoryTree = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useCategories]: No entityId provided, skipping tree fetch')
      return
    }

    console.log(`INFO [useCategories]: Fetching category tree for entity ${entityId}`)
    setLoading(true)
    try {
      const categoryTree = await categoryService.getCategoryTree(entityId)
      setState((prev) => ({ ...prev, categoryTree, loading: false, error: null }))
      console.log(`INFO [useCategories]: Fetched tree with ${categoryTree.length} root categories`)
    } catch (err) {
      console.error('ERROR [useCategories]: Failed to fetch category tree:', err)
      setError('Failed to load category tree')
    }
  }, [entityId])

  const createCategory = useCallback(
    async (data: CategoryCreateInput): Promise<Category> => {
      console.log(`INFO [useCategories]: Creating category ${data.name}`)
      try {
        const newCategory = await categoryService.createCategory(data)
        console.log(`INFO [useCategories]: Category created with id ${newCategory.id}`)
        // Refresh both lists after creation
        await fetchCategories()
        await fetchCategoryTree()
        return newCategory
      } catch (err) {
        console.error('ERROR [useCategories]: Failed to create category:', err)
        throw err
      }
    },
    [fetchCategories, fetchCategoryTree]
  )

  const updateCategory = useCallback(
    async (categoryId: string, data: CategoryUpdateInput): Promise<Category> => {
      if (!entityId) {
        throw new Error('No entity ID available')
      }

      console.log(`INFO [useCategories]: Updating category ${categoryId}`)
      try {
        const updatedCategory = await categoryService.updateCategory(categoryId, entityId, data)
        console.log(`INFO [useCategories]: Category updated: ${updatedCategory.name}`)
        // Refresh both lists after update
        await fetchCategories()
        await fetchCategoryTree()
        return updatedCategory
      } catch (err) {
        console.error('ERROR [useCategories]: Failed to update category:', err)
        throw err
      }
    },
    [entityId, fetchCategories, fetchCategoryTree]
  )

  const deleteCategory = useCallback(
    async (categoryId: string): Promise<void> => {
      if (!entityId) {
        throw new Error('No entity ID available')
      }

      console.log(`INFO [useCategories]: Deleting category ${categoryId}`)
      try {
        await categoryService.deleteCategory(categoryId, entityId)
        console.log(`INFO [useCategories]: Category deleted: ${categoryId}`)
        // Refresh both lists after deletion
        await fetchCategories()
        await fetchCategoryTree()
      } catch (err) {
        console.error('ERROR [useCategories]: Failed to delete category:', err)
        throw err
      }
    },
    [entityId, fetchCategories, fetchCategoryTree]
  )

  // Auto-fetch when entityId changes
  useEffect(() => {
    if (entityId) {
      fetchCategories()
      fetchCategoryTree()
    }
  }, [entityId, fetchCategories, fetchCategoryTree])

  return {
    ...state,
    fetchCategories,
    fetchCategoryTree,
    createCategory,
    updateCategory,
    deleteCategory,
    clearError,
  }
}

export default useCategories

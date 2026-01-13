import { apiClient } from '@/api/clients'
import type { Category, CategoryTree, CategoryCreateInput, CategoryUpdateInput } from '@/types'

/**
 * Category service for CRUD operations on categories.
 */
export const categoryService = {
  /**
   * Get all categories for an entity.
   * @param entityId - Entity ID
   * @param includeInactive - Whether to include inactive categories
   * @returns List of categories
   */
  async getCategories(entityId: string, includeInactive: boolean = false): Promise<Category[]> {
    console.log(`INFO [CategoryService]: Fetching categories for entity ${entityId}`)
    try {
      const response = await apiClient.get<Category[]>(`/categories/entity/${entityId}`, {
        params: { include_inactive: includeInactive },
      })
      console.log(`INFO [CategoryService]: Fetched ${response.data.length} categories`)
      return response.data
    } catch (error) {
      console.error('ERROR [CategoryService]: Failed to fetch categories:', error)
      throw error
    }
  },

  /**
   * Get hierarchical category tree for an entity.
   * @param entityId - Entity ID
   * @returns Tree structure of categories
   */
  async getCategoryTree(entityId: string): Promise<CategoryTree[]> {
    console.log(`INFO [CategoryService]: Fetching category tree for entity ${entityId}`)
    try {
      const response = await apiClient.get<CategoryTree[]>(`/categories/entity/${entityId}/tree`)
      console.log(`INFO [CategoryService]: Fetched category tree with ${response.data.length} root categories`)
      return response.data
    } catch (error) {
      console.error('ERROR [CategoryService]: Failed to fetch category tree:', error)
      throw error
    }
  },

  /**
   * Get a single category by ID.
   * @param categoryId - Category ID
   * @param entityId - Entity ID for validation
   * @returns Category data
   */
  async getCategory(categoryId: string, entityId: string): Promise<Category> {
    console.log(`INFO [CategoryService]: Fetching category ${categoryId}`)
    try {
      const response = await apiClient.get<Category>(`/categories/${categoryId}`, {
        params: { entity_id: entityId },
      })
      console.log(`INFO [CategoryService]: Fetched category ${response.data.name}`)
      return response.data
    } catch (error) {
      console.error('ERROR [CategoryService]: Failed to fetch category:', error)
      throw error
    }
  },

  /**
   * Create a new category.
   * @param data - Category creation data
   * @returns Created category
   */
  async createCategory(data: CategoryCreateInput): Promise<Category> {
    console.log(`INFO [CategoryService]: Creating category ${data.name}`)
    try {
      const response = await apiClient.post<Category>('/categories/', data)
      console.log(`INFO [CategoryService]: Created category ${response.data.id}`)
      return response.data
    } catch (error) {
      console.error('ERROR [CategoryService]: Failed to create category:', error)
      throw error
    }
  },

  /**
   * Update an existing category.
   * @param categoryId - Category ID to update
   * @param entityId - Entity ID for validation
   * @param data - Category update data
   * @returns Updated category
   */
  async updateCategory(
    categoryId: string,
    entityId: string,
    data: CategoryUpdateInput
  ): Promise<Category> {
    console.log(`INFO [CategoryService]: Updating category ${categoryId}`)
    try {
      const response = await apiClient.put<Category>(`/categories/${categoryId}`, data, {
        params: { entity_id: entityId },
      })
      console.log(`INFO [CategoryService]: Updated category ${response.data.name}`)
      return response.data
    } catch (error) {
      console.error('ERROR [CategoryService]: Failed to update category:', error)
      throw error
    }
  },

  /**
   * Delete a category.
   * @param categoryId - Category ID to delete
   * @param entityId - Entity ID for validation
   */
  async deleteCategory(categoryId: string, entityId: string): Promise<void> {
    console.log(`INFO [CategoryService]: Deleting category ${categoryId}`)
    try {
      await apiClient.delete(`/categories/${categoryId}`, {
        params: { entity_id: entityId },
      })
      console.log(`INFO [CategoryService]: Deleted category ${categoryId}`)
    } catch (error) {
      console.error('ERROR [CategoryService]: Failed to delete category:', error)
      throw error
    }
  },
}

export default categoryService

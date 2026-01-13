// Base API response interface
export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

// User interface matching backend UserResponseDTO
export interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  is_active: boolean
  createdAt?: string
  updatedAt?: string
}

// Login credentials for authentication
export interface LoginCredentials {
  email: string
  password: string
}

// Registration data for new users
export interface RegisterData {
  email: string
  password: string
  first_name?: string
  last_name?: string
}

// Authentication response from backend
export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// Authentication state placeholder
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

// Entity interface matching backend EntityResponseDTO
export interface Entity {
  id: string
  name: string
  type: 'family' | 'startup'
  description?: string
  created_at: string
  updated_at?: string
}

// Data for creating a new entity
export interface CreateEntityData {
  name: string
  type: 'family' | 'startup'
  description?: string
}

// Data for updating an entity
export interface UpdateEntityData {
  name?: string
  description?: string
}

// User-Entity membership interface
export interface UserEntity {
  id: string
  user_id: string
  entity_id: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  created_at: string
}

// Entity member with user details
export interface EntityMember {
  id: string
  user_id: string
  email: string
  first_name?: string
  last_name?: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  created_at: string
}

// Transaction types placeholder
export type TransactionType = 'income' | 'expense'

export interface Transaction {
  id: string
  entityId: string
  categoryId: string
  type: TransactionType
  amount: number
  description: string
  date: string
  createdAt: string
  updatedAt: string
}

// Category interface placeholder
export interface Category {
  id: string
  name: string
  type: TransactionType
  parentId?: string
  createdAt: string
  updatedAt: string
}

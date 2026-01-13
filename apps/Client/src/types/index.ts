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

// Entity interface placeholder
export interface Entity {
  id: string
  name: string
  type: 'family' | 'startup'
  createdAt: string
  updatedAt: string
}

// Transaction types
export type TransactionType = 'income' | 'expense'

export interface Transaction {
  id: string
  entity_id: string
  category_id: string
  user_id?: string
  type: TransactionType
  amount: number
  description?: string
  date: string
  notes?: string
  created_at: string
  updated_at?: string
}

export interface TransactionCreate {
  entity_id: string
  category_id: string
  amount: number
  type: TransactionType
  description?: string
  date: string
  notes?: string
}

export interface TransactionUpdate {
  category_id?: string
  amount?: number
  type?: TransactionType
  description?: string
  date?: string
  notes?: string
}

export interface TransactionFilters {
  start_date?: string
  end_date?: string
  category_id?: string
  type?: TransactionType
}

export interface TransactionListResponse {
  transactions: Transaction[]
  total: number
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

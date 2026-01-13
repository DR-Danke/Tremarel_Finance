// Base API response interface
export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

// User interface placeholder
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  createdAt: string
  updatedAt: string
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

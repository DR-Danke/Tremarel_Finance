import { apiClient } from '@/api/clients'
import type { LoginCredentials, RegisterData, AuthResponse, User } from '@/types'

/**
 * Authentication service for login, register, and user management.
 */
export const authService = {
  /**
   * Login user with email and password credentials.
   * @param credentials - Email and password
   * @returns Authentication response with token and user data
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    console.log('INFO [AuthService]: Attempting login for email:', credentials.email)
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials)
      console.log('INFO [AuthService]: Login successful for user:', response.data.user.email)
      return response.data
    } catch (error) {
      console.error('ERROR [AuthService]: Login failed:', error)
      throw error
    }
  },

  /**
   * Register a new user.
   * @param data - Registration data including email, password, and optional name
   * @returns Authentication response with token and user data
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    console.log('INFO [AuthService]: Attempting registration for email:', data.email)
    try {
      const response = await apiClient.post<AuthResponse>('/auth/register', data)
      console.log('INFO [AuthService]: Registration successful for user:', response.data.user.email)
      return response.data
    } catch (error) {
      console.error('ERROR [AuthService]: Registration failed:', error)
      throw error
    }
  },

  /**
   * Get current authenticated user data.
   * @returns Current user data
   */
  async getCurrentUser(): Promise<User> {
    console.log('INFO [AuthService]: Fetching current user')
    try {
      const response = await apiClient.get<User>('/auth/me')
      console.log('INFO [AuthService]: Current user fetched:', response.data.email)
      return response.data
    } catch (error) {
      console.error('ERROR [AuthService]: Failed to fetch current user:', error)
      throw error
    }
  },
}

export default authService

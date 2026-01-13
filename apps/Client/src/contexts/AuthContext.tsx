import React, { useState, useEffect, useCallback, useMemo } from 'react'
import type { User, LoginCredentials } from '@/types'
import { authService } from '@/services/authService'
import { AuthContext, type AuthContextType } from './authContextDef'

const TOKEN_KEY = 'token'

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = useMemo(() => !!token && !!user, [token, user])

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initializeAuth = async () => {
      console.log('INFO [AuthContext]: Initializing authentication state')
      const storedToken = localStorage.getItem(TOKEN_KEY)

      if (storedToken) {
        console.log('INFO [AuthContext]: Found stored token, validating...')
        setToken(storedToken)

        try {
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
          console.log('INFO [AuthContext]: Token validated, user authenticated:', currentUser.email)
        } catch (error) {
          console.error('ERROR [AuthContext]: Token validation failed, clearing auth state')
          localStorage.removeItem(TOKEN_KEY)
          setToken(null)
          setUser(null)
        }
      } else {
        console.log('INFO [AuthContext]: No stored token found')
      }

      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  const login = useCallback(async (credentials: LoginCredentials) => {
    console.log('INFO [AuthContext]: Login attempt for:', credentials.email)

    const response = await authService.login(credentials)

    // Store token in localStorage
    localStorage.setItem(TOKEN_KEY, response.access_token)
    setToken(response.access_token)
    setUser(response.user)

    console.log('INFO [AuthContext]: Login successful, user:', response.user.email)
  }, [])

  const logout = useCallback(() => {
    console.log('INFO [AuthContext]: Logging out user:', user?.email)

    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)

    console.log('INFO [AuthContext]: User logged out successfully')
  }, [user?.email])

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      token,
      isAuthenticated,
      isLoading,
      login,
      logout,
    }),
    [user, token, isAuthenticated, isLoading, login, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthProvider

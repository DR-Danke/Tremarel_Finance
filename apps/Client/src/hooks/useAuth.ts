import { useContext } from 'react'
import { AuthContext, type AuthContextType } from '@/contexts/authContextDef'

/**
 * Custom hook for accessing authentication context.
 * @throws Error if used outside of AuthProvider
 * @returns AuthContextType with user, token, isAuthenticated, isLoading, login, logout
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}

export default useAuth

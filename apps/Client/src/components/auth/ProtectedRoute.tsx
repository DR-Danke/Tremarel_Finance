import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'

interface ProtectedRouteProps {
  children: React.ReactNode
}

/**
 * Route guard component that protects routes for authenticated users only.
 * Redirects unauthenticated users to login page, preserving the attempted location.
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  // Show loading indicator while checking authentication
  if (isLoading) {
    console.log('INFO [ProtectedRoute]: Checking authentication status...')
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    console.log('INFO [ProtectedRoute]: User not authenticated, redirecting to login from:', location.pathname)
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  console.log('INFO [ProtectedRoute]: User authenticated, rendering protected content')
  return <>{children}</>
}

export default ProtectedRoute

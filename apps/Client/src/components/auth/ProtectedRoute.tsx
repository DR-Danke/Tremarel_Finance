import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const MODULE_ROUTE_PREFIXES: Record<string, string[]> = {
  legaldesk: ['/poc/legal-desk'],
  'restaurant-os': ['/poc/restaurant-os'],
  finance: ['/dashboard', '/transactions', '/recurring', '/categories', '/budgets', '/prospects', '/reports'],
}

const MODULE_DEFAULT_PAGES: Record<string, string> = {
  legaldesk: '/poc/legal-desk/dashboard',
  'restaurant-os': '/poc/restaurant-os/dashboard',
  finance: '/dashboard',
}

/**
 * Route guard component that protects routes for authenticated users only.
 * Redirects unauthenticated users to login page, preserving the attempted location.
 * Module-restricted users are redirected to their default module page.
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isAuthenticated, isLoading } = useAuth()
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

  // Module-based access control
  const allowedModules = user?.allowed_modules
  if (allowedModules && allowedModules.length > 0) {
    const currentPath = location.pathname
    console.log(`INFO [ProtectedRoute]: allowed_modules=${JSON.stringify(allowedModules)}, currentPath=${currentPath}`)

    // Always allow /settings
    if (currentPath === '/settings') {
      return <>{children}</>
    }

    // Check if current path is allowed by any module
    const isAllowed = allowedModules.some((mod) => {
      const prefixes = MODULE_ROUTE_PREFIXES[mod]
      console.log(`INFO [ProtectedRoute]: Checking module="${mod}", prefixes=${JSON.stringify(prefixes)}`)
      return prefixes?.some((prefix) => currentPath.startsWith(prefix))
    })

    if (!isAllowed) {
      const defaultPage = MODULE_DEFAULT_PAGES[allowedModules[0]] ?? '/dashboard'
      console.log(`INFO [ProtectedRoute]: Module-restricted user redirected from ${currentPath} to ${defaultPage}`)
      return <Navigate to={defaultPage} replace />
    }
  }

  console.log('INFO [ProtectedRoute]: User authenticated, rendering protected content')
  return <>{children}</>
}

export default ProtectedRoute

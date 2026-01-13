import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Box, CircularProgress, Typography, Container, Paper, Button } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'
import type { User } from '@/types'

interface RoleProtectedRouteProps {
  children: React.ReactNode
  allowedRoles: User['role'][]
}

/**
 * Route guard component that protects routes based on user roles.
 * Redirects unauthenticated users to login page.
 * Shows access denied message for authenticated users without required role.
 */
export const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({
  children,
  allowedRoles,
}) => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  // Show loading indicator while checking authentication
  if (isLoading) {
    console.log('INFO [RoleProtectedRoute]: Checking authentication status...')
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
    console.log('INFO [RoleProtectedRoute]: User not authenticated, redirecting to login from:', location.pathname)
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check if user has required role
  if (user && !allowedRoles.includes(user.role)) {
    console.log(
      `INFO [RoleProtectedRoute]: User role '${user.role}' not in allowed roles [${allowedRoles.join(', ')}]. Access denied.`
    )
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              textAlign: 'center',
            }}
          >
            <Typography variant="h4" component="h1" gutterBottom color="error">
              Access Denied
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              You do not have permission to access this page.
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Required roles: {allowedRoles.join(', ')}
            </Typography>
            <Button variant="contained" href="/dashboard">
              Go to Dashboard
            </Button>
          </Paper>
        </Box>
      </Container>
    )
  }

  console.log('INFO [RoleProtectedRoute]: User has required role, rendering protected content')
  return <>{children}</>
}

export default RoleProtectedRoute

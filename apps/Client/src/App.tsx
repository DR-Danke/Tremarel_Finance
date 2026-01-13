import { useEffect } from 'react'
import { Routes, Route, useLocation, Link } from 'react-router-dom'
import { Box, Typography, Container, Button } from '@mui/material'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { EntitiesPage } from '@/pages/EntitiesPage'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

function HomePage() {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom>
          Finance Tracker
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Track your income and expenses for family and startup management
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Welcome! Sign in to access your dashboard.
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button variant="contained" component={Link} to="/login">
            Sign In
          </Button>
          <Button variant="outlined" component={Link} to="/dashboard">
            Dashboard
          </Button>
        </Box>
      </Box>
    </Container>
  )
}

function App() {
  const location = useLocation()

  useEffect(() => {
    console.log(`INFO [App]: Route changed to ${location.pathname}`)
  }, [location])

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entities"
        element={
          <ProtectedRoute>
            <EntitiesPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App

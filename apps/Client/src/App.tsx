import { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import { Box, Typography, Container } from '@mui/material'

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
        <Typography variant="body1" color="text.secondary">
          Welcome! Authentication and dashboard features coming soon.
        </Typography>
      </Box>
    </Container>
  )
}

function LoginPage() {
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
        <Typography variant="h4" component="h1" gutterBottom>
          Login
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Login form will be implemented in the authentication module.
        </Typography>
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
    </Routes>
  )
}

export default App

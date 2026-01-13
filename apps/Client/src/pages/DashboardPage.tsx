import { Box, Typography, Container, Paper, Button, Grid } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'
import { useNavigate } from 'react-router-dom'

/**
 * Dashboard page displaying user info and logout functionality.
 * This is a placeholder page for future dashboard features.
 */
export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    console.log('INFO [DashboardPage]: User initiated logout')
    logout()
    navigate('/login')
  }

  // Get display name from user data
  const displayName = user?.first_name
    ? `${user.first_name}${user.last_name ? ` ${user.last_name}` : ''}`
    : user?.email

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          py: 4,
          minHeight: '100vh',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            mb: 4,
          }}
        >
          <Grid container justifyContent="space-between" alignItems="center">
            <Grid>
              <Typography variant="h4" component="h1" gutterBottom>
                Welcome, {displayName}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {user?.email}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Role: {user?.role}
              </Typography>
            </Grid>
            <Grid>
              <Button variant="outlined" color="primary" onClick={handleLogout}>
                Logout
              </Button>
            </Grid>
          </Grid>
        </Paper>

        <Paper
          elevation={1}
          sx={{
            p: 4,
            textAlign: 'center',
          }}
        >
          <Typography variant="h5" gutterBottom>
            Finance Tracker Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Dashboard features coming soon.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            You will be able to track your income and expenses, manage budgets, and view financial
            reports.
          </Typography>
        </Paper>
      </Box>
    </Container>
  )
}

export default DashboardPage

import { Box, Typography, Container, Paper, Button, Grid, Divider } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'
import { useEntity } from '@/hooks/useEntity'
import { useNavigate, Link } from 'react-router-dom'
import { TREntitySelector } from '@/components/ui/TREntitySelector'

/**
 * Dashboard page displaying user info, current entity, and logout functionality.
 * This is a placeholder page for future dashboard features.
 */
export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth()
  const { currentEntity, entities } = useEntity()
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
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <TREntitySelector />
                <Button variant="outlined" component={Link} to="/entities">
                  Manage Entities
                </Button>
                <Button variant="outlined" color="primary" onClick={handleLogout}>
                  Logout
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Current Entity Info */}
        {currentEntity ? (
          <Paper
            elevation={2}
            sx={{
              p: 3,
              mb: 4,
              backgroundColor: currentEntity.type === 'family' ? 'primary.light' : 'secondary.light',
              color: 'primary.contrastText',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Current Entity: {currentEntity.name}
            </Typography>
            <Typography variant="body2">
              Type: {currentEntity.type.charAt(0).toUpperCase() + currentEntity.type.slice(1)}
            </Typography>
            {currentEntity.description && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                {currentEntity.description}
              </Typography>
            )}
          </Paper>
        ) : (
          <Paper
            elevation={2}
            sx={{
              p: 3,
              mb: 4,
              textAlign: 'center',
            }}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Entity Selected
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {entities.length === 0
                ? 'Create your first entity to start tracking finances.'
                : 'Select an entity to view its financial data.'}
            </Typography>
            <Button
              variant="contained"
              component={Link}
              to="/entities"
              sx={{ mt: 2 }}
            >
              {entities.length === 0 ? 'Create Entity' : 'Manage Entities'}
            </Button>
          </Paper>
        )}

        <Divider sx={{ my: 4 }} />

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

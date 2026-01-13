import { Box, Typography, Paper, Grid } from '@mui/material'
import { useAuth } from '@/hooks/useAuth'
import { useEntity } from '@/hooks/useEntity'

/**
 * Dashboard page displaying user info and current entity.
 * This is a placeholder page for future dashboard features.
 */
export const DashboardPage: React.FC = () => {
  const { user } = useAuth()
  const { currentEntity } = useEntity()

  // Get display name from user data
  const displayName = user?.first_name
    ? `${user.first_name}${user.last_name ? ` ${user.last_name}` : ''}`
    : user?.email

  return (
    <Box>
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
            {currentEntity && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Current Entity: {currentEntity.name} ({currentEntity.type})
              </Typography>
            )}
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
  )
}

export default DashboardPage

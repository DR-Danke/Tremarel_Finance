import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Grid,
  Divider,
  Alert,
  Skeleton,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { useAuth } from '@/hooks/useAuth'
import { useEntity } from '@/hooks/useEntity'
import { useDashboard } from '@/hooks/useDashboard'
import { useNavigate, Link } from 'react-router-dom'
import { TREntitySelector } from '@/components/ui/TREntitySelector'
import { TRStatCard } from '@/components/ui/TRStatCard'
import { TRMonthlyTrendChart } from '@/components/ui/TRMonthlyTrendChart'
import { TRExpenseBreakdownChart } from '@/components/ui/TRExpenseBreakdownChart'

/**
 * Dashboard page displaying financial summary, charts, and quick actions.
 */
export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth()
  const { currentEntity, entities } = useEntity()
  const { stats, isLoading, error } = useDashboard(currentEntity?.id)
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

  // Render loading skeleton for stat cards
  const renderStatCardSkeleton = () => (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Box sx={{ flex: 1 }}>
          <Skeleton width={100} height={20} />
          <Skeleton width={150} height={40} sx={{ mt: 1 }} />
        </Box>
        <Skeleton variant="circular" width={60} height={60} />
      </Box>
    </Paper>
  )

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
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

        {/* Dashboard Content - Only show if entity is selected */}
        {currentEntity && (
          <>
            {/* Error State */}
            {error && (
              <Alert severity="error" sx={{ mb: 4 }}>
                {error}
              </Alert>
            )}

            {/* Loading State for Stat Cards */}
            {isLoading ? (
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={4}>
                  {renderStatCardSkeleton()}
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  {renderStatCardSkeleton()}
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  {renderStatCardSkeleton()}
                </Grid>
              </Grid>
            ) : stats ? (
              <>
                {/* Stat Cards */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} sm={6} md={4}>
                    <TRStatCard
                      title="Total Income"
                      value={Number(stats.current_month_summary.total_income)}
                      subtitle="This month"
                      variant="income"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <TRStatCard
                      title="Total Expenses"
                      value={Number(stats.current_month_summary.total_expenses)}
                      subtitle="This month"
                      variant="expense"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <TRStatCard
                      title="Net Balance"
                      value={Number(stats.current_month_summary.net_balance)}
                      subtitle="This month"
                      variant="balance"
                    />
                  </Grid>
                </Grid>

                {/* Charts Section */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} md={7}>
                    <TRMonthlyTrendChart data={stats.monthly_trends} />
                  </Grid>
                  <Grid item xs={12} md={5}>
                    <TRExpenseBreakdownChart data={stats.expense_breakdown} />
                  </Grid>
                </Grid>
              </>
            ) : null}

            <Divider sx={{ my: 4 }} />

            {/* Quick Actions */}
            <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Manage your finances with these quick actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  component={Link}
                  to="/transactions"
                >
                  Add Transaction
                </Button>
                <Button
                  variant="outlined"
                  component={Link}
                  to="/categories"
                >
                  Manage Categories
                </Button>
              </Box>
            </Paper>
          </>
        )}
      </Box>
    </Container>
  )
}

export default DashboardPage

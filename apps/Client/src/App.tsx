import { useEffect } from 'react'
import { Routes, Route, useLocation, Link } from 'react-router-dom'
import { Box, Typography, Container, Button } from '@mui/material'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { TRMainLayout } from '@/components/layout'

// Placeholder pages for future implementation
function TransactionsPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Transactions
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Transaction management coming soon.
      </Typography>
    </Box>
  )
}

function CategoriesPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Categories
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Category management coming soon.
      </Typography>
    </Box>
  )
}

function BudgetsPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Budgets
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Budget tracking coming soon.
      </Typography>
    </Box>
  )
}

function ReportsPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Reports
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Financial reports coming soon.
      </Typography>
    </Box>
  )
}

function SettingsPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Application settings coming soon.
      </Typography>
    </Box>
  )
}

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

      {/* Protected routes with main layout */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <TRMainLayout>
              <DashboardPage />
            </TRMainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/transactions"
        element={
          <ProtectedRoute>
            <TRMainLayout>
              <TransactionsPage />
            </TRMainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/categories"
        element={
          <ProtectedRoute>
            <TRMainLayout>
              <CategoriesPage />
            </TRMainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/budgets"
        element={
          <ProtectedRoute>
            <TRMainLayout>
              <BudgetsPage />
            </TRMainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <TRMainLayout>
              <ReportsPage />
            </TRMainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <TRMainLayout>
              <SettingsPage />
            </TRMainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App

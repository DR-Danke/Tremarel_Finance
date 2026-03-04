import React from 'react'
import { Alert, Box, Button, Card, CardContent, CircularProgress, Grid, Typography } from '@mui/material'
import GavelIcon from '@mui/icons-material/Gavel'
import PeopleIcon from '@mui/icons-material/People'
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
import GroupsIcon from '@mui/icons-material/Groups'
import { useLegaldeskDashboard } from '@/hooks/useLegaldeskDashboard'

export const LegalDeskDashboardPage: React.FC = () => {
  const { stats, loading, error, refreshStats } = useLegaldeskDashboard()

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={refreshStats}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Legal Desk Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Overview of cases, specialists, and clients
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <GavelIcon sx={{ fontSize: 40, color: '#1565C0' }} />
              <Box>
                <Typography variant="h4">{stats?.total_cases ?? 0}</Typography>
                <Typography variant="body2" color="text.secondary">Total Cases</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <BusinessCenterIcon sx={{ fontSize: 40, color: '#2E7D32' }} />
              <Box>
                <Typography variant="h4">{stats?.active_cases ?? 0}</Typography>
                <Typography variant="body2" color="text.secondary">Active Cases</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <PeopleIcon sx={{ fontSize: 40, color: '#7B1FA2' }} />
              <Box>
                <Typography variant="h4">{stats?.total_specialists ?? 0}</Typography>
                <Typography variant="body2" color="text.secondary">Specialists</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <GroupsIcon sx={{ fontSize: 40, color: '#00796B' }} />
              <Box>
                <Typography variant="h4">{stats?.total_clients ?? 0}</Typography>
                <Typography variant="body2" color="text.secondary">Clients</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default LegalDeskDashboardPage

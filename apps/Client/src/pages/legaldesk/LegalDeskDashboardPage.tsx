import React from 'react'
import {
  Box,
  Typography,
  Container,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useLegaldeskDashboard } from '@/hooks/useLegaldeskDashboard'
import {
  CASE_STATUS_LABELS,
  CASE_STATUS_COLORS,
  LEGAL_DOMAIN_LABELS,
  LEGAL_DOMAIN_COLORS,
} from '@/types/legaldesk'
import type { CaseStatus, LegalDomain } from '@/types/legaldesk'

export const LegalDeskDashboardPage: React.FC = () => {
  const { stats, loading, error, refreshStats } = useLegaldeskDashboard()

  console.log('INFO [LegalDeskDashboardPage]: Rendering dashboard')

  if (loading && !stats) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
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
      </Container>
    )
  }

  const statusChartData = stats
    ? Object.entries(stats.cases_by_status)
        .filter(([, value]) => value > 0)
        .map(([key, value]) => ({
          name: CASE_STATUS_LABELS[key as CaseStatus],
          value,
          fill: CASE_STATUS_COLORS[key as CaseStatus],
        }))
    : []

  const domainChartData = stats
    ? Object.entries(stats.cases_by_domain)
        .filter(([, value]) => value > 0)
        .map(([key, value]) => ({
          name: LEGAL_DOMAIN_LABELS[key as LegalDomain],
          value,
          fill: LEGAL_DOMAIN_COLORS[key as LegalDomain],
        }))
    : []

  const statCards = stats
    ? [
        { title: 'Active Cases', value: stats.active_cases },
        { title: 'Total Cases', value: stats.total_cases },
        { title: 'Specialists Active', value: stats.total_specialists },
        { title: 'Total Clients', value: stats.total_clients },
      ]
    : []

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Legal Desk Dashboard
          </Typography>
          <Button startIcon={<RefreshIcon />} onClick={refreshStats} disabled={loading}>
            Refresh
          </Button>
        </Box>

        {/* Stat Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {statCards.map((card) => (
            <Grid item xs={12} sm={6} md={3} key={card.title}>
              <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h3" fontWeight={700}>
                  {card.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {card.title}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Cases by Status
              </Typography>
              {statusChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusChartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {statusChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                  No case data available.
                </Typography>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Cases by Domain
              </Typography>
              {domainChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={domainChartData}>
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={11} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="value" name="Cases">
                      {domainChartData.map((entry, index) => (
                        <Cell key={`bar-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                  No domain data available.
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  )
}

export default LegalDeskDashboardPage

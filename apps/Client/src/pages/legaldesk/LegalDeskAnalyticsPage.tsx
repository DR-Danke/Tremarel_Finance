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
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useLegaldeskDashboard } from '@/hooks/useLegaldeskDashboard'
import { LEGAL_DOMAIN_LABELS, LEGAL_DOMAIN_COLORS } from '@/types/legaldesk'
import type { LegalDomain } from '@/types/legaldesk'

export const LegalDeskAnalyticsPage: React.FC = () => {
  const { stats, loading, error, refreshStats } = useLegaldeskDashboard()

  console.log('INFO [LegalDeskAnalyticsPage]: Rendering analytics page')

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

  const domainChartData = stats
    ? Object.entries(stats.cases_by_domain)
        .filter(([, value]) => value > 0)
        .map(([key, value]) => ({
          name: LEGAL_DOMAIN_LABELS[key as LegalDomain],
          value,
          fill: LEGAL_DOMAIN_COLORS[key as LegalDomain],
        }))
    : []

  const summaryCards = stats
    ? [
        { title: 'Total Cases', value: stats.total_cases },
        { title: 'Active Cases', value: stats.active_cases },
        { title: 'Total Specialists', value: stats.total_specialists },
      ]
    : []

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Legal Desk Analytics
        </Typography>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {summaryCards.map((card) => (
            <Grid item xs={12} sm={4} key={card.title}>
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
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Cases by Domain
              </Typography>
              {domainChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
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
                  No data available.
                </Typography>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Specialist Utilization
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                Specialist utilization analytics will be available once cases are assigned.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  )
}

export default LegalDeskAnalyticsPage

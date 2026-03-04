import React, { useState } from 'react'
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  Snackbar,
  LinearProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { useLegaldeskSpecialists } from '@/hooks/useLegaldeskSpecialists'
import { TRLegalSpecialistForm } from '@/components/forms/TRLegalSpecialistForm'
import { TRSpecialistScoreDisplay } from '@/components/ui/TRSpecialistScoreDisplay'
import type { LdSpecialistCreate } from '@/types/legaldesk'

export const LegalDeskSpecialistsPage: React.FC = () => {
  const { specialists, loading, error, createSpecialist, refreshSpecialists } =
    useLegaldeskSpecialists()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [snackbar, setSnackbar] = useState<string | null>(null)

  console.log('INFO [LegalDeskSpecialistsPage]: Rendering specialists page')

  const handleCreateSpecialist = async (data: LdSpecialistCreate) => {
    setSubmitting(true)
    try {
      await createSpecialist(data)
      setDialogOpen(false)
      setSnackbar('Specialist created successfully')
      console.log('INFO [LegalDeskSpecialistsPage]: Specialist created')
    } catch {
      console.error('ERROR [LegalDeskSpecialistsPage]: Failed to create specialist')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading && specialists.length === 0) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Legal Desk Specialists
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
            Add Specialist
          </Button>
        </Box>

        {error && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            action={
              <Button color="inherit" size="small" onClick={refreshSpecialists}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {specialists.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No specialists yet. Click "Add Specialist" to create one.
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {specialists.map((specialist) => {
              const workloadPct =
                specialist.max_concurrent_cases > 0
                  ? (specialist.current_workload / specialist.max_concurrent_cases) * 100
                  : 0
              return (
                <Grid item xs={12} sm={6} md={4} key={specialist.id}>
                  <Card elevation={2}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {specialist.full_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {specialist.email}
                      </Typography>
                      <Typography variant="body2">
                        Experience: {specialist.years_experience} years
                      </Typography>
                      {specialist.hourly_rate != null && (
                        <Typography variant="body2">
                          Rate: {specialist.currency} {specialist.hourly_rate}/hr
                        </Typography>
                      )}
                      <Box sx={{ mt: 1.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          Score
                        </Typography>
                        <TRSpecialistScoreDisplay score={specialist.overall_score} />
                      </Box>
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Workload: {specialist.current_workload}/{specialist.max_concurrent_cases}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(workloadPct, 100)}
                          color={workloadPct >= 80 ? 'error' : workloadPct >= 50 ? 'warning' : 'primary'}
                          sx={{ height: 6, borderRadius: 3, mt: 0.5 }}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )
            })}
          </Grid>
        )}

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Specialist</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <TRLegalSpecialistForm onSubmit={handleCreateSpecialist} loading={submitting} />
          </DialogContent>
        </Dialog>

        <Snackbar
          open={!!snackbar}
          autoHideDuration={3000}
          onClose={() => setSnackbar(null)}
          message={snackbar}
        />
      </Box>
    </Container>
  )
}

export default LegalDeskSpecialistsPage

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
  CardActions,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  Snackbar,
  LinearProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import { useLegaldeskSpecialists } from '@/hooks/useLegaldeskSpecialists'
import { legaldeskService } from '@/services/legaldeskService'
import { TRLegalSpecialistForm } from '@/components/forms/TRLegalSpecialistForm'
import { TRSpecialistScoreDisplay } from '@/components/ui/TRSpecialistScoreDisplay'
import type { LdSpecialistCreate, LdSpecialistUpdate, LdSpecialistDetail, LegalDomain, ProficiencyLevel } from '@/types/legaldesk'

export const LegalDeskSpecialistsPage: React.FC = () => {
  const { specialists, loading, error, createSpecialist, updateSpecialist, addExpertise, addJurisdiction, refreshSpecialists } =
    useLegaldeskSpecialists()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingSpecialist, setEditingSpecialist] = useState<LdSpecialistDetail | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [snackbar, setSnackbar] = useState<string | null>(null)

  console.log('INFO [LegalDeskSpecialistsPage]: Rendering specialists page')

  const handleOpenCreate = () => {
    setEditingSpecialist(null)
    setDialogOpen(true)
  }

  const handleOpenEdit = async (specialistId: number) => {
    try {
      const detail = await legaldeskService.getSpecialist(specialistId)
      setEditingSpecialist(detail)
      setDialogOpen(true)
    } catch {
      console.error('ERROR [LegalDeskSpecialistsPage]: Failed to fetch specialist detail')
      setSnackbar('Failed to load specialist details')
    }
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingSpecialist(null)
  }

  const handleSubmitSpecialist = async (
    data: LdSpecialistCreate | LdSpecialistUpdate,
    expertise?: { legal_domain: string; proficiency_level: string }[],
    jurisdictions?: { country: string; region: string; is_primary: boolean }[],
  ) => {
    setSubmitting(true)
    try {
      if (editingSpecialist) {
        await updateSpecialist(editingSpecialist.id, data as LdSpecialistUpdate)
        if (expertise) {
          for (const exp of expertise) {
            await addExpertise(editingSpecialist.id, { specialist_id: editingSpecialist.id, legal_domain: exp.legal_domain as LegalDomain, proficiency_level: exp.proficiency_level as ProficiencyLevel })
          }
        }
        if (jurisdictions) {
          for (const jur of jurisdictions) {
            if (jur.country) {
              await addJurisdiction(editingSpecialist.id, { specialist_id: editingSpecialist.id, country: jur.country, region: jur.region || undefined, is_primary: jur.is_primary })
            }
          }
        }
        setSnackbar('Specialist updated successfully')
        console.log('INFO [LegalDeskSpecialistsPage]: Specialist updated')
      } else {
        await createSpecialist(data as LdSpecialistCreate)
        setSnackbar('Specialist created successfully')
        console.log('INFO [LegalDeskSpecialistsPage]: Specialist created')
      }
      handleCloseDialog()
    } catch {
      console.error('ERROR [LegalDeskSpecialistsPage]: Failed to save specialist')
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
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}>
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
                    <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenEdit(specialist.id)}
                      >
                        Edit
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              )
            })}
          </Grid>
        )}

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>{editingSpecialist ? 'Edit Specialist' : 'Add Specialist'}</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <TRLegalSpecialistForm
              onSubmit={handleSubmitSpecialist}
              initialData={editingSpecialist ?? undefined}
              onCancel={handleCloseDialog}
              isSubmitting={submitting}
            />
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

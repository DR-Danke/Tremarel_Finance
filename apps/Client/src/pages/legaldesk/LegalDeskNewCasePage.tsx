import React, { useState } from 'react'
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { useNavigate } from 'react-router-dom'
import { useLegaldeskCases } from '@/hooks/useLegaldeskCases'
import { useLegaldeskClients } from '@/hooks/useLegaldeskClients'
import { TRLegalCaseForm } from '@/components/forms/TRLegalCaseForm'
import type { LdCaseCreate, LdCaseUpdate } from '@/types/legaldesk'

export const LegalDeskNewCasePage: React.FC = () => {
  const { createCase } = useLegaldeskCases()
  const { clients, loading: clientsLoading } = useLegaldeskClients()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  console.log('INFO [LegalDeskNewCasePage]: Rendering new case page')

  const handleSubmit = async (data: LdCaseCreate | LdCaseUpdate) => {
    // Form always submits LdCaseCreate in create mode
    setSubmitting(true)
    setSubmitError(null)
    try {
      const newCase = await createCase(data as LdCaseCreate)
      console.log('INFO [LegalDeskNewCasePage]: Case created:', newCase.id)
      navigate(`/poc/legal-desk/cases/${newCase.id}`)
    } catch {
      setSubmitError('Failed to create case. Please try again.')
      console.error('ERROR [LegalDeskNewCasePage]: Failed to create case')
    } finally {
      setSubmitting(false)
    }
  }

  if (clientsLoading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/poc/legal-desk/cases')}
          sx={{ mb: 2 }}
        >
          Back to Cases
        </Button>

        <Typography variant="h4" component="h1" gutterBottom>
          New Case
        </Typography>

        {submitError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {submitError}
          </Alert>
        )}

        <Paper sx={{ p: 3 }}>
          <TRLegalCaseForm
            onSubmit={handleSubmit}
            clients={clients}
            onCancel={() => navigate('/poc/legal-desk/cases')}
            isSubmitting={submitting}
          />
        </Paper>
      </Box>
    </Container>
  )
}

export default LegalDeskNewCasePage
